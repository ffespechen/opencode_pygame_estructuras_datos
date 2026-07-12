"""Clase base para todas las animaciones de estructuras de datos."""

import pygame


class BaseAnimation:
    """Define la interfaz común: update(dt), draw(surface, rect) y current_action."""

    def __init__(self) -> None:
        self.action_index = 0
        self.action_timer = 0.0
        self.actions: list[tuple[str, float]] = []  # (nombre, duracion en segundos)
        self.current_action = ""
        self._font = None

    def _init_font(self) -> None:
        self._font = pygame.font.SysFont("monospace", 14, bold=True)

    def update(self, dt: float) -> None:
        if not self.actions:
            return

        self.action_timer += dt
        _, duration = self.actions[self.action_index]
        if self.action_timer >= duration:
            self.action_timer = 0.0
            self.action_index = (self.action_index + 1) % len(self.actions)

        self.current_action = self.actions[self.action_index][0]

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        raise NotImplementedError

    def progress(self) -> float:
        """Devuelve el progreso de la acción actual en rango [0, 1)."""
        if not self.actions:
            return 0.0
        _, duration = self.actions[self.action_index]
        if duration == 0:
            return 0.0
        return min(self.action_timer / duration, 0.999)
