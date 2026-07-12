"""Máquina de estados principal: menú ↔ visualización."""

import pygame
from ds_visualizer import config
from ds_visualizer.states import MenuState, VisualizationState


class App:
    """Controla el ciclo de vida y la transición entre estados."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.running = True
        self.screen = screen
        self.window_width = config.WINDOW_WIDTH
        self.window_height = config.WINDOW_HEIGHT

        self.menu_state = MenuState()
        self.vis_state = VisualizationState()
        self.current_state = self.menu_state
        self.menu_state.on_enter(screen)

    def handle_events(self) -> None:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self._handle_resize(event)
            elif event.type == pygame.KEYDOWN:
                if (
                    event.key == pygame.K_q
                    and event.mod & pygame.KMOD_CTRL
                ):
                    self.running = False

        self.current_state.handle_events(events)

        if self.current_state is self.menu_state and self.menu_state.selected_ds is not None:
            ds_key = self.menu_state.selected_ds
            self.menu_state.selected_ds = None
            if ds_key == "__quit__":
                self.running = False
            else:
                self._switch_to_visualization(ds_key)
        elif self.current_state is self.vis_state and self.vis_state.back_to_menu:
            self.vis_state.back_to_menu = False
            self._switch_to_menu()

    def update(self, dt: float) -> None:
        self.current_state.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(config.BG_COLOR)
        self.current_state.draw(screen, self.window_width, self.window_height)

    def _switch_to_menu(self) -> None:
        self.current_state = self.menu_state
        self.menu_state.on_enter(self.screen)

    def _switch_to_visualization(self, ds_key: str) -> None:
        self.vis_state.on_enter(ds_key, self.screen, self.window_width, self.window_height)
        self.current_state = self.vis_state

    def _handle_resize(self, event: pygame.event.Event) -> None:
        self.window_width = max(event.w, config.MIN_WIDTH)
        self.window_height = max(event.h, config.MIN_HEIGHT)
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height),
            pygame.RESIZABLE,
        )
        self.current_state.on_resize(
            self.screen, self.window_width, self.window_height
        )
