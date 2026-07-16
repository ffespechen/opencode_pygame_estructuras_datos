"""Animación visual para Queue implementada con lista enlazada."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import (
    AnimStep,
    BaseAnimation,
    Challenge,
    Operation,
)


class QueueLinkedListAnimation(BaseAnimation):
    """Cola FIFO con FRONT en HEAD y REAR en TAIL de una lista enlazada."""

    def __init__(self) -> None:
        super().__init__()
        self.base_values = [12, 45, 67, 30]
        self._initial = list(self.base_values)
        self.values = list(self._initial)
        self.actions = [
            ("Enqueue: insertar en TAIL (88)", 5.0),
            ("Peek: consultar FRONT / HEAD", 5.0),
            ("Dequeue: eliminar HEAD", 5.0),
            ("Enqueue: insertar en TAIL (19)", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Enqueue", "enqueue",
                prompt="Valor a encolar:", example="88",
                complexity="O(1)",
            ),
            Operation(
                pygame.K_2, "Peek", "peek",
                complexity="O(1)", mutates=False,
            ),
            Operation(
                pygame.K_3, "Dequeue", "dequeue",
                complexity="O(1)",
            ),
        ])
        self.set_challenges([
            Challenge(
                "qll_empty",
                "Vaciar la cola",
                "Dequeue hasta dejarla vacía.",
                "Dequeue saca FRONT=HEAD.",
                lambda a: len(a.values) == 0,
            ),
            Challenge(
                "qll_front_7",
                "FRONT = 7",
                "Dejá el valor 7 al frente.",
                "Enqueue 7 y dequeue lo demás, o dequeue hasta 7.",
                lambda a: bool(a.values) and a.values[0] == 7,
            ),
        ])

    def reset(self) -> None:
        super().reset()
        self.values = list(self._initial)

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "enqueue":
            v = self.parse_int(user_input or "")
            if v is None:
                return "Ingresá un número entero"
            self.values.append(v)
            self.highlight_idx = len(self.values) - 1
            return f"Enqueue {v} en TAIL"
        if op_id == "peek":
            if not self.values:
                self.highlight_idx = -1
                return "Cola vacía"
            self.highlight_idx = 0
            return f"Peek → {self.values[0]}"
        if op_id == "dequeue":
            if not self.values:
                self.highlight_idx = -1
                return "Cola vacía"
            removed = self.values.pop(0)
            self.highlight_idx = 0 if self.values else -1
            return f"Dequeue {removed}"
        return ""

    def build_steps(
        self, op_id: str, user_input: str | None = None
    ) -> list[AnimStep]:
        if op_id == "peek" and self.values:
            return [
                AnimStep("Mirar FRONT=HEAD", highlight_idx=0, note="O(1)"),
            ]
        if op_id == "dequeue":
            return [AnimStep("Remover HEAD", note="O(1)")]
        return []

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            self._draw_interactive(surface, rect)
            return

        if self.action_index == 0:
            self._draw_enqueue(surface, rect, 88)
        elif self.action_index == 1:
            self._draw_nodes(
                surface, rect, self.base_values, highlight_front=True
            )
        elif self.action_index == 2:
            self._draw_dequeue(surface, rect)
        elif self.action_index == 3:
            self._draw_enqueue(surface, rect, 19)

    def _draw_interactive(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if not self.values:
            self.draw_empty(surface, rect, "(cola vacía)")
            return
        highlight_front = self.live_op in ("peek", "dequeue")
        highlight_rear = self.live_op == "enqueue"
        if not self.live_op:
            if self.highlight_idx == 0:
                highlight_front = True
            elif self.highlight_idx == len(self.values) - 1:
                highlight_rear = True
        self._draw_nodes(
            surface, rect, self.values,
            highlight_front=highlight_front,
            highlight_rear=highlight_rear,
            register=True,
        )

    def _draw_nodes(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        values: list[int],
        highlight_front: bool = False,
        highlight_rear: bool = False,
        fade_idx: int = -1,
        fade_alpha: int = 255,
        register: bool = False,
    ) -> None:
        n = len(values)
        if n == 0:
            return

        node_w, node_h = 70, 44
        gap = 18
        total_width = n * node_w + (n - 1) * gap
        start_x = rect.x + (rect.width - total_width) // 2
        base_y = rect.y + rect.height // 2 - node_h // 2

        for i, val in enumerate(values):
            nx = start_x + i * (node_w + gap)
            node_rect = pygame.Rect(nx, base_y, node_w, node_h)

            if i == 0 and highlight_front:
                fg = config.HIGHLIGHT_COLOR
                border = fg
            elif i == n - 1 and highlight_rear:
                fg = config.ACCENT_COLOR
                border = fg
            else:
                fg = config.TEXT_COLOR
                border = config.DIVIDER_COLOR

            alpha = fade_alpha if i == fade_idx else 255
            temp = pygame.Surface((node_w, node_h), pygame.SRCALPHA)
            temp.fill((*config.CODE_BG, alpha))
            pygame.draw.rect(
                temp, (*border, alpha), temp.get_rect(), width=2, border_radius=5
            )
            val_surf = self._font.render(str(val), True, (*fg, alpha))
            val_rect = val_surf.get_rect(center=temp.get_rect().center)
            temp.blit(val_surf, val_rect)
            surface.blit(temp, node_rect)

            if register and alpha > 200:
                self.register_hit(
                    f"idx:{i}", node_rect, label=f"[{i}]={val}",
                    index=i, value=val,
                )

            if i < n - 1:
                arrow_start = (nx + node_w + 2, base_y + node_h // 2)
                arrow_end = (nx + node_w + gap - 2, base_y + node_h // 2)
                arrow_color = config.DIVIDER_COLOR
                if (i == 0 and highlight_front) or (i == n - 2 and highlight_rear):
                    arrow_color = config.ACCENT_COLOR
                pygame.draw.line(surface, arrow_color, arrow_start, arrow_end, width=2)
                tip_l = (arrow_end[0] - 6, arrow_end[1] - 4)
                tip_r = (arrow_end[0] - 6, arrow_end[1] + 4)
                pygame.draw.polygon(surface, arrow_color, [arrow_end, tip_l, tip_r])

        front_surf = self._font.render("FRONT=HEAD", True, config.HIGHLIGHT_COLOR)
        frect = front_surf.get_rect(midtop=(start_x + node_w // 2, base_y - 22))
        surface.blit(front_surf, frect)

        rear_surf = self._font.render("REAR=TAIL", True, config.ACCENT_COLOR)
        rrect = rear_surf.get_rect(
            midtop=(start_x + (n - 1) * (node_w + gap) + node_w // 2, base_y - 22)
        )
        surface.blit(rear_surf, rrect)

        hint = self._font.render(
            "Queue vía lista enlazada: enqueue en TAIL, dequeue en HEAD",
            True,
            config.SUBTEXT_COLOR,
        )
        hint_rect = hint.get_rect(midbottom=(rect.centerx, rect.bottom - 8))
        surface.blit(hint, hint_rect)

    def _draw_enqueue(
        self, surface: pygame.Surface, rect: pygame.Rect, value: int
    ) -> None:
        p = self.progress()
        if p < 0.4:
            self._draw_nodes(surface, rect, self.base_values, highlight_rear=True)
        else:
            display = list(self.base_values) + [value]
            self._draw_nodes(surface, rect, display, highlight_rear=True)

    def _draw_dequeue(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.35:
            self._draw_nodes(surface, rect, self.base_values, highlight_front=True)
        elif p < 0.65:
            alpha = int(255 * (1.0 - (p - 0.35) / 0.3))
            self._draw_nodes(
                surface,
                rect,
                self.base_values,
                highlight_front=True,
                fade_idx=0,
                fade_alpha=max(alpha, 20),
            )
        else:
            self._draw_nodes(
                surface, rect, self.base_values[1:], highlight_front=True
            )
