"""Animación visual para Binary Tree (Árbol Binario)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import AnimStep, BaseAnimation, Challenge, Operation


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
        self.bst_values = [50, 30, 70, 20, 40, 60, 80]
        self._initial_bst = list(self.bst_values)
        self.preorder = [0, 1, 3, 4, 2, 5, 6]
        self.inorder = [3, 1, 4, 0, 5, 2, 6]
        self.postorder = [3, 4, 1, 5, 6, 2, 0]
        self.actions = [
            ("Recorrido Preorden (R-I-D)", 5.0),
            ("Recorrido Inorden (I-R-D)", 5.0),
            ("Recorrido Postorden (I-D-R)", 5.0),
            ("Inserción en BST (valor=55)", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Preorder", "preorder",
                complexity="O(n)", mutates=False,
            ),
            Operation(
                pygame.K_2, "Inorder", "inorder",
                complexity="O(n)", mutates=False,
            ),
            Operation(
                pygame.K_3, "Postorder", "postorder",
                complexity="O(n)", mutates=False,
            ),
            Operation(
                pygame.K_4, "Insert", "insert",
                prompt="Valor a insertar:", example="55",
                complexity="O(h)",
            ),
        ])
        self.set_challenges([
            Challenge(
                "bst_55", "Insertar 55",
                "Insertá 55 en el BST.", "Insert → 55",
                lambda a: 55 in a.bst_values,
            ),
            Challenge(
                "bst_size", "Al menos 9 nodos",
                "Insertá valores hasta tener 9 o más.", "Insert varias veces",
                lambda a: len(a.bst_values) >= 9,
            ),
        ])

    def reset(self) -> None:
        super().reset()
        self.bst_values = list(self._initial_bst)

    def build_steps(
        self, op_id: str, user_input: str | None = None
    ) -> list[AnimStep]:
        if op_id not in ("preorder", "inorder", "postorder"):
            return []
        nodes = self._build_nodes_from_values(self.bst_values)
        order = self._traversal_order(nodes, op_id)
        steps = []
        seen: set[int] = set()
        for nid in order:
            seen.add(nid)
            steps.append(AnimStep(
                f"{op_id}: {nodes[nid]['v']}",
                highlight_set=frozenset(seen),
                current_idx=nid,
                note=f"{nodes[nid]['v']} · Space=siguiente",
            ))
        return steps

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id in ("preorder", "inorder", "postorder"):
            self.highlight_set = set()
            return f"Recorrido {op_id}"
        if op_id == "insert":
            val = self.parse_int(user_input or "")
            if val is None:
                return "Indicá un número entero"
            self.bst_values = self._bst_insert(self.bst_values, val)
            self.highlight_set = set()
            return f"Insert BST: {val}"
        return ""

    def _bst_insert(self, values: list[int], val: int) -> list[int]:
        result = list(values)
        if val not in result:
            result.append(val)
        return result

    def _build_nodes_from_values(self, values: list[int]) -> dict:
        if not values:
            return {}
        nodes: dict[int, dict] = {}
        root_id = 0
        nodes[root_id] = {"v": values[0], "l": None, "r": None}
        next_id = 1

        for val in values[1:]:
            cur = root_id
            while True:
                if val < nodes[cur]["v"]:
                    if nodes[cur]["l"] is None:
                        nodes[cur]["l"] = next_id
                        nodes[next_id] = {"v": val, "l": None, "r": None}
                        next_id += 1
                        break
                    cur = nodes[cur]["l"]
                else:
                    if nodes[cur]["r"] is None:
                        nodes[cur]["r"] = next_id
                        nodes[next_id] = {"v": val, "l": None, "r": None}
                        next_id += 1
                        break
                    cur = nodes[cur]["r"]
        return nodes

    def _compute_positions_dynamic(
        self, nodes: dict, rect: pygame.Rect, root: int = 0,
    ) -> dict[int, tuple[int, int]]:
        if not nodes or root not in nodes:
            return {}

        levels: dict[int, list[int]] = {}

        def assign_level(nid: int, lv: int) -> None:
            levels.setdefault(lv, []).append(nid)
            node = nodes[nid]
            if node["l"] is not None:
                assign_level(node["l"], lv + 1)
            if node["r"] is not None:
                assign_level(node["r"], lv + 1)

        assign_level(root, 0)
        max_level = max(levels.keys())
        v_spacing = (rect.height - 120) // max(max_level + 1, 1)
        positions: dict[int, tuple[int, int]] = {}

        for lv in range(max_level + 1):
            nodes_at_level = levels.get(lv, [])
            n = len(nodes_at_level)
            if n == 0:
                continue
            h_spacing = rect.width // (n + 1)
            y = rect.y + 60 + lv * v_spacing
            for i, nid in enumerate(nodes_at_level):
                x = rect.x + (i + 1) * h_spacing
                positions[nid] = (x, y)
        return positions

    def _traversal_order(self, nodes: dict, kind: str, root: int = 0) -> list[int]:
        if root not in nodes:
            return []
        order: list[int] = []

        def walk(nid: int) -> None:
            if nid is None or nid not in nodes:
                return
            if kind == "preorder":
                order.append(nid)
                walk(nodes[nid]["l"])
                walk(nodes[nid]["r"])
            elif kind == "inorder":
                walk(nodes[nid]["l"])
                order.append(nid)
                walk(nodes[nid]["r"])
            else:
                walk(nodes[nid]["l"])
                walk(nodes[nid]["r"])
                order.append(nid)

        walk(root)
        return order

    def update(self, dt: float) -> None:
        super().update(dt)

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            self._draw_interactive(surface, rect)
            return

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

    def _draw_interactive(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        nodes = self._build_nodes_from_values(self.bst_values)
        if not nodes:
            return
        positions = self._compute_positions_dynamic(nodes, rect)

        highlighted: set[int] = set(self.highlight_set)
        current: int | None = None
        if self.step_mode:
            highlighted = set(self.highlight_set)
            current = self.focus_idx if self.focus_idx >= 0 else None
        elif self.live_op in ("preorder", "inorder", "postorder"):
            order = self._traversal_order(nodes, self.live_op)
            count = int(self.live_progress() * (len(order) + 1))
            highlighted = set(order[:count])
            if count > 0:
                current = order[min(count - 1, len(order) - 1)]
        elif self.live_op == "insert":
            highlighted = set(nodes.keys())

        edges_drawn: set[tuple[int, int]] = set()
        self._draw_edges_interactive(
            surface, positions, nodes, 0, highlighted, edges_drawn, current,
        )
        self._draw_nodes_interactive(
            surface, positions, nodes, highlighted, current,
        )

    def _draw_edges_interactive(
        self, surface: pygame.Surface,
        positions: dict[int, tuple[int, int]],
        nodes: dict,
        node_id: int,
        highlighted: set[int],
        drawn: set[tuple[int, int]],
        current: int | None = None,
    ) -> None:
        if node_id not in nodes:
            return
        node = nodes[node_id]
        for child_key in ("l", "r"):
            child_id = node[child_key]
            if child_id is not None and child_id in positions:
                edge = (node_id, child_id)
                if edge not in drawn:
                    drawn.add(edge)
                    is_path = (
                        (current is not None and (
                            node_id == current or child_id == current
                        ))
                        or (node_id in highlighted and child_id in highlighted)
                    )
                    color = (
                        config.PATH_EDGE_COLOR if is_path else config.DIVIDER_COLOR
                    )
                    width = 3 if (
                        current is not None
                        and (node_id == current or child_id == current)
                    ) else 2
                    pygame.draw.line(
                        surface, color, positions[node_id], positions[child_id],
                        width=width,
                    )
                    self._draw_edges_interactive(
                        surface, positions, nodes, child_id, highlighted, drawn,
                        current,
                    )

    def _draw_nodes_interactive(
        self, surface: pygame.Surface,
        positions: dict[int, tuple[int, int]],
        nodes: dict,
        highlighted: set[int],
        current: int | None = None,
    ) -> None:
        radius = 22
        for nid, (x, y) in positions.items():
            if current is not None and nid == current:
                role = "current"
            elif nid in highlighted:
                role = "visited"
            else:
                role = "plain"
            fg = self.color_for_role(role)
            pygame.draw.circle(surface, config.CODE_BG, (x, y), radius)
            pygame.draw.circle(
                surface, fg, (x, y), radius, width=3 if role == "current" else 2,
            )
            val = nodes[nid]["v"]
            val_surf = self._font.render(str(val), True, fg)
            surface.blit(val_surf, val_surf.get_rect(center=(x, y)))
            hit = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
            self.register_hit(
                f"node:{nid}", hit, label=str(val), value=val, index=nid,
            )

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
        if p < 0.3:
            return set()
        elif p < 0.5:
            return {0}
        elif p < 0.7:
            return {0, 2}
        else:
            return {0, 2, 5}
