"""Animación visual para Priority Queue (cola de prioridad)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import (
    AnimStep,
    BaseAnimation,
    Challenge,
    Operation,
)


class PriorityQueueAnimation(BaseAnimation):
    """Cola ordenada por prioridad (vista lineal), distinta del heap como árbol."""

    _LABELS = "ABCDEFGHJKLMNPQRSTUVWXYZ"

    def __init__(self) -> None:
        super().__init__()
        self.base: list[tuple[int, str]] = [
            (1, "URG"),
            (3, "JOB"),
            (5, "LOG"),
            (8, "BAK"),
        ]
        self._initial = list(self.base)
        self.items = list(self._initial)
        self._label_idx = 0
        self.actions = [
            ("Enqueue: tarea (prio=2, NET)", 5.0),
            ("Peek: consultar máxima prioridad", 5.0),
            ("Dequeue: extraer máxima prioridad", 5.0),
            ("Enqueue: tarea (prio=4, SYNC)", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Enqueue", "enqueue",
                prompt="Prioridad y etiqueta:", example="2 NET",
                complexity="O(n)",
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
                "pq_empty",
                "Vaciar la cola",
                "Dequeue hasta vaciarla.",
                "Siempre sale el de menor prio (FRONT).",
                lambda a: len(a.items) == 0,
            ),
            Challenge(
                "pq_front_0",
                "FRONT prio = 0",
                "Enqueue algo con prioridad 0.",
                "Enqueue: 0 TOP",
                lambda a: bool(a.items) and a.items[0][0] == 0,
            ),
        ])

    def reset(self) -> None:
        super().reset()
        self.items = list(self._initial)
        self._label_idx = 0

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "enqueue":
            parsed = self.parse_prio_label(user_input or "")
            if parsed is None:
                return "Formato: prioridad y etiqueta (ej: 2 NET)"
            prio, label = parsed
            item = (prio, label)
            self.items.append(item)
            self.items.sort(key=lambda x: x[0])
            self.highlight_idx = self.items.index(item)
            return f"Enqueue (p={prio}, {label})"
        if op_id == "peek":
            if not self.items:
                self.highlight_idx = -1
                return "Cola vacía"
            self.highlight_idx = 0
            prio, label = self.items[0]
            return f"Peek → (p={prio}, {label})"
        if op_id == "dequeue":
            if not self.items:
                self.highlight_idx = -1
                return "Cola vacía"
            prio, label = self.items.pop(0)
            self.highlight_idx = 0 if self.items else -1
            return f"Dequeue (p={prio}, {label})"
        return ""

    def build_steps(
        self, op_id: str, user_input: str | None = None
    ) -> list[AnimStep]:
        if op_id == "peek" and self.items:
            prio, label = self.items[0]
            return [
                AnimStep(
                    f"FRONT = (p={prio}, {label})",
                    highlight_idx=0,
                    note="O(1)",
                ),
            ]
        if op_id == "dequeue":
            return [AnimStep("Extraer FRONT", highlight_idx=0, note="O(1)")]
        return []

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            self._draw_interactive(surface, rect)
            return

        if self.action_index == 0:
            self._draw_enqueue(surface, rect, (2, "NET"))
        elif self.action_index == 1:
            self._draw_items(surface, rect, self.base, highlight_idx=0)
            self._hint(surface, rect, "Peek → (1, URG)  |  menor prio = más urgente")
        elif self.action_index == 2:
            self._draw_dequeue(surface, rect)
        elif self.action_index == 3:
            self._draw_enqueue(surface, rect, (4, "SYNC"))

    def _draw_interactive(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if not self.items:
            self.draw_empty(surface, rect, "(cola vacía)")
            return
        highlight = self.highlight_idx
        if self.live_op in ("peek", "dequeue"):
            highlight = 0
        elif self.live_op == "enqueue" and self.highlight_idx >= 0:
            highlight = self.highlight_idx
        self._draw_items(
            surface, rect, self.items, highlight_idx=highlight, register=True,
        )
        self._hint(surface, rect, "Menor prio = más urgente (FRONT)")

    def _hint(self, surface: pygame.Surface, rect: pygame.Rect, text: str) -> None:
        lbl = self._font.render(text, True, config.SUBTEXT_COLOR)
        surface.blit(lbl, lbl.get_rect(midbottom=(rect.centerx, rect.bottom - 8)))

    def _draw_items(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        items: list[tuple[int, str]],
        highlight_idx: int = -1,
        fade_idx: int = -1,
        fade_alpha: int = 255,
        register: bool = False,
    ) -> None:
        n = len(items)
        if n == 0:
            return

        box_w, box_h = 88, 52
        gap = 12
        total_w = n * box_w + (n - 1) * gap
        start_x = rect.x + (rect.width - total_w) // 2
        base_y = rect.y + rect.height // 2 - box_h // 2 - 10

        title = self._font.render(
            "Priority Queue (min-priority al frente)", True, config.ACCENT_COLOR
        )
        surface.blit(title, title.get_rect(midtop=(rect.centerx, rect.y + 12)))

        for i, (prio, val) in enumerate(items):
            bx = start_x + i * (box_w + gap)
            alpha = fade_alpha if i == fade_idx else 255
            fg = (
                config.HIGHLIGHT_COLOR
                if i == highlight_idx
                else config.TEXT_COLOR
            )
            border = fg if i == highlight_idx else config.DIVIDER_COLOR

            temp = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            temp.fill((*config.CODE_BG, alpha))
            pygame.draw.rect(
                temp, (*border, alpha), temp.get_rect(), width=2, border_radius=5
            )
            p_surf = self._font.render(f"p={prio}", True, (*config.ACCENT_COLOR, alpha))
            v_surf = self._font.render(val, True, (*fg, alpha))
            temp.blit(p_surf, p_surf.get_rect(midtop=(box_w // 2, 6)))
            temp.blit(v_surf, v_surf.get_rect(midbottom=(box_w // 2, box_h - 6)))
            surface.blit(temp, (bx, base_y))

            if register and alpha > 200:
                cell = pygame.Rect(bx, base_y, box_w, box_h)
                self.register_hit(
                    f"idx:{i}", cell, label=f"p={prio} {val}",
                    index=i, value=prio, key=val,
                )

        if n > 0:
            front = self._font.render("FRONT", True, config.HIGHLIGHT_COLOR)
            surface.blit(
                front,
                front.get_rect(midtop=(start_x + box_w // 2, base_y + box_h + 6)),
            )

    def _sorted_with(
        self, item: tuple[int, str]
    ) -> list[tuple[int, str]]:
        result = list(self.base) + [item]
        result.sort(key=lambda x: x[0])
        return result

    def _draw_enqueue(
        self, surface: pygame.Surface, rect: pygame.Rect, item: tuple[int, str]
    ) -> None:
        p = self.progress()
        if p < 0.4:
            self._draw_items(surface, rect, self.base)
            self._hint(
                surface, rect,
                f"Enqueue ({item[0]}, {item[1]}) — insertar ordenado por prioridad"
            )
        else:
            display = self._sorted_with(item)
            idx = display.index(item)
            self._draw_items(surface, rect, display, highlight_idx=idx)
            self._hint(surface, rect, f"Insertado en posición según p={item[0]}")

    def _draw_dequeue(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.35:
            self._draw_items(surface, rect, self.base, highlight_idx=0)
            self._hint(surface, rect, "Dequeue: extraer el de mayor prioridad (FRONT)")
        elif p < 0.65:
            alpha = int(255 * (1.0 - (p - 0.35) / 0.3))
            self._draw_items(
                surface, rect, self.base, highlight_idx=0,
                fade_idx=0, fade_alpha=max(alpha, 20),
            )
            self._hint(surface, rect, "Extrayendo (1, URG)…")
        else:
            self._draw_items(surface, rect, self.base[1:], highlight_idx=0)
            self._hint(surface, rect, "Nuevo FRONT: (3, JOB)")
