"""Animación visual para Hash Set (conjunto basado en hash)."""

import copy

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation


BUCKET_COUNT = 7


class HashSetAnimation(BaseAnimation):
    """Muestra un conjunto con buckets: add, contains, remove e intersección."""

    def __init__(self) -> None:
        super().__init__()
        self._buckets: list[list[str]] = [[] for _ in range(BUCKET_COUNT)]
        for val in ("Ana", "Leo", "Max", "Eva", "Tito"):
            self._buckets[self._hash_fn(val)].append(val)
        self.actions = [
            ("Add: insertar 'Zoe'", 5.0),
            ("Contains: ¿está 'Ana'?", 5.0),
            ("Remove: eliminar 'Leo'", 5.0),
            ("Intersección con {Ana, Pia, Max}", 5.0),
        ]

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)
        title = self._font.render(
            "hash(x) = sum(ord(c)) mod 7  |  valores únicos",
            True,
            config.SUBTEXT_COLOR,
        )
        surface.blit(
            title,
            title.get_rect(center=(rect.centerx, rect.y + 20)),
        )

        if self.action_index == 0:
            self._draw_add(surface, rect)
        elif self.action_index == 1:
            self._draw_contains(surface, rect)
        elif self.action_index == 2:
            self._draw_remove(surface, rect)
        elif self.action_index == 3:
            self._draw_intersection(surface, rect)

    @staticmethod
    def _hash_fn(key: str) -> int:
        return sum(ord(c) for c in key) % BUCKET_COUNT

    def _draw_buckets(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        buckets: list[list[str]],
        highlight_bucket: int = -1,
        highlight_val: str = "",
        result_label: str = "",
    ) -> None:
        n = len(buckets)
        bw = min(90, (rect.width - 60) // n - 8)
        bh = 36
        total_w = n * bw + (n - 1) * 8
        start_x = rect.x + (rect.width - total_w) // 2
        base_y = rect.y + 70

        for i, bucket in enumerate(buckets):
            bx = start_x + i * (bw + 8)
            idx_surf = self._font.render(str(i), True, config.ACCENT_COLOR)
            surface.blit(
                idx_surf,
                idx_surf.get_rect(midbottom=(bx + bw // 2, base_y - 4)),
            )

            border = (
                config.HIGHLIGHT_COLOR
                if i == highlight_bucket
                else config.DIVIDER_COLOR
            )
            frame = pygame.Rect(bx, base_y, bw, bh * 3 + 12)
            pygame.draw.rect(surface, config.CODE_BG, frame, border_radius=4)
            pygame.draw.rect(surface, border, frame, width=2, border_radius=4)

            for j, val in enumerate(bucket):
                vy = base_y + 6 + j * (bh + 2)
                cell = pygame.Rect(bx + 4, vy, bw - 8, bh)
                is_hl = val == highlight_val
                fg = config.HIGHLIGHT_COLOR if is_hl else config.TEXT_COLOR
                pygame.draw.rect(surface, config.PANEL_BG, cell, border_radius=3)
                pygame.draw.rect(
                    surface,
                    fg if is_hl else config.DIVIDER_COLOR,
                    cell,
                    width=1,
                    border_radius=3,
                )
                vs = self._font.render(val, True, fg)
                surface.blit(vs, vs.get_rect(center=cell.center))

        if result_label:
            lbl = self._font.render(result_label, True, config.SUBTEXT_COLOR)
            surface.blit(
                lbl, lbl.get_rect(midbottom=(rect.centerx, rect.bottom - 8))
            )

    def _draw_add(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        buckets = copy.deepcopy(self._buckets)
        idx = self._hash_fn("Zoe")
        if p < 0.4:
            self._draw_buckets(
                surface, rect, buckets, highlight_bucket=idx,
                result_label=f"hash('Zoe') = {idx}"
            )
        else:
            if "Zoe" not in buckets[idx]:
                buckets[idx].append("Zoe")
            self._draw_buckets(
                surface, rect, buckets, highlight_bucket=idx,
                highlight_val="Zoe",
                result_label="Add('Zoe') — si ya existía, no se duplica"
            )

    def _draw_contains(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        idx = self._hash_fn("Ana")
        self._draw_buckets(
            surface, rect, self._buckets, highlight_bucket=idx,
            highlight_val="Ana",
            result_label="Contains('Ana') → True"
        )

    def _draw_remove(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        buckets = copy.deepcopy(self._buckets)
        idx = self._hash_fn("Leo")
        if p < 0.4:
            self._draw_buckets(
                surface, rect, buckets, highlight_bucket=idx,
                highlight_val="Leo",
                result_label="Remove('Leo')…"
            )
        else:
            if "Leo" in buckets[idx]:
                buckets[idx].remove("Leo")
            self._draw_buckets(
                surface, rect, buckets, highlight_bucket=idx,
                result_label="Leo eliminado del conjunto"
            )

    def _draw_intersection(
        self, surface: pygame.Surface, rect: pygame.Rect
    ) -> None:
        p = self.progress()
        other = {"Ana", "Pia", "Max"}
        result = {"Ana", "Max"}
        buckets = copy.deepcopy(self._buckets)
        if p < 0.5:
            self._draw_buckets(
                surface, rect, buckets,
                highlight_val="Ana" if p < 0.25 else "Max",
                result_label=f"A ∩ B  con B = {sorted(other)}"
            )
        else:
            # mostrar solo resultado en buckets filtrados visualmente
            filtered = [[] for _ in range(BUCKET_COUNT)]
            for v in result:
                filtered[self._hash_fn(v)].append(v)
            self._draw_buckets(
                surface, rect, filtered,
                highlight_val="Ana",
                result_label="Resultado: {Ana, Max}"
            )
