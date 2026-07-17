"""Toolbar clickeable de operaciones (etapa 2)."""

from __future__ import annotations

import pygame

from ds_visualizer import config
from ds_visualizer.animations.base import Operation


class OpToolbar:
    """Fila de botones sobre la barra de atajos."""

    HEIGHT = 44
    PAD_X = 10
    PAD_Y = 6
    GAP = 8

    def __init__(self) -> None:
        self._font = None
        self._buttons: list[tuple[pygame.Rect, str]] = []  # rect, op_id
        self._extra: list[tuple[pygame.Rect, str]] = []  # rect, action_id

    def _init_font(self) -> None:
        self._font = pygame.font.SysFont(
            config.FONT_FAMILY, config.SHORTCUT_FONT_SIZE, bold=True
        )

    def layout(
        self,
        width: int,
        bar_y: int,
        operations: list[Operation],
        extras: list[tuple[str, str]] | None = None,
    ) -> None:
        """Recalcula botones. ``extras`` = [(action_id, label), ...]."""
        if self._font is None:
            self._init_font()
        self._buttons = []
        self._extra = []
        x = self.PAD_X
        y = bar_y + self.PAD_Y
        h = self.HEIGHT - 2 * self.PAD_Y

        def add_btn(label: str, store: list, key: str) -> None:
            nonlocal x
            text = self._font.render(label, True, config.TEXT_COLOR)
            w = max(text.get_width() + 18, 52)
            if x + w > width - self.PAD_X:
                return
            rect = pygame.Rect(x, y, w, h)
            store.append((rect, key))
            x += w + self.GAP

        for op in operations:
            key_name = pygame.key.name(op.key).upper()
            label = f"{key_name} {op.label}"
            add_btn(label, self._buttons, op.op_id)

        for action_id, label in extras or []:
            add_btn(label, self._extra, action_id)

    def hit(self, pos: tuple[int, int]) -> tuple[str, str] | None:
        """Devuelve ('op'|'extra', id) o None."""
        for rect, op_id in self._buttons:
            if rect.collidepoint(pos):
                return ("op", op_id)
        for rect, action_id in self._extra:
            if rect.collidepoint(pos):
                return ("extra", action_id)
        return None

    def draw(self, screen: pygame.Surface, width: int, bar_y: int) -> None:
        if self._font is None:
            self._init_font()
        bar = pygame.Rect(0, bar_y, width, self.HEIGHT)
        pygame.draw.rect(screen, config.SHORTCUT_BG, bar)
        pygame.draw.line(
            screen, config.DIVIDER_COLOR, (0, bar_y), (width, bar_y), width=1
        )

        for rect, op_id in self._buttons + self._extra:
            pygame.draw.rect(screen, config.MENU_UNSELECTED_BG, rect, border_radius=5)
            pygame.draw.rect(screen, config.DIVIDER_COLOR, rect, width=1, border_radius=5)
            # label stored only as id — re-render from rect content via last layout labels
        # Redibujar con texto: necesitamos labels; relayout guarda solo id.
        # Usamos el texto ya medido en layout — re-layout callers pass ops each frame.
        # Aquí volvemos a pintar buscando en _buttons; el texto se re-renderiza abajo
        # desde un mapa construido en draw_with_labels.

    def draw_with_labels(
        self,
        screen: pygame.Surface,
        width: int,
        bar_y: int,
        operations: list[Operation],
        extras: list[tuple[str, str]] | None = None,
    ) -> None:
        self.layout(width, bar_y, operations, extras)
        if self._font is None:
            self._init_font()
        bar = pygame.Rect(0, bar_y, width, self.HEIGHT)
        pygame.draw.rect(screen, config.SHORTCUT_BG, bar)
        pygame.draw.line(
            screen, config.DIVIDER_COLOR, (0, bar_y), (width, bar_y), width=1
        )

        labels: dict[str, str] = {}
        for op in operations:
            key_name = pygame.key.name(op.key).upper()
            labels[op.op_id] = f"{key_name} {op.label}"
        for action_id, label in extras or []:
            labels[action_id] = label

        for rect, key in self._buttons + self._extra:
            pygame.draw.rect(screen, config.MENU_UNSELECTED_BG, rect, border_radius=5)
            pygame.draw.rect(screen, config.ACCENT_COLOR, rect, width=1, border_radius=5)
            text = self._font.render(
                labels.get(key, key), True, config.TEXT_COLOR
            )
            screen.blit(text, text.get_rect(center=rect.center))
