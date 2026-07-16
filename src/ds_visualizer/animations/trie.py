"""Animación visual para Trie (árbol de prefijos)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation


class TrieAnimation(BaseAnimation):
    """Muestra un trie con inserción de palabras, búsqueda de prefijo y borrado."""

    def __init__(self) -> None:
        super().__init__()
        # Estructura fija: ROOT -> C -> A -> T* / R*
        # Tras insertar "CAT" y "CAR"
        self.actions = [
            ("Insertar palabra: CAT", 5.0),
            ("Insertar palabra: CAR (prefijo CA)", 5.0),
            ("Buscar prefijo: CA", 5.0),
            ("Eliminar palabra: CAT", 5.0),
        ]

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.action_index == 0:
            self._draw_insert_cat(surface, rect)
        elif self.action_index == 1:
            self._draw_insert_car(surface, rect)
        elif self.action_index == 2:
            self._draw_search_prefix(surface, rect)
        elif self.action_index == 3:
            self._draw_delete_cat(surface, rect)

    def _layout(self, rect: pygame.Rect) -> dict[str, tuple[int, int]]:
        cx = rect.centerx
        top = rect.y + 36
        mid = rect.y + rect.height // 2 - 10
        bot = rect.y + rect.height - 70
        return {
            "ROOT": (cx, top),
            "C": (cx, top + (mid - top) // 2 + 10),
            "A": (cx, mid),
            "T": (cx - 70, bot),
            "R": (cx + 70, bot),
        }

    def _draw_node(
        self,
        surface: pygame.Surface,
        pos: tuple[int, int],
        label: str,
        highlight: bool = False,
        end_mark: bool = False,
        alpha: int = 255,
        radius: int = 20,
    ) -> None:
        x, y = pos
        fg = config.HIGHLIGHT_COLOR if highlight else config.TEXT_COLOR
        border = fg

        if alpha < 255:
            temp = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            cx, cy = radius + 2, radius + 2
            pygame.draw.circle(temp, (*config.CODE_BG, alpha), (cx, cy), radius)
            pygame.draw.circle(temp, (*border, alpha), (cx, cy), radius, width=2)
            lbl = self._font.render(label, True, (*fg, alpha))
            lbl_r = lbl.get_rect(center=(cx, cy))
            temp.blit(lbl, lbl_r)
            surface.blit(temp, (x - radius - 2, y - radius - 2))
        else:
            pygame.draw.circle(surface, config.CODE_BG, (x, y), radius)
            pygame.draw.circle(surface, border, (x, y), radius, width=2)
            lbl = self._font.render(label, True, fg)
            lbl_r = lbl.get_rect(center=(x, y))
            surface.blit(lbl, lbl_r)

        if end_mark:
            mark = self._font.render("*", True, config.ACCENT_COLOR)
            surface.blit(mark, (x + radius - 4, y - radius - 2))

    def _draw_edge(
        self,
        surface: pygame.Surface,
        p1: tuple[int, int],
        p2: tuple[int, int],
        highlight: bool = False,
        alpha: int = 255,
    ) -> None:
        color = config.HIGHLIGHT_COLOR if highlight else config.DIVIDER_COLOR
        if alpha < 255:
            # pygame line no soporta alpha directo; dibujar atenuado aproximado
            color = tuple(
                int(c * alpha / 255 + config.PANEL_BG[i] * (1 - alpha / 255))
                for i, c in enumerate(color)
            )
        pygame.draw.line(surface, color, p1, p2, width=2)

    def _draw_trie(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        nodes: set[str],
        ends: set[str],
        highlighted: set[str] | None = None,
        fading: dict[str, int] | None = None,
        words_label: str = "",
    ) -> None:
        highlighted = highlighted or set()
        fading = fading or {}
        pos = self._layout(rect)

        edges = [
            ("ROOT", "C"),
            ("C", "A"),
            ("A", "T"),
            ("A", "R"),
        ]
        for a, b in edges:
            if a in nodes and b in nodes:
                alpha = min(fading.get(a, 255), fading.get(b, 255))
                self._draw_edge(
                    surface,
                    pos[a],
                    pos[b],
                    highlight=a in highlighted or b in highlighted,
                    alpha=alpha,
                )

        for name in ("ROOT", "C", "A", "T", "R"):
            if name not in nodes:
                continue
            self._draw_node(
                surface,
                pos[name],
                name if name != "ROOT" else "·",
                highlight=name in highlighted,
                end_mark=name in ends,
                alpha=fading.get(name, 255),
                radius=18 if name == "ROOT" else 20,
            )

        if words_label:
            lbl = self._font.render(words_label, True, config.SUBTEXT_COLOR)
            surface.blit(lbl, lbl.get_rect(midbottom=(rect.centerx, rect.bottom - 8)))

    def _draw_insert_cat(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.25:
            self._draw_trie(surface, rect, {"ROOT"}, set(), words_label="palabras: (vacío)")
        elif p < 0.5:
            self._draw_trie(
                surface, rect, {"ROOT", "C"}, set(),
                highlighted={"C"}, words_label="insertando C…"
            )
        elif p < 0.75:
            self._draw_trie(
                surface, rect, {"ROOT", "C", "A"}, set(),
                highlighted={"A"}, words_label="insertando A…"
            )
        else:
            self._draw_trie(
                surface, rect, {"ROOT", "C", "A", "T"}, {"T"},
                highlighted={"T"}, words_label="palabras: CAT  (* = fin de palabra)"
            )

    def _draw_insert_car(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        base = {"ROOT", "C", "A", "T"}
        ends = {"T"}
        if p < 0.35:
            self._draw_trie(
                surface, rect, base, ends,
                highlighted={"C", "A"}, words_label="reutiliza prefijo CA…"
            )
        elif p < 0.65:
            self._draw_trie(
                surface, rect, base | {"R"}, ends,
                highlighted={"R"}, words_label="insertando R…"
            )
        else:
            self._draw_trie(
                surface, rect, base | {"R"}, {"T", "R"},
                highlighted={"R"}, words_label="palabras: CAT, CAR"
            )

    def _draw_search_prefix(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        nodes = {"ROOT", "C", "A", "T", "R"}
        ends = {"T", "R"}
        if p < 0.33:
            hl = {"C"}
            msg = "buscar 'CA': paso C"
        elif p < 0.66:
            hl = {"C", "A"}
            msg = "buscar 'CA': paso A"
        else:
            hl = {"C", "A", "T", "R"}
            msg = "prefijo 'CA' encontrado → CAT, CAR"
        self._draw_trie(surface, rect, nodes, ends, highlighted=hl, words_label=msg)

    def _draw_delete_cat(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        nodes = {"ROOT", "C", "A", "T", "R"}
        if p < 0.35:
            self._draw_trie(
                surface, rect, nodes, {"T", "R"},
                highlighted={"T"}, words_label="eliminar CAT: quitar marca *"
            )
        elif p < 0.7:
            fading = {"T": int(255 * (1.0 - (p - 0.35) / 0.35))}
            self._draw_trie(
                surface, rect, nodes, {"R"},
                highlighted={"T"}, fading=fading,
                words_label="nodo T sin hijos → se elimina"
            )
        else:
            self._draw_trie(
                surface, rect, {"ROOT", "C", "A", "R"}, {"R"},
                highlighted={"R"}, words_label="palabras: CAR"
            )
