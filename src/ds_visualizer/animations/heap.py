"""Animación visual para Heap / Montículo (Min-Heap)."""

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation


class HeapAnimation(BaseAnimation):
    """Muestra un min-heap como árbol, animando inserción (bubble-up),
       extracción (bubble-down), heapify y peek."""

    def __init__(self) -> None:
        super().__init__()
        self.heap = [8, 15, 12, 30, 20, 25, 18]
        self.actions = [
            ("Inserción de 5: bubble-up", 5.0),
            ("Extracción del mínimo: bubble-down", 5.0),
            ("Peek: consulta del mínimo", 5.0),
            ("Heapify: convertir array en heap", 5.0),
        ]

    def update(self, dt: float) -> None:
        super().update(dt)

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)

        if self.action_index == 0:
            self._draw_insert(surface, rect)
        elif self.action_index == 1:
            self._draw_extract(surface, rect)
        elif self.action_index == 2:
            self._draw_peek(surface, rect)
        elif self.action_index == 3:
            self._draw_heapify(surface, rect)

    def _compute_positions(self, rect: pygame.Rect,
                           n: int) -> dict[int, tuple[int, int]]:
        positions: dict[int, tuple[int, int]] = {}
        if n == 0:
            return positions

        levels = {}
        for i in range(n):
            lv = 0
            idx = i + 1
            while idx > 1:
                idx //= 2
                lv += 1
            levels.setdefault(lv, []).append(i)

        max_level = max(levels.keys())
        v_spacing = (rect.height - 90) // (max_level + 1)
        for lv in range(max_level + 1):
            nodes = levels.get(lv, [])
            k = len(nodes)
            h_spacing = rect.width // (k + 1)
            y = rect.y + 45 + lv * v_spacing
            for j, nid in enumerate(nodes):
                x = rect.x + (j + 1) * h_spacing
                positions[nid] = (x, y)
        return positions

    def _draw_edges(self, surface: pygame.Surface,
                    positions: dict[int, tuple[int, int]],
                    n: int, highlighted: set[int]) -> None:
        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and i in positions and left in positions:
                color = (config.HIGHLIGHT_COLOR
                         if i in highlighted or left in highlighted
                         else config.DIVIDER_COLOR)
                pygame.draw.line(surface, color, positions[i],
                                 positions[left], width=2)
            if right < n and i in positions and right in positions:
                color = (config.HIGHLIGHT_COLOR
                         if i in highlighted or right in highlighted
                         else config.DIVIDER_COLOR)
                pygame.draw.line(surface, color, positions[i],
                                 positions[right], width=2)

    def _draw_nodes(self, surface: pygame.Surface,
                    positions: dict[int, tuple[int, int]],
                    values: list[int], highlighted: set[int]) -> None:
        radius = 20
        for i, (x, y) in positions.items():
            is_hl = i in highlighted
            fg = config.HIGHLIGHT_COLOR if is_hl else config.TEXT_COLOR
            border = fg
            bg = config.CODE_BG
            val = values[i]

            pygame.draw.circle(surface, bg, (x, y), radius)
            pygame.draw.circle(surface, border, (x, y), radius, width=2)

            val_surf = self._font.render(str(val), True, fg)
            vr = val_surf.get_rect(center=(x, y))
            surface.blit(val_surf, vr)

    def _draw_array_bar(self, surface: pygame.Surface, rect: pygame.Rect,
                        values: list[int],
                        highlight_indices: set[int]) -> None:
        n = len(values)
        if n == 0:
            return
        box_s = min(40, (rect.width - 40) // n - 6)
        total_w = n * box_s + (n - 1) * 6
        sx = rect.x + (rect.width - total_w) // 2
        sy = rect.y + rect.height - 38
        small = pygame.font.SysFont("monospace", 13, bold=True)

        for i, v in enumerate(values):
            bx = sx + i * (box_s + 6)
            br = pygame.Rect(int(bx), sy, box_s, box_s)
            is_hl = i in highlight_indices
            fg = config.HIGHLIGHT_COLOR if is_hl else config.TEXT_COLOR
            border = fg
            bg = config.CODE_BG

            pygame.draw.rect(surface, bg, br, border_radius=3)
            pygame.draw.rect(surface, border, br, width=1, border_radius=3)
            vs = small.render(str(v), True, fg)
            vr = vs.get_rect(center=br.center)
            surface.blit(vs, vr)

            idx_s = small.render(str(i), True, config.SUBTEXT_COLOR)
            ir = idx_s.get_rect(
                center=(br.centerx, sy - 12)
            )
            surface.blit(idx_s, ir)

    def _draw_insert(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.heap)

        if p < 0.3:
            positions = self._compute_positions(rect, n)
            self._draw_edges(surface, positions, n, set())
            self._draw_nodes(surface, positions, self.heap, set())
            self._draw_array_bar(surface, rect, self.heap, set())
        elif p < 0.6:
            new_heap = self.heap + [5]
            nn = n + 1
            positions = self._compute_positions(rect, nn)
            self._draw_edges(surface, positions, nn, {n})
            self._draw_nodes(surface, positions, new_heap, {n})
            self._draw_array_bar(surface, rect, new_heap, {n})
        else:
            result = [5, 8, 12, 30, 20, 25, 18, 15]
            positions = self._compute_positions(rect, len(result))
            self._draw_edges(surface, positions, len(result), {0, 1, 7})
            self._draw_nodes(surface, positions, result, {0, 1, 7})
            self._draw_array_bar(surface, rect, result, {0, 1, 7})

    def _draw_extract(self, surface: pygame.Surface,
                      rect: pygame.Rect) -> None:
        p = self.progress()
        n = len(self.heap)

        if p < 0.2:
            positions = self._compute_positions(rect, n)
            self._draw_edges(surface, positions, n, {0})
            self._draw_nodes(surface, positions, self.heap, {0})
            self._draw_array_bar(surface, rect, self.heap, {0})
        elif p < 0.5:
            positions = self._compute_positions(rect, n)
            self._draw_edges(surface, positions, n, {0, n - 1})
            swap = list(self.heap)
            swap[0], swap[-1] = swap[-1], swap[0]
            self._draw_nodes(surface, positions, swap, {0, n - 1})
            self._draw_array_bar(surface, rect, swap, {0, n - 1})
        else:
            result = [12, 15, 18, 30, 20, 25]
            positions = self._compute_positions(rect, len(result))
            hl = {0, 1, 2}
            self._draw_edges(surface, positions, len(result), hl)
            self._draw_nodes(surface, positions, result, hl)
            self._draw_array_bar(surface, rect, result, hl)

    def _draw_peek(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        n = len(self.heap)
        positions = self._compute_positions(rect, n)
        self._draw_edges(surface, positions, n, {0})
        self._draw_nodes(surface, positions, self.heap, {0})
        self._draw_array_bar(surface, rect, self.heap, {0})

        label = self._font.render("MÍN", True, config.HIGHLIGHT_COLOR)
        root_pos = positions.get(0)
        if root_pos:
            lr = label.get_rect(
                midbottom=(root_pos[0], root_pos[1] - 24)
            )
            surface.blit(label, lr)

    def _draw_heapify(self, surface: pygame.Surface,
                      rect: pygame.Rect) -> None:
        p = self.progress()
        unsorted = [24, 10, 45, 8, 30, 18, 5]
        result = [5, 8, 18, 24, 30, 45, 10]

        if p < 0.3:
            n = len(unsorted)
            positions = self._compute_positions(rect, n)
            self._draw_edges(surface, positions, n, {3, 4, 5, 6})
            self._draw_nodes(surface, positions, unsorted, {3, 4, 5, 6})
            self._draw_array_bar(surface, rect, unsorted, {3, 4, 5, 6})
        elif p < 0.6:
            partial = [24, 10, 5, 8, 30, 18, 45]
            n = len(partial)
            positions = self._compute_positions(rect, n)
            self._draw_edges(surface, positions, n, {1})
            self._draw_nodes(surface, positions, partial, {1})
            self._draw_array_bar(surface, rect, partial, {1})
        else:
            n = len(result)
            positions = self._compute_positions(rect, n)
            self._draw_edges(surface, positions, n, {0, 2, 6})
            self._draw_nodes(surface, positions, result, {0, 2, 6})
            self._draw_array_bar(surface, rect, result, {0, 2, 6})
