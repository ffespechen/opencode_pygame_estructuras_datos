"""Animación visual para AVL Tree (árbol binario balanceado)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation


class AvlAnimation(BaseAnimation):
    """Muestra inserción, factores de balance y rotaciones LL/RR en un AVL."""

    def __init__(self) -> None:
        super().__init__()
        self.actions = [
            ("Insertar 30 → desbalanceo (BF=+2)", 5.0),
            ("Rotación simple derecha (LL)", 5.0),
            ("Insertar 70 → desbalanceo (BF=-2)", 5.0),
            ("Rotación simple izquierda (RR)", 5.0),
        ]

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.action_index == 0:
            self._draw_insert_ll_imbalance(surface, rect)
        elif self.action_index == 1:
            self._draw_rotate_right(surface, rect)
        elif self.action_index == 2:
            self._draw_insert_rr_imbalance(surface, rect)
        elif self.action_index == 3:
            self._draw_rotate_left(surface, rect)

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
        # Cadena 50 <- 40 <- 30 (desbalance LL en 50)
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
            # Antes: 50-40-30
            self._edge(surface, (cx + 40, y1), (cx - 20, y2))
            self._edge(surface, (cx - 20, y2), (cx - 80, y3))
            self._node(surface, cx + 40, y1, "50", bf="+2", highlight=True)
            self._node(surface, cx - 20, y2, "40", bf="+1")
            self._node(surface, cx - 80, y3, "30", bf="0")
            self._hint(surface, rect, "Rotación derecha sobre 50…")
        else:
            # Después: 40 con hijos 30 y 50
            self._edge(surface, (cx, y1), (cx - 90, y2))
            self._edge(surface, (cx, y1), (cx + 90, y2))
            self._node(surface, cx, y1, "40", bf="0", highlight=True)
            self._node(surface, cx - 90, y2, "30", bf="0")
            self._node(surface, cx + 90, y2, "50", bf="0")
            self._hint(surface, rect, "Equilibrado: 40 es nueva raíz local")

    def _draw_insert_rr_imbalance(
        self, surface: pygame.Surface, rect: pygame.Rect
    ) -> None:
        # Partimos del AVL balanceado 40(30,50) e insertamos 70 → RR en 40? 
        # Mejor: mostrar 40-50-70 cadena derecha
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
            # Resultado: 50 raíz, 40 izq (30), 70 der
            self._edge(surface, (cx, y1), (cx - 100, y2))
            self._edge(surface, (cx, y1), (cx + 100, y2))
            self._edge(surface, (cx - 100, y2), (cx - 160, y2 + 55))
            self._node(surface, cx, y1, "50", bf="0", highlight=True)
            self._node(surface, cx - 100, y2, "40", bf="+1")
            self._node(surface, cx + 100, y2, "70", bf="0")
            self._node(surface, cx - 160, y2 + 55, "30", bf="0")
            self._hint(surface, rect, "Equilibrado tras rotación RR")
