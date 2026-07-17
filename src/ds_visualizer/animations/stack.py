"""Animación visual para Stack / Pila (LIFO) — tope arriba."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import (
    AnimStep,
    BaseAnimation,
    Challenge,
    HitTarget,
    Operation,
)


class StackAnimation(BaseAnimation):
    """Muestra una pila vertical con el tope en la parte superior."""

    def __init__(self) -> None:
        super().__init__()
        self.base_values = [55, 23, 78, 41]
        self._initial = list(self.base_values)
        self.values = list(self._initial)
        self.actions = [
            ("Push: apilando elemento (99)", 5.0),
            ("Peek: consultando tope", 5.0),
            ("Pop: desapilando elemento", 5.0),
            ("Push: apilando elemento (33)", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Push", "push",
                prompt="Valor a apilar:", example="99",
                complexity="O(1)",
            ),
            Operation(
                pygame.K_2, "Peek", "peek",
                complexity="O(1)", mutates=False,
            ),
            Operation(
                pygame.K_3, "Pop", "pop",
                complexity="O(1)",
            ),
        ])
        self.set_challenges([
            Challenge(
                "stack_empty",
                "Vaciar la pila",
                "Hacé Pop hasta dejar la pila vacía.",
                "Pop quita el TOPE (último en entrar).",
                lambda a: len(a.values) == 0,
            ),
            Challenge(
                "stack_top_1",
                "Tope = 1",
                "Dejá el valor 1 en el tope de la pila.",
                "Push 1 (o Pop hasta poder Push 1 arriba).",
                lambda a: bool(a.values) and a.values[-1] == 1,
            ),
        ])

    def reset(self) -> None:
        super().reset()
        self.values = list(self._initial)

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "push":
            v = self.parse_int(user_input or "")
            if v is None:
                return "Ingresá un número entero"
            self.values.append(v)
            self.highlight_idx = len(self.values) - 1
            return f"Push {v}"
        if op_id == "peek":
            if not self.values:
                self.highlight_idx = -1
                return "Pila vacía"
            self.highlight_idx = len(self.values) - 1
            return f"Peek → {self.values[-1]}"
        if op_id == "pop":
            if not self.values:
                self.highlight_idx = -1
                return "Pila vacía"
            removed = self.values.pop()
            self.highlight_idx = len(self.values) - 1 if self.values else -1
            return f"Pop {removed}"
        return ""

    def build_steps(
        self, op_id: str, user_input: str | None = None
    ) -> list[AnimStep]:
        if op_id == "peek" and self.values:
            return [
                AnimStep("Mirar TOPE (LIFO)", highlight_idx=len(self.values) - 1,
                         note="O(1)"),
            ]
        if op_id == "pop" and self.highlight_idx >= -1:
            # Tras pop, mostrar mensaje único
            return [
                AnimStep("Remover TOPE", note="O(1)"),
            ]
        return []

    def on_drop(self, source_id: str, dest: HitTarget | None) -> str:
        # Soltar sobre la pila desde un elemento = no-op pedagógico
        return ""

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
            self._draw_push(surface, rect, 99)
        elif self.action_index == 1:
            self._draw_peek(surface, rect)
        elif self.action_index == 2:
            self._draw_pop(surface, rect)
        elif self.action_index == 3:
            self._draw_push(surface, rect, 33)

    def _draw_interactive(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if not self.values:
            self.draw_empty(surface, rect, "(pila vacía)")
            return
        highlight_top = (
            self.live_op == "peek"
            or self.live_op == "push"
            or self.live_op == "pop"
            or self.highlight_idx == len(self.values) - 1
        )
        self._draw_stack(
            surface, rect, self.values,
            highlight_top=highlight_top, register=True,
        )

    def _stack_center_y(self, rect: pygame.Rect, n: int,
                        box_h: int = 38, gap: int = 4) -> float:
        total_height = n * box_h + (n - 1) * gap
        return rect.y + (rect.height - total_height) // 2

    def _draw_box(
        self, surface: pygame.Surface, rect: pygame.Rect,
        bx: float, by: float, box_w: int, box_h: int,
        val: int, highlight: bool, alpha: int = 255,
        register_id: str | None = None, register_label: str = "",
        register_index: int | None = None,
    ) -> None:
        box_rect = pygame.Rect(int(bx), int(by), box_w, box_h)

        fg = config.HIGHLIGHT_COLOR if highlight else config.TEXT_COLOR
        border = fg

        temp_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        temp_surf.fill((*config.CODE_BG, alpha))
        border_rect = pygame.Rect(0, 0, box_w, box_h)
        pygame.draw.rect(temp_surf, (*border, alpha),
                         border_rect, width=2, border_radius=4)

        val_surf = self._font.render(str(val), True, (*fg, alpha))
        val_r = val_surf.get_rect(center=(box_w // 2, box_h // 2))
        temp_surf.blit(val_surf, val_r)
        surface.blit(temp_surf, box_rect)

        if register_id is not None and alpha > 200:
            meta = {"value": val, "draggable": True}
            if register_index is not None:
                meta["index"] = register_index
            self.register_hit(
                register_id, box_rect, label=register_label or str(val), **meta
            )

    def _draw_stack(
        self, surface: pygame.Surface, rect: pygame.Rect,
        values: list[int], highlight_top: bool = False,
        register: bool = False,
    ) -> None:
        box_w, box_h = 100, 38
        gap = 4
        n = len(values)
        start_y = self._stack_center_y(rect, n, box_h, gap)
        cx = rect.x + rect.width // 2 - box_w // 2

        for i in range(n):
            val = values[n - 1 - i]
            by = start_y + i * (box_h + gap)
            is_top = i == 0
            idx = n - 1 - i
            self._draw_box(
                surface, rect, cx, by, box_w, box_h,
                val, is_top and highlight_top,
                register_id=f"idx:{idx}" if register else None,
                register_label=f"[{idx}]={val}" + (" TOPE" if is_top else ""),
                register_index=idx,
            )

        if n > 0:
            lbl_surf = self._font.render("TOPE →", True, config.ACCENT_COLOR)
            lbl_y = start_y + box_h // 2
            lbl_rect = lbl_surf.get_rect(
                midleft=(rect.x + rect.width // 2 + box_w // 2 + 12, lbl_y)
            )
            surface.blit(lbl_surf, lbl_rect)

    def _draw_push(self, surface: pygame.Surface, rect: pygame.Rect,
                   value: int) -> None:
        box_w, box_h = 100, 38
        gap = 4
        p = self.progress()
        n = len(self.base_values)
        start_y = self._stack_center_y(rect, n, box_h, gap)
        cx = rect.x + rect.width // 2 - box_w // 2

        if p < 0.4:
            self._draw_stack(surface, rect, self.base_values)
            alpha = int(255 * (p / 0.4))
            float_y = start_y - box_h - gap - int((1 - p / 0.4) * 30)
            self._draw_box(surface, rect, cx, float_y, box_w, box_h,
                           value, True, alpha)
        elif p < 0.7:
            full = list(self.base_values) + [value]
            self._draw_stack(surface, rect, full, highlight_top=True)
        else:
            self._draw_stack(surface, rect,
                             self.base_values + [value], highlight_top=True)

    def _draw_peek(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        self._draw_stack(surface, rect, self.base_values, highlight_top=True)

    def _draw_pop(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        box_w, box_h = 100, 38
        gap = 4
        p = self.progress()
        remaining = self.base_values[:-1]
        start_y = self._stack_center_y(rect, len(remaining), box_h, gap)
        cx = rect.x + rect.width // 2 - box_w // 2

        if p < 0.2:
            self._draw_stack(surface, rect, self.base_values,
                             highlight_top=True)
        elif p < 0.6:
            self._draw_stack(surface, rect, remaining)
            top_val = self.base_values[-1]
            alpha = int(255 * (1.0 - (p - 0.2) / 0.4))
            slide_progress = (p - 0.2) / 0.4
            top_y = (start_y - box_h - gap
                     - int(slide_progress * (box_h + 20)))
            self._draw_box(surface, rect, cx, top_y, box_w, box_h,
                           top_val, True, max(alpha, 20))
        else:
            self._draw_stack(surface, rect, remaining)
