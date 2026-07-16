"""Animación visual para Array / Lista."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation, Operation


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
            Operation(pygame.K_1, "Traverse", "traverse"),
            Operation(
                pygame.K_2, "Search", "search",
                prompt="Valor a buscar:",
                example="63",
            ),
            Operation(
                pygame.K_3, "Insert", "insert",
                prompt="Valor a insertar:",
                example="99",
            ),
            Operation(
                pygame.K_4, "Delete", "delete",
                prompt="Índice a eliminar:",
                example="2",
            ),
        ])

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
        second = -1

        if self.live_op == "traverse":
            n = len(self.values)
            if n > 0:
                highlight = min(int(self.live_progress() * n), n - 1)
        elif self.live_op == "search":
            n = len(self.values)
            if n > 0 and self._search_target is not None:
                target_val = self._search_target
                try:
                    target_idx = self.values.index(target_val)
                    total = target_idx + 1 + 0.5
                    current = self.live_progress() * total
                    highlight = min(int(current), target_idx)
                    if self.live_progress() > 0.85:
                        second = target_idx
                except ValueError:
                    current = int(self.live_progress() * n)
                    highlight = min(current, n - 1)

        self._draw_boxes(surface, rect, self.values, highlight_idx=highlight,
                         second_highlight=second)

    def _draw_boxes(
        self, surface: pygame.Surface, rect: pygame.Rect,
        values: list[int], highlight_idx: int = -1,
        second_highlight: int = -1,
    ) -> None:
        n = len(values)
        box_size = min(70, (rect.width - 40) // max(n, 1) - 8)
        total_width = n * (box_size + 8) - 8
        start_x = rect.x + (rect.width - total_width) // 2
        base_y = rect.y + rect.height // 2 - box_size // 2 + 15

        for i, val in enumerate(values):
            bx = start_x + i * (box_size + 8)
            box_rect = pygame.Rect(bx, base_y, box_size, box_size)

            if i == highlight_idx:
                color = config.HIGHLIGHT_COLOR
                pygame.draw.rect(surface, color, box_rect, border_radius=6)
                pygame.draw.rect(surface, color, box_rect, width=2, border_radius=6)
            elif i == second_highlight:
                color = config.ACCENT_COLOR
                pygame.draw.rect(surface, config.CODE_BG, box_rect, border_radius=6)
                pygame.draw.rect(surface, color, box_rect, width=2, border_radius=6)
            else:
                color = config.TEXT_COLOR
                pygame.draw.rect(surface, config.CODE_BG, box_rect, border_radius=6)
                pygame.draw.rect(surface, config.DIVIDER_COLOR, box_rect, width=1, border_radius=6)

            val_surf = self._font.render(str(val), True, color if i == highlight_idx else config.TEXT_COLOR)
            val_rect = val_surf.get_rect(center=box_rect.center)
            surface.blit(val_surf, val_rect)

            idx_surf = self._font.render(str(i), True, config.SUBTEXT_COLOR)
            idx_rect = idx_surf.get_rect(center=(box_rect.centerx, box_rect.top - 14))
            surface.blit(idx_surf, idx_rect)

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
                    display_values[idx] = display_values[idx - 1] if idx > ti else self.values[ti]
            self._draw_boxes(surface, rect, display_values, highlight_idx=ti)
        else:
            reveal_progress = (p - 0.5) / 0.5
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
