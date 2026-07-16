"""Animación visual para Grafo."""

import copy
import math

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation, Operation


class GraphAnimation(BaseAnimation):
    """Muestra un grafo no dirigido con animaciones BFS y DFS."""

    def __init__(self) -> None:
        super().__init__()
        self._initial_vertices = {
            0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F",
        }
        self._initial_edges = [
            (0, 1), (0, 2), (1, 3), (1, 4),
            (2, 4), (2, 5), (3, 5),
        ]
        self.vertices = copy.deepcopy(self._initial_vertices)
        self.edges = copy.deepcopy(self._initial_edges)
        self.bfs_order = [0, 1, 2, 3, 4, 5]
        self.dfs_order = [0, 1, 3, 5, 2, 4]
        self._next_vertex_id = 6
        self._highlighted: set[int] = set()
        self._last_order: list[int] = []
        self.actions = [
            ("BFS: recorrido en anchura", 5.0),
            ("DFS: recorrido en profundidad", 5.0),
            ("Agregando vértice (G)", 5.0),
            ("Agregando arista (B-F)", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "BFS", "bfs",
                prompt="Inicio BFS:",
                example="A",
            ),
            Operation(
                pygame.K_2, "DFS", "dfs",
                prompt="Inicio DFS:",
                example="A",
            ),
            Operation(
                pygame.K_3, "Add vertex", "add_vertex",
                prompt="Etiqueta del vértice:",
                example="G",
            ),
            Operation(
                pygame.K_4, "Add edge", "add_edge",
                prompt="Par de vértices:",
                example="B F",
            ),
        ])
        self.extra_vertex = None
        self.extra_edge = None

    def reset(self) -> None:
        super().reset()
        self.vertices = copy.deepcopy(self._initial_vertices)
        self.edges = copy.deepcopy(self._initial_edges)
        self._next_vertex_id = 6
        self._highlighted = set()
        self._last_order = []
        self.extra_vertex = None
        self.extra_edge = None

    def _label_to_id(self, label: str) -> int | None:
        label = label.strip().upper()
        for vid, name in self.vertices.items():
            if name.upper() == label:
                return vid
        return None

    def _bfs(self, start: int = 0) -> list[int]:
        visited: list[int] = []
        queue = [start]
        seen = {start}
        while queue:
            v = queue.pop(0)
            visited.append(v)
            for a, b in self.edges:
                nbr = b if a == v else a if b == v else None
                if nbr is not None and nbr not in seen:
                    seen.add(nbr)
                    queue.append(nbr)
        return visited

    def _dfs(self, start: int = 0) -> list[int]:
        visited: list[int] = []
        seen: set[int] = set()

        def walk(v: int) -> None:
            if v in seen:
                return
            seen.add(v)
            visited.append(v)
            for a, b in self.edges:
                nbr = b if a == v else a if b == v else None
                if nbr is not None and nbr not in seen:
                    walk(nbr)

        walk(start)
        return visited

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        labels = ", ".join(self.vertices[v] for v in sorted(self.vertices))

        if op_id in ("bfs", "dfs"):
            token = self.parse_token(user_input or "A")
            if token is None:
                return "Indicá un vértice de inicio"
            start = self._label_to_id(token)
            if start is None:
                return f"'{token}' no existe. Vértices: {labels}"
            order = self._bfs(start) if op_id == "bfs" else self._dfs(start)
            self._last_order = order
            self._highlighted = set(order)
            name = "BFS" if op_id == "bfs" else "DFS"
            path = " -> ".join(self.vertices[v] for v in order)
            return f"{name} desde {self.vertices[start]}: {path}"

        if op_id == "add_vertex":
            token = self.parse_token(user_input or "")
            if token is None:
                return "Indicá una etiqueta (ej: G)"
            label = token.upper()
            if any(v.upper() == label for v in self.vertices.values()):
                return f"El vértice '{label}' ya existe"
            if len(label) > 3:
                return "Usá una etiqueta corta (máx. 3 caracteres)"
            self.vertices[self._next_vertex_id] = label
            self._highlighted = {self._next_vertex_id}
            self._next_vertex_id += 1
            return f"Vértice '{label}' agregado"

        if op_id == "add_edge":
            pair = self.parse_pair(user_input or "")
            if pair is None:
                return f"Formato: dos vértices. Ej: B F. Disponibles: {labels}"
            a_lbl, b_lbl = pair
            a = self._label_to_id(a_lbl)
            b = self._label_to_id(b_lbl)
            if a is None:
                return f"'{a_lbl}' no existe. Vértices: {labels}"
            if b is None:
                return f"'{b_lbl}' no existe. Vértices: {labels}"
            if a == b:
                return "Los extremos deben ser distintos"
            edge = tuple(sorted((a, b)))
            existing = {tuple(sorted(e)) for e in self.edges}
            if edge in existing:
                return f"Arista {self.vertices[a]}-{self.vertices[b]} ya existe"
            self.edges.append((a, b))
            self._highlighted = {a, b}
            return f"Arista {self.vertices[a]}-{self.vertices[b]} agregada"

        return ""

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.interactive:
            self.extra_vertex = None
            self.extra_edge = None

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            self._draw_interactive(surface, rect)
            return

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

    def _draw_interactive(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        positions = self._compute_positions(rect)
        highlighted = set(self._highlighted)
        if self.live_op in ("bfs", "dfs") and self._last_order:
            count = int(self.live_progress() * (len(self._last_order) + 1))
            highlighted = set(self._last_order[:count])
        active_edges = self._get_active_edges(positions, highlighted)
        self._draw_edges_lines(surface, positions, active_edges, highlighted)
        self._draw_vertices_circles(surface, positions, highlighted)

        hint = self._font.render(
            "4: arista pide par (ej: B F)  |  3: etiqueta del vértice",
            True,
            config.SUBTEXT_COLOR,
        )
        surface.blit(hint, hint.get_rect(midtop=(rect.centerx, rect.y + 8)))

    def _compute_positions(self, rect: pygame.Rect) -> dict[int, tuple[int, int]]:
        cx = rect.x + rect.width // 2
        cy = rect.y + rect.height // 2
        rx = rect.width // 2 - 50
        ry = rect.height // 2 - 60
        n = max(len(self.vertices), 1)
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

            label = self.vertices.get(vid, "?")
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
        self.extra_vertex = 6
        return {0, 2, 3, 6}

    def _get_add_edge_states(self) -> set[int]:
        p = self.progress()
        if p < 0.4:
            return {1, 5}
        self.extra_edge = (1, 5)
        return {1, 5}
