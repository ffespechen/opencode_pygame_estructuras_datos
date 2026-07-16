"""Animación visual para Array / Lista."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import (
    AnimStep,
    BaseAnimation,
    Challenge,
    HitTarget,
    Operation,
)


class ArrayAnimation(BaseAnimation):
    """Muestra cajas con valores e índice, animando operaciones típicas."""

    def __init__(self) -> None:
        super().__init__()
        self._initial = [42, 17, 88, 35, 63, 29, 51, 74]
        self.values = list(self._initial)
        self.insert_value = 99
        self.insert_index = 2
        self.anim_values = list(self.values)
        self.actions = [
            ("Recorriendo por índice", 5.0),
            ("Búsqueda lineal (valor=63)", 5.0),
            ("Inserción en posición 2 (valor=99)", 5.0),
            ("Eliminación en posición 3", 5.0),
        ]
        self._search_target: int | None = None
        self.set_operations([
            Operation(
                pygame.K_1, "Traverse", "traverse",
                complexity="O(n)", mutates=False,
            ),
            Operation(
                pygame.K_2, "Search", "search",
                prompt="Valor a buscar:", example="63",
                complexity="O(n)", mutates=False, uses_selection=True,
            ),
            Operation(
                pygame.K_3, "Insert", "insert",
                prompt="Valor a insertar:", example="99",
                complexity="O(1) amortizado",
            ),
            Operation(
                pygame.K_4, "Delete", "delete",
                prompt="Índice a eliminar:", example="2",
                complexity="O(n)", uses_selection=True,
            ),
        ])
        self.set_challenges([
            Challenge(
                "array_len5",
                "Dejá 5 elementos",
                "Usá Insert/Delete hasta que el array tenga exactamente 5 valores.",
                "Insert agrega al final; Delete pide un índice (o click + Delete).",
                lambda a: len(a.values) == 5,
            ),
            Challenge(
                "array_has_7",
                "Incluí un 7",
                "Insertá el valor 7 en el array.",
                "Insert → escribí 7 → Enter.",
                lambda a: 7 in a.values,
            ),
        ])

    def capture_state(self) -> dict:
        state = super().capture_state()
        state["values"] = list(self.values)
        state["_search_target"] = self._search_target
        return state

    def restore_state(self, state: dict) -> None:
        super().restore_state(state)
        self.values = list(state.get("values", self._initial))
        self._search_target = state.get("_search_target")

    def reset(self) -> None:
        super().reset()
        self.values = list(self._initial)
        self._search_target = None

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "traverse":
            self.highlight_idx = 0
            self._search_target = None
            return "Recorriendo por índice"
        if op_id == "search":
            v = self.parse_int(user_input or "")
            if v is None:
                return "Ingresá un número entero"
            if not self.values:
                self._search_target = v
                self.highlight_idx = -1
                return "Array vacío"
            self._search_target = v
            try:
                idx = self.values.index(v)
                self.highlight_idx = idx
                return f"Búsqueda: valor={v} encontrado en índice {idx}"
            except ValueError:
                self.highlight_idx = -1
                return f"Búsqueda: valor={v} no encontrado"
        if op_id == "insert":
            v = self.parse_int(user_input or "")
            if v is None:
                return "Ingresá un número entero"
            self.values.append(v)
            self.highlight_idx = len(self.values) - 1
            self._search_target = None
            return f"Insert {v} al final"
        if op_id == "delete":
            idx = self.parse_int(user_input or "")
            if idx is None:
                return "Ingresá un índice entero"
            if not self.values:
                self.highlight_idx = -1
                return "Array vacío"
            if idx < 0 or idx >= len(self.values):
                return f"Índice fuera de rango (0..{len(self.values) - 1})"
            removed = self.values.pop(idx)
            self.highlight_idx = -1
            self._search_target = None
            return f"Delete {removed} en índice {idx}"
        return ""

    def build_steps(
        self, op_id: str, user_input: str | None = None
    ) -> list[AnimStep]:
        if op_id == "traverse" and self.values:
            return [
                AnimStep(
                    f"Índice {i} → {self.values[i]}",
                    highlight_idx=i,
                    highlight_set=frozenset(range(i + 1)),
                    current_idx=i,
                    note=f"{i + 1}/{len(self.values)} · Space=siguiente",
                )
                for i in range(len(self.values))
            ]
        if op_id == "search" and self.values and self._search_target is not None:
            target = self._search_target
            steps: list[AnimStep] = []
            for i, val in enumerate(self.values):
                visited = frozenset(range(i + 1))
                if val == target:
                    steps.append(AnimStep(
                        f"Comparar [{i}]={val} == {target} → encontrado",
                        highlight_idx=i,
                        highlight_set=visited,
                        current_idx=i,
                        note="match · Space=siguiente",
                    ))
                    break
                steps.append(AnimStep(
                    f"Comparar [{i}]={val} ≠ {target}",
                    highlight_idx=i,
                    highlight_set=visited,
                    current_idx=i,
                    note=f"{i + 1}/{len(self.values)} · Space=siguiente",
                ))
            else:
                steps.append(AnimStep(
                    f"{target} no está en el array",
                    highlight_set=frozenset(range(len(self.values))),
                    note="miss",
                ))
            return steps
        return []

    def on_drop(self, source_id: str, dest: HitTarget | None) -> str:
        if dest is None or not source_id.startswith("idx:"):
            return ""
        if not dest.target_id.startswith("idx:"):
            return ""
        try:
            src = int(source_id.split(":")[1])
            dst = int(dest.target_id.split(":")[1])
        except (IndexError, ValueError):
            return ""
        if src == dst or src >= len(self.values) or dst >= len(self.values):
            return ""
        self.values[src], self.values[dst] = self.values[dst], self.values[src]
        self.highlight_idx = dst
        return f"Swap [{src}] ↔ [{dst}]  [O(1)]"

    def update(self, dt: float) -> None:
        super().update(dt)

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            self._draw_interactive(surface, rect)
            return

        if self.action_index == 0:
            self._draw_traverse(surface, rect)
        elif self.action_index == 1:
            self._draw_search(surface, rect)
        elif self.action_index == 2:
            self._draw_insert(surface, rect)
        elif self.action_index == 3:
            self._draw_delete(surface, rect)

    def _draw_interactive(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        highlight = self.highlight_idx
        visited: set[int] = set()
        second = -1

        if self.step_mode and self.steps:
            highlight = self.focus_idx if self.focus_idx >= 0 else self.highlight_idx
            visited = set(self.highlight_set)
        elif self.live_op == "traverse":
            n = len(self.values)
            if n > 0:
                highlight = min(int(self.live_progress() * n), n - 1)
                visited = set(range(highlight + 1))
        elif self.live_op == "search":
            n = len(self.values)
            if n > 0 and self._search_target is not None:
                target_val = self._search_target
                try:
                    target_idx = self.values.index(target_val)
                    total = target_idx + 1 + 0.5
                    current = self.live_progress() * total
                    highlight = min(int(current), target_idx)
                    visited = set(range(highlight + 1))
                    if self.live_progress() > 0.85:
                        second = target_idx
                except ValueError:
                    current = int(self.live_progress() * n)
                    highlight = min(current, n - 1)
                    visited = set(range(highlight + 1))

        self._draw_boxes(
            surface, rect, self.values,
            highlight_idx=highlight, second_highlight=second,
            visited=visited, register=True,
        )

    def _draw_boxes(
        self, surface: pygame.Surface, rect: pygame.Rect,
        values: list[int], highlight_idx: int = -1,
        second_highlight: int = -1, register: bool = False,
        visited: set[int] | None = None,
    ) -> None:
        n = len(values)
        box_size = min(70, (rect.width - 40) // max(n, 1) - 8)
        total_width = n * (box_size + 8) - 8
        start_x = rect.x + (rect.width - total_width) // 2
        base_y = rect.y + rect.height // 2 - box_size // 2 + 15
        visited = visited or set()

        for i, val in enumerate(values):
            bx = start_x + i * (box_size + 8)
            box_rect = pygame.Rect(bx, base_y, box_size, box_size)

            if i == highlight_idx:
                role = "current"
            elif i == second_highlight:
                role = "frontier"
            elif i in visited:
                role = "visited"
            else:
                role = "plain"
            fg = self.color_for_role(role)
            border = fg if role != "plain" else config.DIVIDER_COLOR
            width = 3 if role == "current" else (2 if role != "plain" else 1)

            pygame.draw.rect(surface, config.CODE_BG, box_rect, border_radius=6)
            if role == "current":
                pygame.draw.rect(surface, fg, box_rect, border_radius=6)
                pygame.draw.rect(surface, fg, box_rect, width=2, border_radius=6)
                text_color = config.CODE_BG
            else:
                pygame.draw.rect(
                    surface, border, box_rect, width=width, border_radius=6,
                )
                text_color = fg if role != "plain" else config.TEXT_COLOR

            val_surf = self._font.render(str(val), True, text_color)
            val_rect = val_surf.get_rect(center=box_rect.center)
            surface.blit(val_surf, val_rect)

            idx_surf = self._font.render(str(i), True, config.SUBTEXT_COLOR)
            idx_rect = idx_surf.get_rect(center=(box_rect.centerx, box_rect.top - 14))
            surface.blit(idx_surf, idx_rect)

            if register:
                self.register_hit(
                    f"idx:{i}", box_rect, label=f"[{i}]={val}", index=i, value=val,
                )

    def _draw_traverse(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.values)
        highlight = int(p * n)
        self._draw_boxes(surface, rect, self.values, highlight_idx=highlight)

    def _draw_search(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.values)
        target_val = 63
        target_idx = self.values.index(target_val)
        total = target_idx + 1 + 0.5
        current = p * total
        highlight = min(int(current), target_idx)
        found = current > target_idx
        self._draw_boxes(
            surface, rect, self.values,
            highlight_idx=highlight,
            second_highlight=target_idx if found else -1,
        )

    def _draw_insert(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.values)
        ti = self.insert_index

        if p < 0.5:
            shift_progress = p / 0.5
            display_values = list(self.values)
            shift_count = int(shift_progress * (n - ti))
            for j in range(shift_count):
                idx = n - 1 - j
                if idx >= ti:
                    display_values[idx] = (
                        display_values[idx - 1] if idx > ti else self.values[ti]
                    )
            self._draw_boxes(surface, rect, display_values, highlight_idx=ti)
        else:
            display_values = list(self.values)
            for j in range(n - 1, ti, -1):
                display_values[j] = display_values[j - 1]
            display_values[ti] = self.insert_value
            self._draw_boxes(surface, rect, display_values, highlight_idx=ti)

    def _draw_delete(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.values)
        target = 3

        if p < 0.3:
            self._draw_boxes(surface, rect, self.values, highlight_idx=target)
        elif p < 0.6:
            display_values = list(self.values)
            display_values[target] = -1
            self._draw_boxes(surface, rect, display_values, highlight_idx=target)
        else:
            shift_progress = (p - 0.6) / 0.4
            display_values = list(self.values)
            shift_count = int(shift_progress * (n - target - 1))
            for j in range(shift_count):
                idx = target + j
                display_values[idx] = display_values[idx + 1] if idx + 1 < n else 0
            self._draw_boxes(surface, rect, display_values, highlight_idx=target)
