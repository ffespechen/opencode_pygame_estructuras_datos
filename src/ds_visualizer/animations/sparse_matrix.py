"""Animación visual para Sparse Matrix (matriz dispersa)."""

import copy
import random

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import (
    AnimStep,
    BaseAnimation,
    Challenge,
    Operation,
)


class SparseMatrixAnimation(BaseAnimation):
    """Matriz con mayoría de ceros: insertar, buscar y recorrer no-ceros."""

    def __init__(self) -> None:
        super().__init__()
        self._initial_entries: list[tuple[int, int, int]] = [
            (0, 1, 5),
            (1, 3, 8),
            (2, 0, 3),
            (3, 2, 7),
        ]
        self.entries = copy.deepcopy(self._initial_entries)
        self.rows = 4
        self.cols = 4
        self._highlight_cell: tuple[int, int] | None = None
        self.actions = [
            ("Vista: matriz densa vs entradas no-cero", 5.0),
            ("Insertar valor en (1,1) = 9", 5.0),
            ("Buscar valor en (2,0)", 5.0),
            ("Recorrer solo no-ceros (COO)", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Insert", "insert",
                prompt="Fila col valor:", example="1 1 9",
                complexity="O(k)",
            ),
            Operation(
                pygame.K_2, "Search", "search",
                prompt="Fila col:", example="2 0",
                complexity="O(k)", mutates=False, uses_selection=True,
            ),
            Operation(
                pygame.K_3, "Traverse", "traverse",
                complexity="O(k)", mutates=False,
            ),
        ])
        self.set_challenges([
            Challenge(
                "sp_11", "Celda (1,1)=9",
                "Insertá 9 en (1,1).", "Insert → 1 1 9",
                lambda a: any(
                    r == 1 and c == 1 and v == 9 for r, c, v in a.entries
                ),
            ),
            Challenge(
                "sp_5", "Al menos 5 no-ceros",
                "Insertá hasta 5 entradas.", "Insert en celdas vacías",
                lambda a: len(a.entries) >= 5,
            ),
        ])

    def reset(self) -> None:
        super().reset()
        self.entries = copy.deepcopy(self._initial_entries)
        self._highlight_cell = None

    def _occupied(self) -> set[tuple[int, int]]:
        return {(r, c) for r, c, _ in self.entries}

    def _random_empty_cell(self) -> tuple[int, int] | None:
        occupied = self._occupied()
        empty = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in occupied
        ]
        return random.choice(empty) if empty else None

    def build_steps(
        self, op_id: str, user_input: str | None = None
    ) -> list[AnimStep]:
        if op_id != "traverse" or not self.entries:
            return []
        return [
            AnimStep(
                f"COO [{i + 1}/{len(self.entries)}]: ({r},{c},{v})",
                note=f"({r},{c})",
            )
            for i, (r, c, v) in enumerate(self.entries)
        ]

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "insert":
            parsed = self.parse_int_triple(user_input or "")
            if parsed is None:
                return "Formato: fila col valor (ej: 1 1 9)"
            r, c, val = parsed
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return f"Coordenadas fuera de rango (0..{self.rows - 1}, 0..{self.cols - 1})"
            for i, (er, ec, _) in enumerate(self.entries):
                if er == r and ec == c:
                    self.entries[i] = (r, c, val)
                    self._highlight_cell = (r, c)
                    return f"Insert ({r},{c}) = {val} (actualizado)"
            self.entries.append((r, c, val))
            self._highlight_cell = (r, c)
            return f"Insert ({r},{c}) = {val}"
        if op_id == "search":
            parsed = self.parse_int_pair(user_input or "")
            if parsed is None:
                return "Formato: fila col (ej: 2 0)"
            r, c = parsed
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return f"Coordenadas fuera de rango (0..{self.rows - 1}, 0..{self.cols - 1})"
            self._highlight_cell = (r, c)
            for er, ec, v in self.entries:
                if er == r and ec == c:
                    return f"Search ({r},{c}) → {v}"
            return f"Search ({r},{c}) → 0"
        if op_id == "traverse":
            self._highlight_cell = None
            return "Recorrer entradas COO"
        return ""

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            highlight = self._highlight_cell
            if self.step_mode and self.steps:
                note = self.steps[self.step_index].note
                if note.startswith("(") and "," in note:
                    try:
                        parts = note.strip("()").split(",")
                        highlight = (int(parts[0]), int(parts[1]))
                    except ValueError:
                        pass
            elif self.live_op == "traverse":
                n = len(self.entries)
                if n > 0:
                    idx = min(int(self.live_progress() * n), n - 1)
                    r, c, _ = self.entries[idx]
                    highlight = (r, c)
            self._draw_grid(
                surface, rect, self.entries, highlight=highlight, register=True,
            )
            return

        if self.action_index == 0:
            self._draw_overview(surface, rect)
        elif self.action_index == 1:
            self._draw_insert(surface, rect)
        elif self.action_index == 2:
            self._draw_search(surface, rect)
        elif self.action_index == 3:
            self._draw_traverse(surface, rect)

    def _hint(self, surface: pygame.Surface, rect: pygame.Rect, text: str) -> None:
        lbl = self._font.render(text, True, config.SUBTEXT_COLOR)
        surface.blit(lbl, lbl.get_rect(midbottom=(rect.centerx, rect.bottom - 8)))

    def _entry_map(
        self, entries: list[tuple[int, int, int]]
    ) -> dict[tuple[int, int], int]:
        return {(r, c): v for r, c, v in entries}

    def _draw_grid(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        entries: list[tuple[int, int, int]],
        highlight: tuple[int, int] | None = None,
        dim_zeros: bool = True,
        register: bool = False,
    ) -> None:
        cell = min(48, (rect.width - 200) // self.cols, (rect.height - 80) // self.rows)
        cell = max(cell, 28)
        grid_w = self.cols * cell
        grid_h = self.rows * cell
        start_x = rect.x + (rect.width - grid_w) // 2 - 40
        start_y = rect.y + (rect.height - grid_h) // 2 - 10
        data = self._entry_map(entries)

        for r in range(self.rows):
            for c in range(self.cols):
                x = start_x + c * cell
                y = start_y + r * cell
                box = pygame.Rect(x, y, cell - 2, cell - 2)
                val = data.get((r, c), 0)
                is_hl = highlight == (r, c)
                is_nz = val != 0

                if is_hl:
                    fg = config.HIGHLIGHT_COLOR
                    border = fg
                elif is_nz:
                    fg = config.ACCENT_COLOR
                    border = config.ACCENT_COLOR
                else:
                    fg = config.SUBTEXT_COLOR if dim_zeros else config.TEXT_COLOR
                    border = config.DIVIDER_COLOR

                pygame.draw.rect(surface, config.CODE_BG, box, border_radius=3)
                pygame.draw.rect(surface, border, box, width=2, border_radius=3)
                vs = self._font.render(str(val), True, fg)
                surface.blit(vs, vs.get_rect(center=box.center))
                if register:
                    self.register_hit(
                        f"cell:{r},{c}", box, label=f"({r},{c})",
                        row=r, col=c, value=val,
                    )

        list_x = start_x + grid_w + 24
        list_y = start_y
        header = self._font.render("COO (i,j,v)", True, config.ACCENT_COLOR)
        surface.blit(header, (list_x, list_y - 22))
        for i, (r, c, v) in enumerate(entries):
            line = self._font.render(f"({r},{c},{v})", True, config.TEXT_COLOR)
            surface.blit(line, (list_x, list_y + i * 20))

    def _draw_overview(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        self._draw_grid(surface, rect, self.entries, dim_zeros=True)
        nz = len(self.entries)
        total = self.rows * self.cols
        if p < 0.5:
            self._hint(
                surface, rect,
                f"Matriz {self.rows}×{self.cols}: {total} celdas, solo {nz} no-ceros"
            )
        else:
            self._hint(
                surface, rect,
                "Formato COO guarda únicamente (fila, col, valor) ≠ 0"
            )

    def _draw_insert(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.4:
            self._draw_grid(surface, rect, self.entries, highlight=(1, 1))
            self._hint(surface, rect, "Insertar en (1,1)…")
        else:
            entries = list(self.entries) + [(1, 1, 9)]
            self._draw_grid(surface, rect, entries, highlight=(1, 1))
            self._hint(surface, rect, "Nueva entrada COO: (1,1,9)")

    def _draw_search(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        target = (2, 0)
        if p < 0.35:
            self._draw_grid(surface, rect, self.entries)
            self._hint(surface, rect, "Buscar (2,0) en lista COO…")
        elif p < 0.7:
            self._draw_grid(surface, rect, self.entries, highlight=target)
            self._hint(surface, rect, "Comparando coordenadas…")
        else:
            self._draw_grid(surface, rect, self.entries, highlight=target)
            self._hint(surface, rect, "Encontrado: valor = 3")

    def _draw_traverse(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.entries)
        idx = min(int(p * n), n - 1)
        r, c, v = self.entries[idx]
        self._draw_grid(surface, rect, self.entries, highlight=(r, c))
        self._hint(
            surface, rect,
            f"Recorrido COO [{idx + 1}/{n}]: ({r},{c}) → {v}"
        )
