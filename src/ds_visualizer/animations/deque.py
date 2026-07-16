"""Animación visual para Deque (Cola de Doble Extremo)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation, Operation


class DequeAnimation(BaseAnimation):
    """Muestra una deque horizontal con push/pop en ambos extremos."""

    def __init__(self) -> None:
        super().__init__()
        self.base_values = [20, 45, 67, 30]
        self._initial = list(self.base_values)
        self.values = list(self._initial)
        self.actions = [
            ("Push front: insertar al frente (99)", 5.0),
            ("Push rear: insertar al final (11)", 5.0),
            ("Pop front: eliminar del frente", 5.0),
            ("Pop rear: eliminar del final", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Push front", "push_front",
                prompt="Valor:",
                example="99",
            ),
            Operation(
                pygame.K_2, "Push rear", "push_rear",
                prompt="Valor:",
                example="99",
            ),
            Operation(pygame.K_3, "Pop front", "pop_front"),
            Operation(pygame.K_4, "Pop rear", "pop_rear"),
        ])

    def reset(self) -> None:
        super().reset()
        self.values = list(self._initial)

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "push_front":
            v = self.parse_int(user_input or "")
            if v is None:
                return "Ingresá un número entero"
            self.values.insert(0, v)
            self.highlight_idx = 0
            return f"Push front {v}"
        if op_id == "push_rear":
            v = self.parse_int(user_input or "")
            if v is None:
                return "Ingresá un número entero"
            self.values.append(v)
            self.highlight_idx = len(self.values) - 1
            return f"Push rear {v}"
        if op_id == "pop_front":
            if not self.values:
                self.highlight_idx = -1
                return "Deque vacía"
            removed = self.values.pop(0)
            self.highlight_idx = 0 if self.values else -1
            return f"Pop front {removed}"
        if op_id == "pop_rear":
            if not self.values:
                self.highlight_idx = -1
                return "Deque vacía"
            removed = self.values.pop()
            self.highlight_idx = len(self.values) - 1 if self.values else -1
            return f"Pop rear {removed}"
        return ""

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            self._draw_interactive(surface, rect)
            return

        if self.action_index == 0:
            self._draw_push_front(surface, rect)
        elif self.action_index == 1:
            self._draw_push_rear(surface, rect)
        elif self.action_index == 2:
            self._draw_pop_front(surface, rect)
        elif self.action_index == 3:
            self._draw_pop_rear(surface, rect)

    def _draw_interactive(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if not self.values:
            self.draw_empty(surface, rect, "(deque vacía)")
            return
        highlight_front = self.live_op in ("push_front", "pop_front")
        highlight_rear = self.live_op in ("push_rear", "pop_rear")
        if not self.live_op:
            if self.highlight_idx == 0:
                highlight_front = True
            elif self.highlight_idx == len(self.values) - 1:
                highlight_rear = True
        self._draw_boxes(
            surface, rect, self.values,
            highlight_front=highlight_front,
            highlight_rear=highlight_rear,
        )

    def _draw_boxes(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        values: list[int],
        highlight_front: bool = False,
        highlight_rear: bool = False,
        fade_idx: int = -1,
        fade_alpha: int = 255,
    ) -> None:
        box_w, box_h = 64, 44
        gap = 10
        n = len(values)
        if n == 0:
            return

        total_width = n * box_w + (n - 1) * gap
        start_x = rect.x + (rect.width - total_width) // 2
        base_y = rect.y + rect.height // 2 - box_h // 2

        for i, val in enumerate(values):
            bx = start_x + i * (box_w + gap)
            box_rect = pygame.Rect(bx, base_y, box_w, box_h)

            is_front = i == 0
            is_rear = i == n - 1
            if is_front and highlight_front:
                fg = config.HIGHLIGHT_COLOR
                border = fg
            elif is_rear and highlight_rear:
                fg = config.ACCENT_COLOR
                border = fg
            else:
                fg = config.TEXT_COLOR
                border = config.DIVIDER_COLOR

            alpha = fade_alpha if i == fade_idx else 255
            temp = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            temp.fill((*config.CODE_BG, alpha))
            pygame.draw.rect(
                temp, (*border, alpha), temp.get_rect(), width=2, border_radius=4
            )
            val_surf = self._font.render(str(val), True, (*fg, alpha))
            val_rect = val_surf.get_rect(center=temp.get_rect().center)
            temp.blit(val_surf, val_rect)
            surface.blit(temp, box_rect)

        front_surf = self._font.render("FRONT", True, config.HIGHLIGHT_COLOR)
        frect = front_surf.get_rect(midtop=(start_x + box_w // 2, base_y - 22))
        surface.blit(front_surf, frect)

        rear_surf = self._font.render("REAR", True, config.ACCENT_COLOR)
        rrect = rear_surf.get_rect(
            midtop=(start_x + (n - 1) * (box_w + gap) + box_w // 2, base_y - 22)
        )
        surface.blit(rear_surf, rrect)

        hint = self._font.render(
            "Deque: operaciones O(1) en ambos extremos", True, config.SUBTEXT_COLOR
        )
        hint_rect = hint.get_rect(midbottom=(rect.centerx, rect.bottom - 8))
        surface.blit(hint, hint_rect)

    def _draw_push_front(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.4:
            self._draw_boxes(surface, rect, self.base_values, highlight_front=True)
        else:
            display = [99] + list(self.base_values)
            self._draw_boxes(surface, rect, display, highlight_front=True)

    def _draw_push_rear(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.4:
            self._draw_boxes(surface, rect, self.base_values, highlight_rear=True)
        else:
            display = list(self.base_values) + [11]
            self._draw_boxes(surface, rect, display, highlight_rear=True)

    def _draw_pop_front(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.35:
            self._draw_boxes(surface, rect, self.base_values, highlight_front=True)
        elif p < 0.65:
            alpha = int(255 * (1.0 - (p - 0.35) / 0.3))
            self._draw_boxes(
                surface,
                rect,
                self.base_values,
                highlight_front=True,
                fade_idx=0,
                fade_alpha=max(alpha, 20),
            )
        else:
            self._draw_boxes(surface, rect, self.base_values[1:], highlight_front=True)

    def _draw_pop_rear(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.base_values)
        if p < 0.35:
            self._draw_boxes(surface, rect, self.base_values, highlight_rear=True)
        elif p < 0.65:
            alpha = int(255 * (1.0 - (p - 0.35) / 0.3))
            self._draw_boxes(
                surface,
                rect,
                self.base_values,
                highlight_rear=True,
                fade_idx=n - 1,
                fade_alpha=max(alpha, 20),
            )
        else:
            self._draw_boxes(
                surface, rect, self.base_values[:-1], highlight_rear=True
            )
