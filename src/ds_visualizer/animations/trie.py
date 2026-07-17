"""Animación visual para Trie (árbol de prefijos)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import (
    AnimStep,
    BaseAnimation,
    Challenge,
    Operation,
)


_WORD_CYCLE = ["CAT", "CAR", "CAB", "DOG", "DOT"]


class TrieAnimation(BaseAnimation):
    """Muestra un trie con inserción de palabras, búsqueda de prefijo y borrado."""

    def __init__(self) -> None:
        super().__init__()
        self.words: set[str] = {"CAT", "CAR"}
        self._initial_words = set(self.words)
        self._word_idx = 0
        self._highlighted: set[str] = set()
        self.actions = [
            ("Insertar palabra: CAT", 5.0),
            ("Insertar palabra: CAR (prefijo CA)", 5.0),
            ("Buscar prefijo: CA", 5.0),
            ("Eliminar palabra: CAT", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Insert", "insert",
                prompt="Palabra:", example="DOG",
                complexity="O(L)",
            ),
            Operation(
                pygame.K_2, "Search", "search",
                prompt="Prefijo o palabra:", example="CA",
                complexity="O(L)", mutates=False,
            ),
            Operation(
                pygame.K_3, "Delete", "delete",
                prompt="Palabra:", example="CAT",
                complexity="O(L)",
            ),
        ])
        self.set_challenges([
            Challenge(
                "trie_dog", "Insertar DOG",
                "Insertá la palabra DOG.", "Insert → DOG",
                lambda a: "DOG" in a.words,
            ),
            Challenge(
                "trie_no_cat", "Sin CAT",
                "Eliminá CAT del trie.", "Delete → CAT",
                lambda a: "CAT" not in a.words,
            ),
        ])

    def reset(self) -> None:
        super().reset()
        self.words = set(self._initial_words)
        self._word_idx = 0
        self._highlighted = set()

    def build_steps(
        self, op_id: str, user_input: str | None = None
    ) -> list[AnimStep]:
        if op_id not in ("search", "insert", "delete"):
            return []
        text = (user_input or "").strip().upper()
        if not text or not text.isalpha():
            return []
        steps = []
        path: list[str] = ["ROOT"]
        seen: set[str] = {"ROOT"}
        steps.append(AnimStep(
            f"{op_id}: desde ROOT",
            highlight_ids=frozenset(seen),
            current_id="ROOT",
            note=f"1/{len(text) + 1} · Space=siguiente",
        ))
        for i, ch in enumerate(text):
            path.append(ch)
            seen.add(ch)
            edge_pairs = frozenset(
                (path[j], path[j + 1]) for j in range(len(path) - 1)
            )
            steps.append(AnimStep(
                f"{op_id}: seguir '{ch}'",
                highlight_ids=frozenset(seen),
                current_id=ch,
                edge_pairs=edge_pairs,
                note=f"{i + 2}/{len(text) + 1} · Space=siguiente",
            ))
        return steps

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "insert":
            word = (user_input or "").strip().upper()
            if not word or not word.isalpha():
                return "Indicá una palabra con letras (A-Z)"
            self.words.add(word)
            self._highlighted = set()
            return f"Insert '{word}'"
        if op_id == "search":
            prefix = (user_input or "").strip().upper()
            if not prefix or not prefix.isalpha():
                return "Indicá un prefijo o palabra (A-Z)"
            self._highlighted = set()
            found = sorted(w for w in self.words if w.startswith(prefix))
            return f"Search '{prefix}' → {found or '∅'}"
        if op_id == "delete":
            word = (user_input or "").strip().upper()
            if not word or not word.isalpha():
                return "Indicá una palabra (A-Z)"
            if word not in self.words:
                self._highlighted = set()
                return f"Delete '{word}': no está en el trie"
            self.words.remove(word)
            self._highlighted = set()
            return f"Delete '{word}'"
        return ""

    def _word_path(self, word: str) -> set[str]:
        nodes = {"ROOT"}
        for ch in word:
            nodes.add(ch)
        return nodes

    def _prefix_path(self, prefix: str) -> set[str]:
        nodes = {"ROOT"}
        for ch in prefix:
            nodes.add(ch)
        return nodes

    def _derive_structure(
        self, words: set[str],
    ) -> tuple[set[str], set[str], list[tuple[str, str]]]:
        nodes: set[str] = {"ROOT"}
        ends: set[str] = set()
        edges: list[tuple[str, str]] = []
        for word in sorted(words):
            prev = "ROOT"
            for ch in word:
                nodes.add(ch)
                edges.append((prev, ch))
                prev = ch
            ends.add(prev)
        return nodes, ends, edges

    def _dynamic_layout(
        self, nodes: set[str], edges: list[tuple[str, str]], rect: pygame.Rect,
    ) -> dict[str, tuple[int, int]]:
        if not nodes:
            return {}
        children: dict[str, list[str]] = {}
        for parent, child in edges:
            children.setdefault(parent, []).append(child)

        levels: dict[str, int] = {"ROOT": 0}
        queue = ["ROOT"]
        while queue:
            cur = queue.pop(0)
            for ch in children.get(cur, []):
                if ch not in levels:
                    levels[ch] = levels[cur] + 1
                    queue.append(ch)

        by_level: dict[int, list[str]] = {}
        for name, lv in levels.items():
            by_level.setdefault(lv, []).append(name)

        max_level = max(by_level.keys()) if by_level else 0
        pos: dict[str, tuple[int, int]] = {}
        v_step = (rect.height - 100) // max(max_level, 1)
        for lv in range(max_level + 1):
            row = by_level.get(lv, [])
            n = len(row)
            h_step = rect.width // (n + 1)
            y = rect.y + 36 + lv * v_step
            for i, name in enumerate(row):
                x = rect.x + (i + 1) * h_step
                pos[name] = (x, y)
        return pos

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.interactive:
            nodes, ends, edges = self._derive_structure(self.words)
            pos = self._dynamic_layout(nodes, edges, rect)
            highlighted = set(self._highlighted)
            current: str | None = None
            path_edges: set[tuple[str, str]] = set()
            if self.step_mode:
                highlighted = set(self.highlight_ids)
                current = self.focus_id or None
                path_edges = {
                    (a, b) for a, b in self.step_edges
                    if isinstance(a, str) and isinstance(b, str)
                }
            elif self.live_op in ("insert", "search", "delete"):
                p = self.live_progress()
                hl_list = sorted(highlighted) if highlighted else ["ROOT"]
                count = max(1, int(p * len(hl_list)))
                count = min(count, len(hl_list))
                highlighted = set(hl_list[:count])
                current = hl_list[count - 1]
            self._draw_trie_dynamic(
                surface, rect, nodes, ends, edges, pos, highlighted,
                current=current, path_edges=path_edges,
                words_label=f"palabras: {', '.join(sorted(self.words)) or '(vacío)'}",
            )
            return

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
        role: str | None = None,
    ) -> None:
        x, y = pos
        if role is None:
            role = "visited" if highlight else "plain"
        fg = self.color_for_role(role)
        border = fg
        width = 3 if role == "current" else 2

        if alpha < 255:
            temp = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            cx, cy = radius + 2, radius + 2
            pygame.draw.circle(temp, (*config.CODE_BG, alpha), (cx, cy), radius)
            pygame.draw.circle(temp, (*border, alpha), (cx, cy), radius, width=width)
            lbl = self._font.render(label, True, (*fg, alpha))
            lbl_r = lbl.get_rect(center=(cx, cy))
            temp.blit(lbl, lbl_r)
            surface.blit(temp, (x - radius - 2, y - radius - 2))
        else:
            pygame.draw.circle(surface, config.CODE_BG, (x, y), radius)
            pygame.draw.circle(surface, border, (x, y), radius, width=width)
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
        path: bool = False,
    ) -> None:
        if path:
            color = config.PATH_EDGE_COLOR
            width = 3
        elif highlight:
            color = config.VISITED_COLOR
            width = 2
        else:
            color = config.DIVIDER_COLOR
            width = 2
        if alpha < 255:
            color = tuple(
                int(c * alpha / 255 + config.PANEL_BG[i] * (1 - alpha / 255))
                for i, c in enumerate(color)
            )
        pygame.draw.line(surface, color, p1, p2, width=width)

    def _draw_trie_dynamic(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        nodes: set[str],
        ends: set[str],
        edges: list[tuple[str, str]],
        pos: dict[str, tuple[int, int]],
        highlighted: set[str] | None = None,
        words_label: str = "",
        current: str | None = None,
        path_edges: set[tuple[str, str]] | None = None,
    ) -> None:
        highlighted = highlighted or set()
        path_edges = path_edges or set()
        for a, b in edges:
            if a in pos and b in pos:
                self._draw_edge(
                    surface, pos[a], pos[b],
                    highlight=a in highlighted or b in highlighted,
                    path=(a, b) in path_edges or (b, a) in path_edges,
                )
        for name in nodes:
            if name not in pos:
                continue
            if current and name == current:
                role = "current"
            elif name in highlighted:
                role = "visited"
            else:
                role = "plain"
            self._draw_node(
                surface, pos[name],
                name if name != "ROOT" else "·",
                highlight=name in highlighted,
                end_mark=name in ends,
                radius=18 if name == "ROOT" else 20,
                role=role,
            )
            x, y = pos[name]
            r = 18 if name == "ROOT" else 20
            hit = pygame.Rect(x - r, y - r, r * 2, r * 2)
            self.register_hit(
                f"trie:{name}", hit, label=name, value=name, key=name,
            )
        if words_label:
            lbl = self._font.render(words_label, True, config.SUBTEXT_COLOR)
            surface.blit(lbl, lbl.get_rect(midbottom=(rect.centerx, rect.bottom - 8)))

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
