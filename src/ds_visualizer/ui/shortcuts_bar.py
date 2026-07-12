"""Barra inferior que muestra atajos de teclado y la acción actual de la animación."""

import pygame
from ds_visualizer import config


class ShortcutsBar:
    """Barra fija en la parte inferior con atajos y acción animada actual."""

    def __init__(self) -> None:
        self._font = None

    def _init_font(self) -> None:
        self._font = pygame.font.SysFont(
            config.FONT_FAMILY, config.SHORTCUT_FONT_SIZE, bold=True
        )

    def draw(
        self, screen: pygame.Surface, width: int, height: int,
        shortcuts: str, current_action: str = "",
    ) -> None:
        if self._font is None:
            self._init_font()

        bar_y = height - config.SHORTCUT_BAR_HEIGHT
        bar_rect = pygame.Rect(0, bar_y, width, config.SHORTCUT_BAR_HEIGHT)
        pygame.draw.rect(screen, config.SHORTCUT_BG, bar_rect)

        pygame.draw.line(
            screen, config.DIVIDER_COLOR,
            (0, bar_y), (width, bar_y), width=1,
        )

        shortcuts_surf = self._font.render(shortcuts, True, config.SUBTEXT_COLOR)
        shortcuts_rect = shortcuts_surf.get_rect(
            midleft=(20, bar_y + config.SHORTCUT_BAR_HEIGHT // 2)
        )
        screen.blit(shortcuts_surf, shortcuts_rect)

        if current_action:
            action_surf = self._font.render(
                current_action, True, config.HIGHLIGHT_COLOR
            )
            action_rect = action_surf.get_rect(
                midright=(width - 20, bar_y + config.SHORTCUT_BAR_HEIGHT // 2)
            )
            screen.blit(action_surf, action_rect)
