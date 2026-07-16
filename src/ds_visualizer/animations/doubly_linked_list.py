"""Animación visual para Doubly Linked List (Lista Doblemente Enlazada)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import (
    AnimStep,
    BaseAnimation,
    Challenge,
    Operation,
)


class DoublyLinkedListAnimation(BaseAnimation):
    """Nodos con flechas bidireccionales: recorrido, inserción y eliminación."""

    def __init__(self) -> None:
        super().__init__()
        self._initial = [15, 42, 8, 73, 56]
        self.values = list(self._initial)
        self.actions = [
            ("Recorrido hacia adelante", 5.0),
            ("Recorrido hacia atrás", 5.0),
            ("Inserción en medio (valor=99)", 5.0),
            ("Eliminación de nodo (valor=73)", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Forward", "forward",
                complexity="O(n)", mutates=False,
            ),
            Operation(
                pygame.K_2, "Backward", "backward",
                complexity="O(n)", mutates=False,
            ),
            Operation(
                pygame.K_3, "Insert mid", "insert_middle",
                prompt="Valor:", example="99",
                complexity="O(n)",
            ),
            Operation(
                pygame.K_4, "Delete", "delete",
                prompt="Valor a eliminar:", example="73",
                complexity="O(n)", uses_selection=True,
            ),
        ])
        self.set_challenges([
            Challenge(
                "dll_head_0",
                "HEAD = 0",
                "Hacé que el primer nodo valga 0.",
                "Insert mid o borrá e insertá hasta que HEAD sea 0.",
                lambda a: bool(a.values) and a.values[0] == 0,
            ),
            Challenge(
                "dll_len_3",
                "Solo 3 nodos",
                "Dejá la lista con exactamente 3 nodos.",
                "Usá Delete (click + 4) hasta quedar con 3.",
                lambda a: len(a.values) == 3,
            ),
        ])

    def reset(self) -> None:
        super().reset()
        self.values = list(self._initial)

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "forward":
            self.highlight_idx = 0
            return "Recorrido hacia adelante"
        if op_id == "backward":
            n = len(self.values)
            self.highlight_idx = max(n - 1, 0)
            return "Recorrido hacia atrás"
        if op_id == "insert_middle":
            v = self.parse_int(user_input or "")
            if v is None:
                return "Ingresá un número entero"
            idx = len(self.values) // 2
            self.values.insert(idx, v)
            self.highlight_idx = idx
            return f"Insert {v} en posición {idx}"
        if op_id == "delete":
            v = self.parse_int(user_input or "")
            if v is None:
                return "Ingresá un número entero"
            if not self.values:
                self.highlight_idx = -1
                return "Lista vacía"
            try:
                idx = self.values.index(v)
            except ValueError:
                self.highlight_idx = -1
                return f"Valor {v} no encontrado"
            self.values.pop(idx)
            self.highlight_idx = -1
            return f"Delete {v}"
        return ""

    def build_steps(
        self, op_id: str, user_input: str | None = None
    ) -> list[AnimStep]:
        if op_id == "forward" and self.values:
            return [
                AnimStep(f"Adelante → nodo {i} = {v}", highlight_idx=i)
                for i, v in enumerate(self.values)
            ]
        if op_id == "backward" and self.values:
            n = len(self.values)
            return [
                AnimStep(
                    f"Atrás → nodo {i} = {self.values[i]}",
                    highlight_idx=i,
                )
                for i in range(n - 1, -1, -1)
            ]
        return []

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            self._draw_interactive(surface, rect)
            return

        if self.action_index == 0:
            self._draw_forward(surface, rect)
        elif self.action_index == 1:
            self._draw_backward(surface, rect)
        elif self.action_index == 2:
            self._draw_insert_middle(surface, rect)
        elif self.action_index == 3:
            self._draw_delete(surface, rect)

    def _draw_interactive(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        highlight = self.highlight_idx
        n = len(self.values)

        if self.live_op == "forward" and n > 0 and not self.step_mode:
            highlight = min(int(self.live_progress() * n), n - 1)
        elif self.live_op == "backward" and n > 0 and not self.step_mode:
            highlight = max(n - 1 - int(self.live_progress() * n), 0)

        if not self.values:
            self.draw_empty(surface, rect, "(lista vacía)")
            return
        self._draw_nodes(
            surface, rect, self.values, highlight_idx=highlight, register=True,
        )

    def _draw_nodes(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        values: list[int],
        highlight_idx: int = -1,
        show_labels: bool = True,
        register: bool = False,
    ) -> None:
        n = len(values)
        node_w, node_h = 70, 44
        gap = 28
        total_width = n * node_w + (n - 1) * gap
        start_x = rect.x + (rect.width - total_width) // 2
        base_y = rect.y + rect.height // 2 - node_h // 2

        for i, val in enumerate(values):
            nx = start_x + i * (node_w + gap)
            node_rect = pygame.Rect(nx, base_y, node_w, node_h)

            if i == highlight_idx:
                fg = config.HIGHLIGHT_COLOR
                border = fg
            else:
                fg = config.TEXT_COLOR
                border = config.DIVIDER_COLOR

            pygame.draw.rect(surface, config.CODE_BG, node_rect, border_radius=5)
            pygame.draw.rect(surface, border, node_rect, width=2, border_radius=5)

            text = "_" if val < 0 else str(val)
            val_surf = self._font.render(text, True, fg)
            val_rect = val_surf.get_rect(center=node_rect.center)
            surface.blit(val_surf, val_rect)

            if register and val >= 0:
                self.register_hit(
                    f"idx:{i}", node_rect, label=f"[{i}]={val}",
                    index=i, value=val,
                )

            if i < n - 1:
                fwd_y = base_y + node_h // 2 - 8
                arrow_start = (nx + node_w + 2, fwd_y)
                arrow_end = (nx + node_w + gap - 2, fwd_y)
                arrow_color = (
                    config.ACCENT_COLOR if i == highlight_idx else config.DIVIDER_COLOR
                )
                pygame.draw.line(surface, arrow_color, arrow_start, arrow_end, width=2)
                tip_l = (arrow_end[0] - 6, arrow_end[1] - 4)
                tip_r = (arrow_end[0] - 6, arrow_end[1] + 4)
                pygame.draw.polygon(surface, arrow_color, [arrow_end, tip_l, tip_r])

                back_y = base_y + node_h // 2 + 8
                back_start = (nx + node_w + gap - 2, back_y)
                back_end = (nx + node_w + 2, back_y)
                back_color = (
                    config.HIGHLIGHT_COLOR
                    if i + 1 == highlight_idx
                    else config.DIVIDER_COLOR
                )
                pygame.draw.line(surface, back_color, back_start, back_end, width=2)
                tip_l = (back_end[0] + 6, back_end[1] - 4)
                tip_r = (back_end[0] + 6, back_end[1] + 4)
                pygame.draw.polygon(surface, back_color, [back_end, tip_l, tip_r])

        if show_labels and n > 0:
            head_surf = self._font.render("HEAD", True, config.ACCENT_COLOR)
            head_rect = head_surf.get_rect(
                midtop=(start_x + node_w // 2, base_y - 22)
            )
            surface.blit(head_surf, head_rect)

            tail_surf = self._font.render("TAIL", True, config.HIGHLIGHT_COLOR)
            tail_rect = tail_surf.get_rect(
                midtop=(
                    start_x + (n - 1) * (node_w + gap) + node_w // 2,
                    base_y - 22,
                )
            )
            surface.blit(tail_surf, tail_rect)

    def _draw_forward(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.values)
        highlight = min(int(p * n), n - 1)
        self._draw_nodes(surface, rect, self.values, highlight_idx=highlight)

    def _draw_backward(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.values)
        highlight = max(n - 1 - int(p * n), 0)
        self._draw_nodes(surface, rect, self.values, highlight_idx=highlight)

    def _draw_insert_middle(
        self, surface: pygame.Surface, rect: pygame.Rect
    ) -> None:
        p = self.progress()
        insert_at = 2
        if p < 0.35:
            self._draw_nodes(surface, rect, self.values, highlight_idx=insert_at)
        elif p < 0.55:
            display = list(self.values)
            display.insert(insert_at, -1)
            self._draw_nodes(surface, rect, display, highlight_idx=insert_at)
        else:
            display = list(self.values)
            display.insert(insert_at, 99)
            self._draw_nodes(surface, rect, display, highlight_idx=insert_at)

    def _draw_delete(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        values = list(self.values)
        try:
            target_idx = values.index(73)
        except ValueError:
            target_idx = 3

        if p < 0.4:
            self._draw_nodes(surface, rect, values, highlight_idx=target_idx)
        else:
            values.pop(target_idx)
            self._draw_nodes(surface, rect, values)
