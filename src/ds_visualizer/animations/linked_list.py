"""Animación visual para Linked List (Lista Enlazada)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import (
    AnimStep,
    BaseAnimation,
    Challenge,
    Operation,
)


class LinkedListAnimation(BaseAnimation):
    """Muestra nodos enlazados con flechas, animando recorrido e inserciones."""

    def __init__(self) -> None:
        super().__init__()
        self._initial = [15, 42, 8, 73, 56]
        self.values = list(self._initial)
        self.actions = [
            ("Recorriendo nodos", 5.0),
            ("Inserción al inicio (valor=99)", 5.0),
            ("Inserción al final (valor=11)", 5.0),
            ("Eliminación de nodo (valor=73)", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Traverse", "traverse",
                complexity="O(n)", mutates=False,
            ),
            Operation(
                pygame.K_2, "Insert head", "insert_head",
                prompt="Valor:", example="99",
                complexity="O(1)",
            ),
            Operation(
                pygame.K_3, "Insert tail", "insert_tail",
                prompt="Valor:", example="99",
                complexity="O(n)",
            ),
            Operation(
                pygame.K_4, "Delete head", "delete_head",
                complexity="O(1)",
            ),
        ])
        self.set_challenges([
            Challenge(
                "ll_head_0",
                "HEAD = 0",
                "Hacé que el primer nodo valga 0.",
                "Insert head → 0.",
                lambda a: bool(a.values) and a.values[0] == 0,
            ),
        ])

    def reset(self) -> None:
        super().reset()
        self.values = list(self._initial)

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "traverse":
            self.highlight_idx = 0
            return "Recorriendo nodos"
        if op_id == "insert_head":
            v = self.parse_int(user_input or "")
            if v is None:
                return "Ingresá un número entero"
            self.values.insert(0, v)
            self.highlight_idx = 0
            return f"Insert head {v}"
        if op_id == "insert_tail":
            v = self.parse_int(user_input or "")
            if v is None:
                return "Ingresá un número entero"
            self.values.append(v)
            self.highlight_idx = len(self.values) - 1
            return f"Insert tail {v}"
        if op_id == "delete_head":
            if not self.values:
                self.highlight_idx = -1
                return "Lista vacía"
            removed = self.values.pop(0)
            self.highlight_idx = 0 if self.values else -1
            return f"Delete head {removed}"
        return ""

    def build_steps(
        self, op_id: str, user_input: str | None = None
    ) -> list[AnimStep]:
        if op_id == "traverse" and self.values:
            return [
                AnimStep(
                    f"Nodo {i} → {v}",
                    highlight_idx=i,
                    highlight_set=frozenset(range(i + 1)),
                    current_idx=i,
                    note=f"{i + 1}/{len(self.values)} · Space=siguiente",
                )
                for i, v in enumerate(self.values)
            ]
        return []

    def update(self, dt: float) -> None:
        super().update(dt)

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            self._draw_interactive(surface, rect)
            return

        if self.action_index == 0:
            self._draw_traverse(surface, rect)
        elif self.action_index == 1:
            self._draw_insert_head(surface, rect)
        elif self.action_index == 2:
            self._draw_insert_tail(surface, rect)
        elif self.action_index == 3:
            self._draw_delete(surface, rect)

    def _draw_interactive(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if not self.values:
            self.draw_empty(surface, rect, "(lista vacía)")
            return
        highlight = self.highlight_idx
        visited = set(self.highlight_set)
        if self.step_mode:
            highlight = self.focus_idx if self.focus_idx >= 0 else self.highlight_idx
            visited = set(self.highlight_set)
        elif self.live_op == "traverse":
            n = len(self.values)
            if n > 0:
                highlight = min(int(self.live_progress() * n), n - 1)
                visited = set(range(highlight + 1))
        self._draw_nodes(
            surface, rect, self.values,
            highlight_idx=highlight, visited=visited, register=True,
        )

    def _draw_nodes(
        self, surface: pygame.Surface, rect: pygame.Rect,
        values: list[int], highlight_idx: int = -1,
        show_head_label: bool = True, extra_node_alpha: float = 1.0,
        register: bool = False,
        visited: set[int] | None = None,
    ) -> None:
        n = len(values)
        node_w, node_h = 70, 44
        gap = 10
        total_width = n * node_w + (n - 1) * gap
        start_x = rect.x + (rect.width - total_width) // 2
        base_y = rect.y + rect.height // 2 - node_h // 2
        visited = visited or set()

        for i, val in enumerate(values):
            nx = start_x + i * (node_w + gap)
            node_rect = pygame.Rect(nx, base_y, node_w, node_h)

            if i == highlight_idx:
                role = "current"
            elif i in visited:
                role = "visited"
            else:
                role = "plain"
            fg = self.color_for_role(role)
            bg = config.CODE_BG
            border = fg

            pygame.draw.rect(surface, bg, node_rect, border_radius=5)
            pygame.draw.rect(
                surface, border, node_rect,
                width=3 if role == "current" else 2, border_radius=5,
            )

            if val < 0:
                text = "_"
            else:
                text = str(val)
            val_surf = self._font.render(text, True, fg)
            val_rect = val_surf.get_rect(center=node_rect.center)
            surface.blit(val_surf, val_rect)

            if register and val >= 0:
                self.register_hit(
                    f"idx:{i}", node_rect, label=f"[{i}]={val}",
                    index=i, value=val,
                )

            if i < n - 1:
                arrow_start = (nx + node_w + 2, base_y + node_h // 2)
                arrow_end = (nx + node_w + gap - 2, base_y + node_h // 2)
                if i < highlight_idx or (i in visited and i + 1 in visited):
                    arrow_color = config.PATH_EDGE_COLOR
                elif i == highlight_idx:
                    arrow_color = config.ACCENT_COLOR
                else:
                    arrow_color = config.DIVIDER_COLOR
                pygame.draw.line(surface, arrow_color, arrow_start, arrow_end, width=2)
                tip_left = (arrow_end[0] - 6, arrow_end[1] - 4)
                tip_right = (arrow_end[0] - 6, arrow_end[1] + 4)
                pygame.draw.polygon(surface, arrow_color, [arrow_end, tip_left, tip_right])

        if show_head_label and n > 0:
            head_surf = self._font.render("HEAD", True, config.ACCENT_COLOR)
            head_rect = head_surf.get_rect(
                midtop=(start_x + node_w // 2, base_y - 22)
            )
            surface.blit(head_surf, head_rect)

    def _draw_traverse(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.values)
        highlight = min(int(p * n), n - 1)
        self._draw_nodes(surface, rect, self.values, highlight_idx=highlight)

    def _draw_insert_head(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.4:
            self._draw_nodes(surface, rect, self.values, highlight_idx=0)
        elif p < 0.6:
            display_values = [-1] + list(self.values)
            self._draw_nodes(surface, rect, display_values, highlight_idx=0)
        else:
            display_values = [99] + list(self.values)
            self._draw_nodes(surface, rect, display_values, highlight_idx=0)

    def _draw_insert_tail(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.values)
        if p < 0.5:
            highlight = min(int(p * n / 0.5), n - 1)
            self._draw_nodes(surface, rect, self.values, highlight_idx=highlight)
        elif p < 0.7:
            self._draw_nodes(surface, rect, self.values, highlight_idx=n - 1)
        else:
            display_values = list(self.values) + [11]
            self._draw_nodes(surface, rect, display_values, highlight_idx=n)

    def _draw_delete(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        values = list(self.values)
        try:
            target_idx = values.index(73)
        except ValueError:
            target_idx = 3

        if p < 0.3:
            self._draw_nodes(surface, rect, values, highlight_idx=target_idx)
        elif p < 0.6:
            self._draw_nodes(surface, rect, values, highlight_idx=target_idx)
        else:
            values.pop(target_idx)
            self._draw_nodes(surface, rect, values)
