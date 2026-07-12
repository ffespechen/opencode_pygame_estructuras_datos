"""Estado del menú principal: selección de estructura de datos."""

import pygame
from ds_visualizer import config


class MenuState:
    """Pantalla inicial con menú navegable de opciones."""

    def __init__(self) -> None:
        self.selected_index = 0
        self.selected_ds = None
        self._font_title = None
        self._font_subtitle = None
        self._font_option = None

    def on_enter(self, screen: pygame.Surface) -> None:
        self._font_title = pygame.font.SysFont(
            config.FONT_FAMILY, config.FONT_SIZE_TITLE, bold=True
        )
        self._font_subtitle = pygame.font.SysFont(
            config.FONT_FAMILY, config.FONT_SIZE_NORMAL
        )
        self._font_option = pygame.font.SysFont(
            config.FONT_FAMILY, config.FONT_SIZE_MENU
        )

    def on_resize(self, screen: pygame.Surface, width: int, height: int) -> None:
        pass

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(config.DS_OPTIONS)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(config.DS_OPTIONS)
                elif event.key == pygame.K_RETURN:
                    self.selected_ds = config.DS_OPTIONS[self.selected_index][1]

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface, width: int, height: int) -> None:
        self._draw_background(screen, width, height)
        self._draw_title(screen, width, height)
        self._draw_options(screen, width, height)

    def _draw_background(self, screen: pygame.Surface, width: int, height: int) -> None:
        screen.fill(config.BG_COLOR)

    def _draw_title(self, screen: pygame.Surface, width: int, height: int) -> None:
        title_surf = self._font_title.render(
            "VISUALIZADOR DE ESTRUCTURAS DE DATOS",
            True,
            config.MENU_TITLE_COLOR,
        )
        title_rect = title_surf.get_rect(center=(width // 2, height // 5))
        screen.blit(title_surf, title_rect)

        subtitle_surf = self._font_subtitle.render(
            "Seleccione una estructura:",
            True,
            config.SUBTEXT_COLOR,
        )
        subtitle_rect = subtitle_surf.get_rect(center=(width // 2, height // 5 + 50))
        screen.blit(subtitle_surf, subtitle_rect)

    def _draw_options(self, screen: pygame.Surface, width: int, height: int) -> None:
        option_width = min(500, width - 120)
        option_height = 52
        n = len(config.DS_OPTIONS)
        start_y = height // 3

        for i, (label, key) in enumerate(config.DS_OPTIONS):
            is_quit = key == "__quit__"
            rect = pygame.Rect(0, 0, option_width, option_height)
            rect.centerx = width // 2
            rect.y = start_y + i * (option_height + 10)

            if is_quit:
                sep_y = rect.y - 6
                pygame.draw.line(
                    screen, config.DIVIDER_COLOR,
                    (rect.x, sep_y), (rect.x + option_width, sep_y),
                    width=1,
                )

            if i == self.selected_index:
                pygame.draw.rect(screen, config.MENU_SELECTED_BG, rect, border_radius=8)
                pygame.draw.rect(screen, config.ACCENT_COLOR, rect, width=2, border_radius=8)
                color = config.ACCENT_COLOR
            elif is_quit:
                pygame.draw.rect(screen, config.MENU_UNSELECTED_BG, rect, border_radius=8)
                color = config.SUBTEXT_COLOR
            else:
                pygame.draw.rect(screen, config.MENU_UNSELECTED_BG, rect, border_radius=8)
                color = config.TEXT_COLOR

            text_surf = self._font_option.render(label, True, color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)
