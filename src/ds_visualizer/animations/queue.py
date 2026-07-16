"""Animación visual para Queue / Cola (FIFO)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation, Operation


class QueueAnimation(BaseAnimation):
    """Muestra una cola horizontal con animaciones de enqueue, dequeue y peek."""

    def __init__(self) -> None:
        super().__init__()
        self.base_values = [12, 45, 67, 30]
        self._initial = list(self.base_values)
        self.values = list(self._initial)
        self.actions = [
            ("Enqueue: encolando elemento (88)", 5.0),
            ("Peek: consultando frente", 5.0),
            ("Dequeue: desencolando elemento", 5.0),
            ("Enqueue: encolando elemento (19)", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Enqueue", "enqueue",
                prompt="Valor a encolar:",
                example="88",
            ),
            Operation(pygame.K_2, "Peek", "peek"),
            Operation(pygame.K_3, "Dequeue", "dequeue"),
        ])

    def reset(self) -> None:
        super().reset()
        self.values = list(self._initial)

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "enqueue":
            v = self.parse_int(user_input or "")
            if v is None:
                return "Ingresá un número entero"
            self.values.append(v)
            self.highlight_idx = len(self.values) - 1
            return f"Enqueue {v}"
        if op_id == "peek":
            if not self.values:
                self.highlight_idx = -1
                return "Cola vacía"
            self.highlight_idx = 0
            return f"Peek → {self.values[0]}"
        if op_id == "dequeue":
            if not self.values:
                self.highlight_idx = -1
                return "Cola vacía"
            removed = self.values.pop(0)
            self.highlight_idx = 0 if self.values else -1
            return f"Dequeue {removed}"
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
            self._draw_enqueue(surface, rect, 88)
        elif self.action_index == 1:
            self._draw_peek(surface, rect, self.base_values)
        elif self.action_index == 2:
            self._draw_dequeue(surface, rect)
        elif self.action_index == 3:
            self._draw_enqueue(surface, rect, 19)

    def _draw_interactive(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if not self.values:
            self.draw_empty(surface, rect, "(cola vacía)")
            return
        highlight_front = self.live_op == "peek" or self.live_op == "dequeue"
        highlight_rear = self.live_op == "enqueue"
        if not self.live_op:
            if self.highlight_idx == 0:
                highlight_front = True
            elif self.highlight_idx == len(self.values) - 1:
                highlight_rear = True
        self._draw_queue_boxes(
            surface, rect, self.values,
            highlight_front=highlight_front,
            highlight_rear=highlight_rear,
        )

    def _draw_queue_boxes(
        self, surface: pygame.Surface, rect: pygame.Rect,
        values: list[int], highlight_front: bool = False,
        highlight_rear: bool = False,
        extra_item: tuple[int, float, str] | None = None,
        slide_out: int = -1,
    ) -> None:
        box_w, box_h = 64, 44
        gap = 10
        n = len(values)
        slide_offset = 0

        if slide_out >= 0:
            slide_offset = int(self.progress() * 60) if self.progress() < 1 else 60

        total_width = n * box_w + (n - 1) * gap
        start_x = rect.x + (rect.width - total_width) // 2
        base_y = rect.y + rect.height // 2 - box_h // 2

        for i, val in enumerate(values):
            bx = start_x + i * (box_w + gap)

            if i == 0 and slide_out >= 0:
                bx -= slide_offset

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

            alpha = 255
            if slide_out >= 0 and i == 0:
                alpha = max(0, int(255 * (1.0 - slide_offset / 60)))

            temp_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            bg_color = (*config.CODE_BG, alpha)
            temp_surf.fill(bg_color)
            border_color = (*border, alpha)
            pygame.draw.rect(temp_surf, border_color, temp_surf.get_rect(), width=2, border_radius=4)
            val_surf = self._font.render(str(val), True, (*fg, alpha))
            val_rect = val_surf.get_rect(center=temp_surf.get_rect().center)
            temp_surf.blit(val_surf, val_rect)
            surface.blit(temp_surf, box_rect)

        if extra_item:
            val, alpha_progress, position = extra_item
            if position == "rear":
                ex = start_x + n * (box_w + gap) + int(alpha_progress * 40)
                box_rect = pygame.Rect(ex, base_y, box_w, box_h)
            else:
                box_rect = pygame.Rect(start_x - box_w - gap, base_y, box_w, box_h)

        if n > 0:
            front_surf = self._font.render("FRENTE", True, config.HIGHLIGHT_COLOR)
            frect = front_surf.get_rect(midtop=(start_x + box_w // 2, base_y - 22))
            surface.blit(front_surf, frect)

            rear_surf = self._font.render("FINAL", True, config.ACCENT_COLOR)
            rrect = rear_surf.get_rect(
                midtop=(start_x + (n - 1) * (box_w + gap) + box_w // 2, base_y - 22)
            )
            surface.blit(rear_surf, rrect)

    def _draw_enqueue(self, surface: pygame.Surface, rect: pygame.Rect, value: int) -> None:
        p = self.progress()
        if p < 0.5:
            self._draw_queue_boxes(surface, rect, self.base_values, highlight_rear=True)
        else:
            display = list(self.base_values) + [value]
            self._draw_queue_boxes(surface, rect, display, highlight_rear=True)

    def _draw_peek(self, surface: pygame.Surface, rect: pygame.Rect, values: list[int]) -> None:
        self._draw_queue_boxes(surface, rect, values, highlight_front=True)

    def _draw_dequeue(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.2:
            self._draw_queue_boxes(surface, rect, self.base_values, highlight_front=True)
        elif p < 0.6:
            display = list(self.base_values)
            self._draw_queue_boxes(surface, rect, display, slide_out=0)
        else:
            self._draw_queue_boxes(surface, rect, self.base_values[1:])
