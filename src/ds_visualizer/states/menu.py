"""Estado del menú principal: selección de estructura de datos."""

import pygame
from ds_visualizer import config


class MenuState:
    """Pantalla inicial con menú navegable (scroll si hay muchas opciones)."""

    def __init__(self) -> None:
        self.selected_index = 0
        self.selected_ds = None
        self._font_title = None
        self._font_subtitle = None
        self._font_option = None
        self._scroll_offset = 0

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
                    self.selected_index = (
                        self.selected_index - 1
                    ) % len(config.DS_OPTIONS)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (
                        self.selected_index + 1
                    ) % len(config.DS_OPTIONS)
                elif event.key == pygame.K_RETURN:
                    self.selected_ds = config.DS_OPTIONS[self.selected_index][1]
            elif event.type == pygame.MOUSEWHEEL:
                self.selected_index = max(
                    0,
                    min(
                        len(config.DS_OPTIONS) - 1,
                        self.selected_index - event.y,
                    ),
                )

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface, width: int, height: int) -> None:
        self._draw_background(screen, width, height)
        self._draw_title(screen, width)
        self._draw_options(screen, width, height)

    def _draw_background(self, screen: pygame.Surface, width: int, height: int) -> None:
        screen.fill(config.BG_COLOR)

    def _draw_title(self, screen: pygame.Surface, width: int) -> None:
        title_surf = self._font_title.render(
            "VISUALIZADOR DE ESTRUCTURAS DE DATOS",
            True,
            config.MENU_TITLE_COLOR,
        )
        title_rect = title_surf.get_rect(center=(width // 2, 36))
        screen.blit(title_surf, title_rect)

        subtitle_surf = self._font_subtitle.render(
            "Seleccione una estructura (↑↓ / rueda):",
            True,
            config.SUBTEXT_COLOR,
        )
        subtitle_rect = subtitle_surf.get_rect(center=(width // 2, 70))
        screen.blit(subtitle_surf, subtitle_rect)

    def _draw_options(self, screen: pygame.Surface, width: int, height: int) -> None:
        option_width = min(520, width - 80)
        option_height = 40
        gap = 6
        step = option_height + gap
        n = len(config.DS_OPTIONS)

        list_top = 96
        list_bottom = height - 24
        visible_h = list_bottom - list_top
        visible_count = max(1, visible_h // step)

        # Mantener la opción seleccionada visible
        if self.selected_index < self._scroll_offset:
            self._scroll_offset = self.selected_index
        elif self.selected_index >= self._scroll_offset + visible_count:
            self._scroll_offset = self.selected_index - visible_count + 1
        max_offset = max(0, n - visible_count)
        self._scroll_offset = max(0, min(self._scroll_offset, max_offset))

        clip = pygame.Rect(0, list_top, width, visible_h)
        screen.set_clip(clip)

        for i, (label, key) in enumerate(config.DS_OPTIONS):
            if i < self._scroll_offset or i >= self._scroll_offset + visible_count + 1:
                continue

            is_quit = key == "__quit__"
            rect = pygame.Rect(0, 0, option_width, option_height)
            rect.centerx = width // 2
            rect.y = list_top + (i - self._scroll_offset) * step

            if is_quit:
                sep_y = rect.y - 4
                pygame.draw.line(
                    screen,
                    config.DIVIDER_COLOR,
                    (rect.x, sep_y),
                    (rect.x + option_width, sep_y),
                    width=1,
                )

            if i == self.selected_index:
                pygame.draw.rect(
                    screen, config.MENU_SELECTED_BG, rect, border_radius=8
                )
                pygame.draw.rect(
                    screen, config.ACCENT_COLOR, rect, width=2, border_radius=8
                )
                color = config.ACCENT_COLOR
            elif is_quit:
                pygame.draw.rect(
                    screen, config.MENU_UNSELECTED_BG, rect, border_radius=8
                )
                color = config.SUBTEXT_COLOR
            else:
                pygame.draw.rect(
                    screen, config.MENU_UNSELECTED_BG, rect, border_radius=8
                )
                color = config.TEXT_COLOR

            text_surf = self._font_option.render(label, True, color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

        screen.set_clip(None)

        if self._scroll_offset > 0:
            up = self._font_subtitle.render("▲ más arriba", True, config.SUBTEXT_COLOR)
            screen.blit(up, up.get_rect(center=(width // 2, list_top - 10)))
        if self._scroll_offset + visible_count < n:
            down = self._font_subtitle.render(
                "▼ más abajo", True, config.SUBTEXT_COLOR
            )
            screen.blit(down, down.get_rect(center=(width // 2, list_bottom + 8)))
