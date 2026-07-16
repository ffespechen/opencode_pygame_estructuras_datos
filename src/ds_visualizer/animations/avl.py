"""Animación visual para AVL Tree (árbol binario balanceado)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation, Operation


class AvlAnimation(BaseAnimation):
    """Muestra inserción, factores de balance y rotaciones LL/RR en un AVL."""

    def __init__(self) -> None:
        super().__init__()
        self.values = [50, 40, 60]
        self._initial_values = list(self.values)
        self._last_inserted: int | None = None
        self._highlight_idx = -1
        self.actions = [
            ("Insertar 30 → desbalanceo (BF=+2)", 5.0),
            ("Rotación simple derecha (LL)", 5.0),
            ("Insertar 70 → desbalanceo (BF=-2)", 5.0),
            ("Rotación simple izquierda (RR)", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Insert", "insert",
                prompt="Valor:", example="30",
            ),
            Operation(
                pygame.K_2, "Delete", "delete",
                prompt="Valor a eliminar:", example="40",
            ),
        ])

    def reset(self) -> None:
        super().reset()
        self.values = list(self._initial_values)
        self._last_inserted = None
        self._highlight_idx = -1

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "insert":
            val = self.parse_int(user_input or "")
            if val is None:
                return "Indicá un número entero"
            self.values = sorted(self.values + [val])
            self._last_inserted = val
            self._highlight_idx = self.values.index(val)
            return f"Insert {val} (ordenado / BST simplificado)"
        if op_id == "delete":
            val = self.parse_int(user_input or "")
            if val is None:
                return "Indicá un número entero"
            if val not in self.values:
                self._highlight_idx = -1
                return f"Delete {val}: no está en el árbol"
            self.values.remove(val)
            if self._last_inserted == val:
                self._last_inserted = None
            self._highlight_idx = -1
            return f"Delete {val}"
        return ""

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            self._draw_interactive(surface, rect)
            return

        if self.action_index == 0:
            self._draw_insert_ll_imbalance(surface, rect)
        elif self.action_index == 1:
            self._draw_rotate_right(surface, rect)
        elif self.action_index == 2:
            self._draw_insert_rr_imbalance(surface, rect)
        elif self.action_index == 3:
            self._draw_rotate_left(surface, rect)

    def _draw_interactive(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        n = len(self.values)
        if n == 0:
            return
        spacing = min(70, (rect.width - 40) // max(n, 1))
        total_w = n * spacing
        start_x = rect.centerx - total_w // 2 + spacing // 2
        y = rect.centery

        for i, val in enumerate(self.values):
            x = start_x + i * spacing
            highlight = i == self._highlight_idx
            self._node(surface, x, y, str(val), highlight=highlight)

        self._hint(surface, rect, "AVL interactivo (inserción)")

    def _node(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        value: str,
        bf: str | None = None,
        highlight: bool = False,
        radius: int = 22,
    ) -> None:
        fg = config.HIGHLIGHT_COLOR if highlight else config.TEXT_COLOR
        pygame.draw.circle(surface, config.CODE_BG, (x, y), radius)
        pygame.draw.circle(surface, fg, (x, y), radius, width=2)
        lbl = self._font.render(value, True, fg)
        surface.blit(lbl, lbl.get_rect(center=(x, y)))
        if bf is not None:
            bf_color = (
                config.HIGHLIGHT_COLOR
                if bf in ("+2", "-2", "2", "-2")
                else config.ACCENT_COLOR
            )
            bf_surf = self._font.render(f"BF{bf}", True, bf_color)
            surface.blit(bf_surf, bf_surf.get_rect(midbottom=(x, y - radius - 2)))

    def _edge(
        self,
        surface: pygame.Surface,
        a: tuple[int, int],
        b: tuple[int, int],
        highlight: bool = False,
    ) -> None:
        color = config.HIGHLIGHT_COLOR if highlight else config.DIVIDER_COLOR
        pygame.draw.line(surface, color, a, b, width=2)

    def _hint(self, surface: pygame.Surface, rect: pygame.Rect, text: str) -> None:
        lbl = self._font.render(text, True, config.SUBTEXT_COLOR)
        surface.blit(lbl, lbl.get_rect(midbottom=(rect.centerx, rect.bottom - 8)))

    def _draw_insert_ll_imbalance(
        self, surface: pygame.Surface, rect: pygame.Rect
    ) -> None:
        p = self.progress()
        cx = rect.centerx
        y1, y2, y3 = rect.y + 50, rect.y + rect.height // 2, rect.y + rect.height - 80

        if p < 0.35:
            self._node(surface, cx, y1, "50", bf="0")
            self._hint(surface, rect, "AVL inicial: solo raíz 50")
        elif p < 0.65:
            self._edge(surface, (cx, y1), (cx - 80, y2))
            self._node(surface, cx, y1, "50", bf="+1")
            self._node(surface, cx - 80, y2, "40", bf="0", highlight=True)
            self._hint(surface, rect, "Insertar 40 (hijo izquierdo)")
        else:
            self._edge(surface, (cx, y1), (cx - 80, y2), highlight=True)
            self._edge(surface, (cx - 80, y2), (cx - 140, y3), highlight=True)
            self._node(surface, cx, y1, "50", bf="+2", highlight=True)
            self._node(surface, cx - 80, y2, "40", bf="+1")
            self._node(surface, cx - 140, y3, "30", bf="0", highlight=True)
            self._hint(surface, rect, "Desbalance LL: BF(+2) en 50")

    def _draw_rotate_right(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        cx = rect.centerx
        y1 = rect.y + 55
        y2 = rect.y + rect.height // 2
        y3 = rect.y + rect.height - 75

        if p < 0.45:
            self._edge(surface, (cx + 40, y1), (cx - 20, y2))
            self._edge(surface, (cx - 20, y2), (cx - 80, y3))
            self._node(surface, cx + 40, y1, "50", bf="+2", highlight=True)
            self._node(surface, cx - 20, y2, "40", bf="+1")
            self._node(surface, cx - 80, y3, "30", bf="0")
            self._hint(surface, rect, "Rotación derecha sobre 50…")
        else:
            self._edge(surface, (cx, y1), (cx - 90, y2))
            self._edge(surface, (cx, y1), (cx + 90, y2))
            self._node(surface, cx, y1, "40", bf="0", highlight=True)
            self._node(surface, cx - 90, y2, "30", bf="0")
            self._node(surface, cx + 90, y2, "50", bf="0")
            self._hint(surface, rect, "Equilibrado: 40 es nueva raíz local")

    def _draw_insert_rr_imbalance(
        self, surface: pygame.Surface, rect: pygame.Rect
    ) -> None:
        p = self.progress()
        cx = rect.centerx
        y1, y2, y3 = rect.y + 50, rect.y + rect.height // 2, rect.y + rect.height - 80

        if p < 0.4:
            self._edge(surface, (cx, y1), (cx - 90, y2))
            self._edge(surface, (cx, y1), (cx + 90, y2))
            self._node(surface, cx, y1, "40", bf="0")
            self._node(surface, cx - 90, y2, "30", bf="0")
            self._node(surface, cx + 90, y2, "50", bf="0", highlight=True)
            self._hint(surface, rect, "AVL equilibrado; insertar 70…")
        else:
            self._edge(surface, (cx, y1), (cx - 90, y2))
            self._edge(surface, (cx, y1), (cx + 70, y2), highlight=True)
            self._edge(surface, (cx + 70, y2), (cx + 130, y3), highlight=True)
            self._node(surface, cx, y1, "40", bf="-2", highlight=True)
            self._node(surface, cx - 90, y2, "30", bf="0")
            self._node(surface, cx + 70, y2, "50", bf="-1")
            self._node(surface, cx + 130, y3, "70", bf="0", highlight=True)
            self._hint(surface, rect, "Desbalance RR: BF(-2) en 40")

    def _draw_rotate_left(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        cx = rect.centerx
        y1 = rect.y + 55
        y2 = rect.y + rect.height // 2 + 10

        if p < 0.45:
            self._edge(surface, (cx - 40, y1), (cx - 130, y2))
            self._edge(surface, (cx - 40, y1), (cx + 40, y2), highlight=True)
            self._edge(surface, (cx + 40, y2), (cx + 110, y2 + 50), highlight=True)
            self._node(surface, cx - 40, y1, "40", bf="-2", highlight=True)
            self._node(surface, cx - 130, y2, "30", bf="0")
            self._node(surface, cx + 40, y2, "50", bf="-1")
            self._node(surface, cx + 110, y2 + 50, "70", bf="0")
            self._hint(surface, rect, "Rotación izquierda sobre 40…")
        else:
            self._edge(surface, (cx, y1), (cx - 100, y2))
            self._edge(surface, (cx, y1), (cx + 100, y2))
            self._edge(surface, (cx - 100, y2), (cx - 160, y2 + 55))
            self._node(surface, cx, y1, "50", bf="0", highlight=True)
            self._node(surface, cx - 100, y2, "40", bf="+1")
            self._node(surface, cx + 100, y2, "70", bf="0")
            self._node(surface, cx - 160, y2 + 55, "30", bf="0")
            self._hint(surface, rect, "Equilibrado tras rotación RR")
