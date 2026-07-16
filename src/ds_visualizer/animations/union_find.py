"""Animación visual para Union-Find (Disjoint Set Union)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation


class UnionFindAnimation(BaseAnimation):
    """Muestra conjuntos disjuntos: find, union y path compression."""

    def __init__(self) -> None:
        super().__init__()
        self.elements = ["A", "B", "C", "D", "E", "F"]
        self.actions = [
            ("Find: buscar raíz de C", 5.0),
            ("Union: unir conjuntos A y D", 5.0),
            ("Union: unir C con E", 5.0),
            ("Path compression en Find(F)", 5.0),
        ]

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.action_index == 0:
            self._draw_find(surface, rect)
        elif self.action_index == 1:
            self._draw_union_ad(surface, rect)
        elif self.action_index == 2:
            self._draw_union_ce(surface, rect)
        elif self.action_index == 3:
            self._draw_path_compression(surface, rect)

    def _positions(self, rect: pygame.Rect) -> dict[str, tuple[int, int]]:
        # Layout en dos filas de raíces / hijos
        cx = rect.centerx
        top = rect.y + 55
        mid = rect.y + rect.height // 2 + 5
        bot = rect.y + rect.height - 70
        return {
            "A": (cx - 200, top),
            "B": (cx - 200, mid),
            "C": (cx - 80, mid),
            "D": (cx + 40, top),
            "E": (cx + 160, top),
            "F": (cx + 160, bot),
        }

    def _draw_node(
        self,
        surface: pygame.Surface,
        pos: tuple[int, int],
        label: str,
        highlight: bool = False,
        is_root: bool = False,
    ) -> None:
        x, y = pos
        radius = 22
        fg = config.HIGHLIGHT_COLOR if highlight else config.TEXT_COLOR
        border = config.ACCENT_COLOR if is_root else fg
        pygame.draw.circle(surface, config.CODE_BG, (x, y), radius)
        pygame.draw.circle(surface, border, (x, y), radius, width=2 if not is_root else 3)
        lbl = self._font.render(label, True, fg)
        surface.blit(lbl, lbl.get_rect(center=(x, y)))

    def _draw_parent_arrow(
        self,
        surface: pygame.Surface,
        child: tuple[int, int],
        parent: tuple[int, int],
        highlight: bool = False,
    ) -> None:
        color = config.HIGHLIGHT_COLOR if highlight else config.DIVIDER_COLOR
        pygame.draw.line(surface, color, child, parent, width=2)
        # pequeña punta hacia el padre
        dx = parent[0] - child[0]
        dy = parent[1] - child[1]
        length = max((dx * dx + dy * dy) ** 0.5, 1)
        ux, uy = dx / length, dy / length
        tip = (parent[0] - ux * 24, parent[1] - uy * 24)
        left = (tip[0] - uy * 5 - ux * 6, tip[1] + ux * 5 - uy * 6)
        right = (tip[0] + uy * 5 - ux * 6, tip[1] - ux * 5 - uy * 6)
        pygame.draw.polygon(surface, color, [tip, left, right])

    def _hint(self, surface: pygame.Surface, rect: pygame.Rect, text: str) -> None:
        lbl = self._font.render(text, True, config.SUBTEXT_COLOR)
        surface.blit(lbl, lbl.get_rect(midbottom=(rect.centerx, rect.bottom - 8)))

    def _draw_forest(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        parent: dict[str, str],
        roots: set[str],
        highlighted: set[str] | None = None,
        highlight_edges: list[tuple[str, str]] | None = None,
    ) -> None:
        highlighted = highlighted or set()
        highlight_edges = highlight_edges or []
        pos = self._positions(rect)

        for child, par in parent.items():
            if child != par:
                self._draw_parent_arrow(
                    surface,
                    pos[child],
                    pos[par],
                    highlight=(child, par) in highlight_edges,
                )

        for name in self.elements:
            self._draw_node(
                surface,
                pos[name],
                name,
                highlight=name in highlighted,
                is_root=name in roots,
            )

    def _draw_find(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        # A raíz de {A,B,C}; D y E y F solos
        parent = {"A": "A", "B": "A", "C": "A", "D": "D", "E": "E", "F": "F"}
        roots = {"A", "D", "E", "F"}
        p = self.progress()
        if p < 0.35:
            hl = {"C"}
            edges = []
            msg = "Find(C): partir desde C"
        elif p < 0.7:
            hl = {"C", "A"}
            edges = [("C", "A")]
            msg = "Find(C): seguir parent → A"
        else:
            hl = {"A"}
            edges = [("C", "A")]
            msg = "Find(C) = A (raíz del conjunto)"
        self._draw_forest(surface, rect, parent, roots, hl, edges)
        self._hint(surface, rect, msg)

    def _draw_union_ad(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.45:
            parent = {"A": "A", "B": "A", "C": "A", "D": "D", "E": "E", "F": "F"}
            roots = {"A", "D", "E", "F"}
            self._draw_forest(
                surface, rect, parent, roots, {"A", "D"}, []
            )
            self._hint(surface, rect, "Union(A, D): dos raíces distintas")
        else:
            parent = {"A": "A", "B": "A", "C": "A", "D": "A", "E": "E", "F": "F"}
            roots = {"A", "E", "F"}
            self._draw_forest(
                surface, rect, parent, roots, {"A", "D"}, [("D", "A")]
            )
            self._hint(surface, rect, "D apunta a A → un solo conjunto")

    def _draw_union_ce(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        # Find(C)=A, Find(E)=E → E.parent = A
        p = self.progress()
        if p < 0.4:
            parent = {"A": "A", "B": "A", "C": "A", "D": "A", "E": "E", "F": "F"}
            roots = {"A", "E", "F"}
            self._draw_forest(
                surface, rect, parent, roots, {"C", "E"}, [("C", "A")]
            )
            self._hint(surface, rect, "Union(C, E): Find(C)=A, Find(E)=E")
        else:
            parent = {"A": "A", "B": "A", "C": "A", "D": "A", "E": "A", "F": "F"}
            roots = {"A", "F"}
            self._draw_forest(
                surface, rect, parent, roots, {"A", "E"}, [("E", "A")]
            )
            self._hint(surface, rect, "E se une bajo la raíz A")

    def _draw_path_compression(
        self, surface: pygame.Surface, rect: pygame.Rect
    ) -> None:
        # Cadena F -> E -> A, luego F apunta directo a A
        p = self.progress()
        pos = self._positions(rect)
        # ajustar F bajo E visualmente
        pos["F"] = (pos["E"][0], pos["E"][1] + 70)
        pos["E"] = (pos["A"][0] + 120, pos["A"][1] + 70)

        if p < 0.45:
            parent = {
                "A": "A", "B": "A", "C": "A", "D": "A", "E": "A", "F": "E"
            }
            for child, par in parent.items():
                if child != par:
                    self._draw_parent_arrow(
                        surface, pos[child], pos[par],
                        highlight=child in ("F", "E"),
                    )
            for name in self.elements:
                self._draw_node(
                    surface, pos[name], name,
                    highlight=name in ("F", "E", "A"),
                    is_root=name == "A",
                )
            self._hint(surface, rect, "Find(F): camino F → E → A")
        else:
            parent = {
                "A": "A", "B": "A", "C": "A", "D": "A", "E": "A", "F": "A"
            }
            for child, par in parent.items():
                if child != par:
                    self._draw_parent_arrow(
                        surface, pos[child], pos[par],
                        highlight=child == "F",
                    )
            for name in self.elements:
                self._draw_node(
                    surface, pos[name], name,
                    highlight=name == "F",
                    is_root=name == "A",
                )
            self._hint(surface, rect, "Path compression: F.parent = A")
