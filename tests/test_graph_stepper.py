"""Pruebas del stepper BFS/DFS del grafo."""

from __future__ import annotations

import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pygame

pygame.init()

from ds_visualizer import config
from ds_visualizer.animations.graph import GraphAnimation


def _labels(g: GraphAnimation, ids: set[int] | list[int]) -> list[str]:
    return [g.vertices[i] for i in sorted(ids)]


def _role_map(g: GraphAnimation) -> dict[str, str]:
    roles: dict[str, str] = {}
    for vid, name in g.vertices.items():
        if g.focus_idx == vid:
            roles[name] = "current"
        elif vid in g.frontier_set:
            roles[name] = "frontier"
        elif vid in g.highlight_set:
            roles[name] = "visited"
        else:
            roles[name] = "plain"
    return roles


def _fill_colors(g: GraphAnimation) -> dict[str, tuple[int, int, int]]:
    """Color de relleno real cerca del borde interno (evita la letra)."""
    surf = pygame.Surface((900, 500))
    rect = pygame.Rect(20, 40, 860, 420)
    g.clear_hit_targets()
    g.draw(surf, rect)
    pos = g._compute_positions(rect)
    out: dict[str, tuple[int, int, int]] = {}
    for vid, (x, y) in pos.items():
        # Offset para no muestrear el glifo de la etiqueta
        out[g.vertices[vid]] = tuple(surf.get_at((x + 14, y)))[:3]
    return out


class GraphStepperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.g = GraphAnimation()
        self.g.interactive = True

    def test_bfs_order_from_a(self) -> None:
        order, parent = self.g._bfs(0)
        self.assertEqual(
            [self.g.vertices[v] for v in order],
            ["A", "B", "C", "D", "E", "F"],
        )
        self.assertIsNone(parent[0])
        self.assertEqual(parent[1], 0)
        self.assertEqual(parent[2], 0)

    def test_dfs_order_from_a(self) -> None:
        order, _parent = self.g._dfs(0)
        self.assertEqual(
            [self.g.vertices[v] for v in order],
            ["A", "B", "D", "F", "C", "E"],
        )

    def test_bfs_does_not_paint_all_at_once(self) -> None:
        self.g._execute_operation(self.g.operations[0], "A")
        self.assertTrue(self.g.step_mode)
        self.assertIsNone(self.g.live_op)
        self.assertEqual(len(self.g.steps), 6)
        self.assertEqual(self.g.step_index, 0)
        self.assertEqual(self.g.focus_idx, 0)
        self.assertEqual(self.g.highlight_set, {0})
        # Solo A visitado/actual; B y C en cola
        roles = _role_map(self.g)
        self.assertEqual(roles["A"], "current")
        self.assertEqual(roles["B"], "frontier")
        self.assertEqual(roles["C"], "frontier")
        self.assertEqual(roles["D"], "plain")
        self.assertEqual(roles["E"], "plain")
        self.assertEqual(roles["F"], "plain")

    def test_bfs_advances_one_vertex_per_step(self) -> None:
        self.g._execute_operation(self.g.operations[0], "A")
        expected = ["A", "B", "C", "D", "E", "F"]
        for i, label in enumerate(expected):
            self.assertEqual(self.g.vertices[self.g.focus_idx], label, f"step {i}")
            self.assertEqual(
                len(self.g.highlight_set),
                i + 1,
                f"visited count at step {i}",
            )
            # Nadie fuera del prefijo del orden debería estar visitado
            visited_labels = {self.g.vertices[v] for v in self.g.highlight_set}
            self.assertEqual(visited_labels, set(expected[: i + 1]))
            if i < len(expected) - 1:
                self.g.step_next()
                self.assertTrue(self.g.step_mode)

    def test_bfs_auto_advance_with_update(self) -> None:
        self.g._execute_operation(self.g.operations[0], "A")
        self.assertTrue(self.g.step_auto)
        self.assertEqual(self.g.step_index, 0)
        # Menos de un paso: sigue en 0
        self.g.update(0.5)
        self.assertEqual(self.g.step_index, 0)
        self.assertEqual(self.g.focus_idx, 0)
        # Completa un intervalo → avanza a B
        self.g.update(self.g.STEP_DURATION)
        self.assertEqual(self.g.step_index, 1)
        self.assertEqual(self.g.vertices[self.g.focus_idx], "B")
        self.assertEqual(self.g.highlight_set, {0, 1})

    def test_bfs_auto_does_not_skip_to_end(self) -> None:
        self.g._execute_operation(self.g.operations[0], "A")
        # Simula ~2.5s: debe haber avanzado ~2 pasos, no 6
        for _ in range(5):
            self.g.update(0.5)
        # 2.5 / 1.05 ≈ 2 avances → step_index 2 (C)
        self.assertLess(self.g.step_index, 5)
        self.assertTrue(self.g.step_mode)
        self.assertLess(len(self.g.highlight_set), 6)

    def test_dfs_step_by_step(self) -> None:
        self.g._execute_operation(self.g.operations[1], "A")
        self.assertTrue(self.g.step_mode)
        expected = ["A", "B", "D", "F", "C", "E"]
        for i, label in enumerate(expected):
            self.assertEqual(self.g.vertices[self.g.focus_idx], label, f"dfs {i}")
            if i < len(expected) - 1:
                self.g.step_next()

    def test_dfs_from_c(self) -> None:
        self.g._execute_operation(self.g.operations[1], "C")
        self.assertEqual(self.g.vertices[self.g.focus_idx], "C")
        self.assertEqual(self.g.highlight_set, {2})
        order = [self.g.vertices[s.current_idx] for s in self.g.steps]
        self.assertEqual(order[0], "C")
        self.assertEqual(len(order), 6)

    def test_pixel_fills_differ_per_role(self) -> None:
        self.g._execute_operation(self.g.operations[0], "A")
        colors = _fill_colors(self.g)
        self.assertEqual(colors["A"], config.CURRENT_COLOR)
        self.assertEqual(colors["B"], config.FRONTIER_COLOR)
        self.assertEqual(colors["C"], config.FRONTIER_COLOR)
        self.assertEqual(colors["D"], config.CODE_BG)
        self.g.step_next()
        colors = _fill_colors(self.g)
        self.assertEqual(colors["B"], config.CURRENT_COLOR)
        self.assertEqual(colors["A"], config.VISITED_COLOR)

    def test_space_pauses_auto(self) -> None:
        self.g._execute_operation(self.g.operations[0], "A")
        self.assertTrue(self.g.step_auto)
        self.g.handle_key(pygame.K_SPACE)
        self.assertFalse(self.g.step_auto)
        self.assertEqual(self.g.vertices[self.g.focus_idx], "B")
        # update largo no avanza si está pausado
        idx = self.g.step_index
        self.g.update(5.0)
        self.assertEqual(self.g.step_index, idx)


if __name__ == "__main__":
    unittest.main()
