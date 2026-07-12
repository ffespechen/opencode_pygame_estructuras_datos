"""Punto de entrada de la aplicación."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame
from ds_visualizer import config
from ds_visualizer.app import App


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Visualizador de Estructuras de Datos")

    screen = pygame.display.set_mode(
        (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
        pygame.RESIZABLE,
    )
    clock = pygame.time.Clock()

    app = App(screen)

    while app.running:
        dt = clock.tick(config.FPS) / 1000.0
        app.handle_events()
        app.update(dt)
        app.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
