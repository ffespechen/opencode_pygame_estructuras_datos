"""Animación visual para Stack implementada con lista enlazada."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation


class StackLinkedListAnimation(BaseAnimation):
    """Pila LIFO donde el TOP es el HEAD de una lista enlazada."""

    def __init__(self) -> None:
        super().__init__()
        self.base_values = [55, 23, 78, 41]
        self.actions = [
            ("Push: insertar en HEAD (99)", 5.0),
            ("Peek: consultar TOP / HEAD", 5.0),
            ("Pop: eliminar HEAD", 5.0),
            ("Push: insertar en HEAD (33)", 5.0),
        ]

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.action_index == 0:
            self._draw_push(surface, rect, 99)
        elif self.action_index == 1:
            self._draw_nodes(surface, rect, self.base_values, highlight_idx=0)
        elif self.action_index == 2:
            self._draw_pop(surface, rect)
        elif self.action_index == 3:
            self._draw_push(surface, rect, 33)

    def _draw_nodes(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        values: list[int],
        highlight_idx: int = -1,
        fade_idx: int = -1,
        fade_alpha: int = 255,
    ) -> None:
        n = len(values)
        if n == 0:
            return

        node_w, node_h = 70, 44
        gap = 18
        total_width = n * node_w + (n - 1) * gap
        start_x = rect.x + (rect.width - total_width) // 2
        base_y = rect.y + rect.height // 2 - node_h // 2

        for i, val in enumerate(values):
            nx = start_x + i * (node_w + gap)
            node_rect = pygame.Rect(nx, base_y, node_w, node_h)

            if i == highlight_idx:
                fg = config.HIGHLIGHT_COLOR
                border = fg
            else:
                fg = config.TEXT_COLOR
                border = config.DIVIDER_COLOR

            alpha = fade_alpha if i == fade_idx else 255
            temp = pygame.Surface((node_w, node_h), pygame.SRCALPHA)
            temp.fill((*config.CODE_BG, alpha))
            pygame.draw.rect(
                temp, (*border, alpha), temp.get_rect(), width=2, border_radius=5
            )
            val_surf = self._font.render(str(val), True, (*fg, alpha))
            val_rect = val_surf.get_rect(center=temp.get_rect().center)
            temp.blit(val_surf, val_rect)
            surface.blit(temp, node_rect)

            if i < n - 1:
                arrow_start = (nx + node_w + 2, base_y + node_h // 2)
                arrow_end = (nx + node_w + gap - 2, base_y + node_h // 2)
                arrow_color = (
                    config.ACCENT_COLOR if i == highlight_idx else config.DIVIDER_COLOR
                )
                pygame.draw.line(surface, arrow_color, arrow_start, arrow_end, width=2)
                tip_l = (arrow_end[0] - 6, arrow_end[1] - 4)
                tip_r = (arrow_end[0] - 6, arrow_end[1] + 4)
                pygame.draw.polygon(surface, arrow_color, [arrow_end, tip_l, tip_r])

        top_surf = self._font.render("TOP = HEAD", True, config.ACCENT_COLOR)
        top_rect = top_surf.get_rect(midtop=(start_x + node_w // 2, base_y - 22))
        surface.blit(top_surf, top_rect)

        hint = self._font.render(
            "Stack vía lista enlazada: push/pop solo en HEAD (O(1))",
            True,
            config.SUBTEXT_COLOR,
        )
        hint_rect = hint.get_rect(midbottom=(rect.centerx, rect.bottom - 8))
        surface.blit(hint, hint_rect)

    def _draw_push(
        self, surface: pygame.Surface, rect: pygame.Rect, value: int
    ) -> None:
        p = self.progress()
        if p < 0.4:
            self._draw_nodes(surface, rect, self.base_values, highlight_idx=0)
        else:
            display = [value] + list(self.base_values)
            self._draw_nodes(surface, rect, display, highlight_idx=0)

    def _draw_pop(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.35:
            self._draw_nodes(surface, rect, self.base_values, highlight_idx=0)
        elif p < 0.65:
            alpha = int(255 * (1.0 - (p - 0.35) / 0.3))
            self._draw_nodes(
                surface,
                rect,
                self.base_values,
                highlight_idx=0,
                fade_idx=0,
                fade_alpha=max(alpha, 20),
            )
        else:
            self._draw_nodes(
                surface, rect, self.base_values[1:], highlight_idx=0
            )
