"""Animación visual para Union-Find (Disjoint Set Union)."""

import copy

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import AnimStep, BaseAnimation, Challenge, Operation


class UnionFindAnimation(BaseAnimation):
    """Muestra conjuntos disjuntos: find, union y path compression."""

    def __init__(self) -> None:
        super().__init__()
        self.elements = ["A", "B", "C", "D", "E", "F"]
        self.parent: dict[str, str] = {e: e for e in self.elements}
        self._initial_parent = copy.deepcopy(self.parent)
        self._find_element = "C"
        self._union_pair = ("A", "D")
        self._highlighted: set[str] = set()
        self._highlight_edges: list[tuple[str, str]] = []
        self.actions = [
            ("Find: buscar raíz de C", 5.0),
            ("Union: unir conjuntos A y D", 5.0),
            ("Union: unir C con E", 5.0),
            ("Path compression en Find(F)", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Find", "find",
                prompt="Elemento:", example="C",
                complexity="O(α(n))", mutates=False, uses_selection=True,
            ),
            Operation(
                pygame.K_2, "Union", "union",
                prompt="Par de elementos:", example="A D",
                complexity="O(α(n))",
            ),
        ])
        self.set_challenges([
            Challenge(
                "uf_ad", "Unir A y D",
                "Union A D (misma raíz).", "Union → A D",
                lambda a: a._find_root("A") == a._find_root("D"),
            ),
        ])

    def reset(self) -> None:
        super().reset()
        self.parent = copy.deepcopy(self._initial_parent)
        self._find_element = "C"
        self._union_pair = ("A", "D")
        self._highlighted = set()
        self._highlight_edges = []

    def _find_root(self, x: str) -> str:
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def _find_path(self, x: str) -> list[str]:
        path = [x]
        while self.parent[x] != x:
            x = self.parent[x]
            path.append(x)
        return path

    def _roots(self) -> set[str]:
        return {e for e in self.elements if self.parent[e] == e}

    def build_steps(
        self, op_id: str, user_input: str | None = None
    ) -> list[AnimStep]:
        if op_id == "find":
            elem = (user_input or self._find_element or "C").strip().upper()
            if elem not in self.elements:
                return []
            path = self._find_path(elem)
            steps = []
            seen: set[str] = set()
            edges: list[tuple[str, str]] = []
            for i, e in enumerate(path):
                seen.add(e)
                if i > 0:
                    edges.append((path[i - 1], e))
                steps.append(AnimStep(
                    f"Find: visitar {e}"
                    + (f" → raíz" if i == len(path) - 1 else ""),
                    highlight_ids=frozenset(seen),
                    current_id=e,
                    edge_pairs=frozenset(edges),
                    note=f"{i + 1}/{len(path)} · Space=siguiente",
                ))
            return steps
        if op_id == "union":
            pair = self.parse_pair(user_input or "")
            if pair is None:
                return []
            a, b = pair
            if a not in self.elements or b not in self.elements:
                return []
            # Tras apply_operation ya están unidos; mostrar a, b y la nueva arista
            ra = self._find_root(a)
            return [
                AnimStep(
                    f"Union: Find({a}) y Find({b})",
                    highlight_ids=frozenset({a, b}),
                    current_id=a,
                    note="1/2 · Space=siguiente",
                ),
                AnimStep(
                    f"Union: enlace bajo raíz {ra}",
                    highlight_ids=frozenset({a, b, ra}),
                    current_id=ra,
                    edge_pairs=frozenset(
                        [(x, self.parent[x]) for x in (a, b) if self.parent[x] != x]
                    ),
                    note="2/2 · Space=siguiente",
                ),
            ]
        return []

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "find":
            elem = self.parse_token(user_input or "")
            if elem is None:
                return "Indicá un elemento"
            elem = elem.upper()
            if elem not in self.elements:
                return f"'{elem}' no existe. Elementos: A-F"
            self._find_element = elem
            path = self._find_path(elem)
            # Stepper pinta iteración a iteración
            self._highlighted = set()
            self._highlight_edges = []
            root = path[-1]
            return f"Find({elem}) = {root}"
        if op_id == "union":
            pair = self.parse_pair(user_input or "")
            if pair is None:
                return "Formato: dos elementos (ej: A D)"
            a, b = pair
            if a not in self.elements or b not in self.elements:
                return f"Elementos válidos: A-F"
            ra, rb = self._find_root(a), self._find_root(b)
            if ra == rb:
                self._highlighted = set()
                self._highlight_edges = []
                return f"Union({a},{b}): ya en el mismo conjunto"
            self.parent[rb] = ra
            self._highlighted = set()
            self._highlight_edges = []
            return f"Union({a},{b}): {b} → {ra}"
        return ""

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            highlighted = set(self._highlighted)
            edges = list(self._highlight_edges)
            current: str | None = None
            if self.step_mode:
                highlighted = set(self.highlight_ids)
                current = self.focus_id or None
                edges = [
                    (a, b) for a, b in self.step_edges
                    if isinstance(a, str) and isinstance(b, str)
                ]
            elif self.live_op == "find":
                path = self._find_path(self._find_element)
                count = max(1, int(self.live_progress() * len(path)))
                count = min(count, len(path))
                highlighted = set(path[:count])
                current = path[count - 1]
                edges = [
                    (path[i], path[i + 1])
                    for i in range(min(count - 1, len(path) - 1))
                ]
            self._draw_forest(
                surface, rect, self.parent, self._roots(),
                highlighted, edges, current=current,
            )
            self._hint(surface, rect, self.operations_hint())
            return

        if self.action_index == 0:
            self._draw_find(surface, rect)
        elif self.action_index == 1:
            self._draw_union_ad(surface, rect)
        elif self.action_index == 2:
            self._draw_union_ce(surface, rect)
        elif self.action_index == 3:
            self._draw_path_compression(surface, rect)

    def _positions(self, rect: pygame.Rect) -> dict[str, tuple[int, int]]:
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
        role: str | None = None,
    ) -> None:
        x, y = pos
        radius = 22
        if role is None:
            role = "visited" if highlight else "plain"
        fg = self.color_for_role(role)
        border = config.ACCENT_COLOR if is_root else fg
        width = 3 if role == "current" or is_root else 2
        pygame.draw.circle(surface, config.CODE_BG, (x, y), radius)
        pygame.draw.circle(surface, border, (x, y), radius, width=width)
        lbl = self._font.render(label, True, fg)
        surface.blit(lbl, lbl.get_rect(center=(x, y)))

    def _draw_parent_arrow(
        self,
        surface: pygame.Surface,
        child: tuple[int, int],
        parent: tuple[int, int],
        highlight: bool = False,
    ) -> None:
        color = config.PATH_EDGE_COLOR if highlight else config.DIVIDER_COLOR
        width = 3 if highlight else 2
        pygame.draw.line(surface, color, child, parent, width=width)
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
        current: str | None = None,
    ) -> None:
        highlighted = highlighted or set()
        highlight_edges = highlight_edges or []
        edge_set = set(highlight_edges)
        pos = self._positions(rect)

        for child, par in parent.items():
            if child != par:
                self._draw_parent_arrow(
                    surface,
                    pos[child],
                    pos[par],
                    highlight=(child, par) in edge_set or (par, child) in edge_set,
                )

        for name in self.elements:
            if current and name == current:
                role = "current"
            elif name in highlighted:
                role = "visited"
            else:
                role = "plain"
            self._draw_node(
                surface,
                pos[name],
                name,
                highlight=name in highlighted,
                is_root=name in roots,
                role=role,
            )
            x, y = pos[name]
            hit = pygame.Rect(x - 22, y - 22, 44, 44)
            self.register_hit(
                f"el:{name}", hit, label=name, value=name, key=name,
            )

    def _draw_find(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
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
        p = self.progress()
        pos = self._positions(rect)
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
