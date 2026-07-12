"""Animación visual para Grafo."""

import math

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation


class GraphAnimation(BaseAnimation):
    """Muestra un grafo no dirigido con animaciones BFS y DFS."""

    def __init__(self) -> None:
        super().__init__()
        self.vertices = {
            0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F",
        }
        self.edges = [
            (0, 1), (0, 2), (1, 3), (1, 4),
            (2, 4), (2, 5), (3, 5),
        ]
        self.bfs_order = [0, 1, 2, 3, 4, 5]
        self.dfs_order = [0, 1, 3, 5, 2, 4]
        self.actions = [
            ("BFS: recorrido en anchura", 5.0),
            ("DFS: recorrido en profundidad", 5.0),
            ("Agregando vértice (G)", 5.0),
            ("Agregando arista (B-F)", 5.0),
        ]
        self.extra_vertex = None
        self.extra_edge = None

    def update(self, dt: float) -> None:
        super().update(dt)
        self.extra_vertex = None
        self.extra_edge = None

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        positions = self._compute_positions(rect)

        highlighted: set[int] = set()
        if self.action_index == 0:
            highlighted = self._get_bfs_highlight()
        elif self.action_index == 1:
            highlighted = self._get_dfs_highlight()
        elif self.action_index == 2:
            highlighted = self._get_add_vertex_states()
        elif self.action_index == 3:
            highlighted = self._get_add_edge_states()

        active_edges = self._get_active_edges(positions, highlighted)
        self._draw_edges_lines(surface, positions, active_edges, highlighted)
        self._draw_vertices_circles(surface, positions, highlighted)

    def _compute_positions(self, rect: pygame.Rect) -> dict[int, tuple[int, int]]:
        cx = rect.x + rect.width // 2
        cy = rect.y + rect.height // 2
        rx = rect.width // 2 - 50
        ry = rect.height // 2 - 60
        n = len(self.vertices)
        positions: dict[int, tuple[int, int]] = {}

        for i, vid in enumerate(self.vertices):
            angle = 2 * math.pi * i / n - math.pi / 2
            x = cx + int(rx * math.cos(angle))
            y = cy + int(ry * math.sin(angle))
            positions[vid] = (x, y)

        if self.extra_vertex is not None:
            positions[6] = (cx + int(rx * 0.3), cy - int(ry * 0.2))

        return positions

    def _draw_edges_lines(
        self, surface: pygame.Surface,
        positions: dict[int, tuple[int, int]],
        active_edges: set[tuple[int, int]],
        highlighted: set[int],
    ) -> None:
        drawn: set[tuple[int, int]] = set()
        for a, b in self.edges:
            if a in positions and b in positions:
                edge = tuple(sorted((a, b)))
                if edge not in drawn:
                    drawn.add(edge)
                    color = (
                        config.HIGHLIGHT_COLOR
                        if edge in active_edges
                        else config.DIVIDER_COLOR
                    )
                    width = 3 if edge in active_edges else 2
                    pygame.draw.line(
                        surface, color, positions[a], positions[b], width=width,
                    )

    def _draw_vertices_circles(
        self, surface: pygame.Surface,
        positions: dict[int, tuple[int, int]],
        highlighted: set[int],
    ) -> None:
        radius = 24
        for vid, (x, y) in positions.items():
            is_highlighted = vid in highlighted
            fg = config.HIGHLIGHT_COLOR if is_highlighted else config.TEXT_COLOR
            border = fg
            bg = config.CODE_BG

            pygame.draw.circle(surface, bg, (x, y), radius)
            pygame.draw.circle(surface, border, (x, y), radius, width=2)

            label = self.vertices.get(vid, "G")
            val_surf = self._font.render(label, True, fg)
            val_rect = val_surf.get_rect(center=(x, y))
            surface.blit(val_surf, val_rect)

    def _get_active_edges(
        self, positions: dict[int, tuple[int, int]], highlighted: set[int],
    ) -> set[tuple[int, int]]:
        active: set[tuple[int, int]] = set()
        for a, b in self.edges:
            if a in highlighted and b in highlighted:
                edge = tuple(sorted((a, b)))
                active.add(edge)
        return active

    def _get_bfs_highlight(self) -> set[int]:
        p = self.progress()
        count = int(p * (len(self.bfs_order) + 1))
        return set(self.bfs_order[:count])

    def _get_dfs_highlight(self) -> set[int]:
        p = self.progress()
        count = int(p * (len(self.dfs_order) + 1))
        return set(self.dfs_order[:count])

    def _get_add_vertex_states(self) -> set[int]:
        p = self.progress()
        if p < 0.5:
            return set()
        else:
            self.extra_vertex = 6
            return {0, 2, 3, 6}

    def _get_add_edge_states(self) -> set[int]:
        p = self.progress()
        if p < 0.4:
            return {1, 5}
        else:
            self.extra_edge = (1, 5)
            return {1, 5}
