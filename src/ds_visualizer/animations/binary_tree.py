"""Animación visual para Binary Tree (Árbol Binario)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation


class BinaryTreeAnimation(BaseAnimation):
    """Muestra un árbol binario con animaciones de los tres recorridos principales."""

    def __init__(self) -> None:
        super().__init__()
        self.nodes = {
            0: {"v": 50, "l": 1, "r": 2},
            1: {"v": 30, "l": 3, "r": 4},
            2: {"v": 70, "l": 5, "r": 6},
            3: {"v": 20, "l": None, "r": None},
            4: {"v": 40, "l": None, "r": None},
            5: {"v": 60, "l": None, "r": None},
            6: {"v": 80, "l": None, "r": None},
        }
        self.preorder = [0, 1, 3, 4, 2, 5, 6]
        self.inorder = [3, 1, 4, 0, 5, 2, 6]
        self.postorder = [3, 4, 1, 5, 6, 2, 0]
        self.actions = [
            ("Recorrido Preorden (R-I-D)", 5.0),
            ("Recorrido Inorden (I-R-D)", 5.0),
            ("Recorrido Postorden (I-D-R)", 5.0),
            ("Inserción en BST (valor=55)", 5.0),
        ]

    def update(self, dt: float) -> None:
        super().update(dt)

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        positions = self._compute_positions(rect)

        highlighted_nodes: set[int] = set()
        if self.action_index == 0:
            highlighted_nodes = self._get_traversal_highlight(self.preorder)
        elif self.action_index == 1:
            highlighted_nodes = self._get_traversal_highlight(self.inorder)
        elif self.action_index == 2:
            highlighted_nodes = self._get_traversal_highlight(self.postorder)
        elif self.action_index == 3:
            highlighted_nodes = self._get_insert_highlight()

        edges_drawn: set[tuple[int, int]] = set()
        self._draw_edges(surface, positions, 0, highlighted_nodes, edges_drawn)
        self._draw_nodes_circles(surface, positions, highlighted_nodes)

    def _compute_positions(self, rect: pygame.Rect) -> dict[int, tuple[int, int]]:
        levels = {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2}
        level_nodes: dict[int, list[int]] = {}
        for nid, lv in levels.items():
            level_nodes.setdefault(lv, []).append(nid)

        max_level = max(levels.values())
        v_spacing = (rect.height - 120) // (max_level + 1)
        positions: dict[int, tuple[int, int]] = {}

        for lv in range(max_level + 1):
            nodes_at_level = level_nodes.get(lv, [])
            n = len(nodes_at_level)
            if n == 0:
                continue
            h_spacing = rect.width // (n + 1)
            y = rect.y + 60 + lv * v_spacing
            for i, nid in enumerate(nodes_at_level):
                x = rect.x + (i + 1) * h_spacing
                positions[nid] = (x, y)

        return positions

    def _draw_edges(
        self, surface: pygame.Surface,
        positions: dict[int, tuple[int, int]],
        node_id: int,
        highlighted: set[int],
        drawn: set[tuple[int, int]],
    ) -> None:
        node = self.nodes[node_id]
        for child_key in ("l", "r"):
            child_id = node[child_key]
            if child_id is not None and child_id in positions:
                edge = (node_id, child_id)
                if edge not in drawn:
                    drawn.add(edge)
                    color = (
                        config.HIGHLIGHT_COLOR
                        if node_id in highlighted or child_id in highlighted
                        else config.DIVIDER_COLOR
                    )
                    p1 = positions[node_id]
                    p2 = positions[child_id]
                    pygame.draw.line(surface, color, p1, p2, width=2)
                    self._draw_edges(surface, positions, child_id, highlighted, drawn)

    def _draw_nodes_circles(
        self, surface: pygame.Surface,
        positions: dict[int, tuple[int, int]],
        highlighted: set[int],
    ) -> None:
        radius = 22
        for nid, (x, y) in positions.items():
            is_highlighted = nid in highlighted
            fg = config.HIGHLIGHT_COLOR if is_highlighted else config.TEXT_COLOR
            border = fg
            bg = config.CODE_BG

            pygame.draw.circle(surface, bg, (x, y), radius)
            pygame.draw.circle(surface, border, (x, y), radius, width=2)

            val = self.nodes[nid]["v"]
            val_surf = self._font.render(str(val), True, fg)
            val_rect = val_surf.get_rect(center=(x, y))
            surface.blit(val_surf, val_rect)

    def _get_traversal_highlight(self, order: list[int]) -> set[int]:
        p = self.progress()
        count = int(p * (len(order) + 1))
        return set(order[:count])

    def _get_insert_highlight(self) -> set[int]:
        p = self.progress()
        path = [0, 2, 5]
        if p < 0.3:
            return set()
        elif p < 0.5:
            return {0}
        elif p < 0.7:
            return {0, 2}
        else:
            return {0, 2, 5}
