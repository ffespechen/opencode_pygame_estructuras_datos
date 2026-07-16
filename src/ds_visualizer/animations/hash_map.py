"""Animación visual para Hash Map / Diccionario."""

import copy

import pygame
from ds_visualizer import config
from ds_visualizer.animations.base import BaseAnimation, Operation


BUCKET_COUNT = 7


class HashmapAnimation(BaseAnimation):
    """Muestra buckets con pares clave-valor, animando inserción, búsqueda,
       colisión y eliminación."""

    def __init__(self) -> None:
        super().__init__()
        self._initial_buckets: list[list[tuple[str, int]]] = [
            [] for _ in range(BUCKET_COUNT)
        ]
        self._initial_buckets[0].append(("Max", 10))
        self._initial_buckets[1].append(("Leo", 20))
        self._initial_buckets[2].append(("Paco", 30))
        self._initial_buckets[3].append(("Tito", 40))
        self._initial_buckets[4].append(("Eva", 50))
        self._initial_buckets[5].append(("Reno", 60))
        self._initial_buckets[6].append(("Ana", 70))
        self._buckets = copy.deepcopy(self._initial_buckets)
        self._key_counter = 1
        self._highlight_bucket = -1
        self._highlight_key = ""
        self.actions = [
            ("Inserción: colision en bucket 1 (Zoe)", 5.0),
            ("Búsqueda por clave 'Ana'", 5.0),
            ("Eliminación de clave 'Reno'", 5.0),
            ("Inserción: hash('Lia') → bucket 5", 5.0),
        ]
        self.set_operations([
            Operation(
                pygame.K_1, "Put", "put",
                prompt="Clave y valor:", example="Zoe 99",
            ),
            Operation(
                pygame.K_2, "Get", "get",
                prompt="Clave:", example="Ana",
            ),
            Operation(
                pygame.K_3, "Remove", "remove",
                prompt="Clave:", example="Reno",
            ),
        ])

    def reset(self) -> None:
        super().reset()
        self._buckets = copy.deepcopy(self._initial_buckets)
        self._key_counter = 1
        self._highlight_bucket = -1
        self._highlight_key = ""

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        if op_id == "put":
            parsed = self.parse_key_value(user_input or "")
            if parsed is None:
                return "Formato: clave valor (ej: Zoe 99)"
            key, val = parsed
            idx = self._hash_fn(key)
            bucket = self._buckets[idx]
            for i, (k, _) in enumerate(bucket):
                if k == key:
                    bucket[i] = (key, val)
                    self._highlight_bucket = idx
                    self._highlight_key = key
                    return f"Put('{key}', {val}) actualizado → bucket {idx}"
            bucket.append((key, val))
            self._highlight_bucket = idx
            self._highlight_key = key
            return f"Put('{key}', {val}) → bucket {idx}"
        if op_id == "get":
            key = self.parse_token(user_input or "")
            if key is None:
                return "Indicá una clave"
            idx = self._hash_fn(key)
            self._highlight_bucket = idx
            self._highlight_key = key
            for k, v in self._buckets[idx]:
                if k == key:
                    return f"Get('{key}') → {v} (bucket {idx})"
            return f"Get('{key}') → no encontrada"
        if op_id == "remove":
            key = self.parse_token(user_input or "")
            if key is None:
                return "Indicá una clave"
            idx = self._hash_fn(key)
            bucket = self._buckets[idx]
            for i, (k, _) in enumerate(bucket):
                if k == key:
                    bucket.pop(i)
                    self._highlight_bucket = idx
                    self._highlight_key = ""
                    return f"Remove('{key}') del bucket {idx}"
            self._highlight_bucket = -1
            self._highlight_key = ""
            return f"Remove('{key}'): clave no encontrada"
        return ""

    def update(self, dt: float) -> None:
        super().update(dt)

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._font is None:
            self._init_font()

        surface.fill(config.PANEL_BG)
        self._draw_hash_fn(surface, rect)

        if self.interactive:
            self._draw_buckets(
                surface, rect, self._buckets,
                highlight_bucket=self._highlight_bucket,
                highlight_key=self._highlight_key,
            )
            return

        if self.action_index == 0:
            self._draw_insert_collision(surface, rect)
        elif self.action_index == 1:
            self._draw_search(surface, rect)
        elif self.action_index == 2:
            self._draw_delete(surface, rect)
        elif self.action_index == 3:
            self._draw_insert_new(surface, rect)

    @staticmethod
    def _hash_fn(key: str) -> int:
        return sum(ord(c) for c in key) % BUCKET_COUNT

    def _buckets_snapshot(self) -> list[list[tuple[str, int]]]:
        return copy.deepcopy(self._buckets)

    def _draw_hash_fn(self, surface: pygame.Surface,
                      rect: pygame.Rect) -> None:
        text = self._font.render(
            "hash(clave) = sum(ord(c)) mod 7", True, config.SUBTEXT_COLOR,
        )
        r = text.get_rect(center=(rect.x + rect.width // 2, rect.y + 22))
        surface.blit(text, r)

    def _draw_buckets(
        self, surface: pygame.Surface, rect: pygame.Rect,
        buckets: list[list[tuple[str, int]]],
        highlight_bucket: int = -1,
        highlight_key: str = "",
    ) -> None:
        n = len(buckets)
        bw = min(90, (rect.width - 60) // n - 8)
        bh = min(52, (rect.height - 80) // 4)
        total_w = n * bw + (n - 1) * 8
        start_x = rect.x + (rect.width - total_w) // 2
        base_y = rect.y + rect.height // 2 - bh // 2 + 10

        for i, bucket in enumerate(buckets):
            bx = start_x + i * (bw + 8)
            box_rect = pygame.Rect(bx, base_y, bw, bh)

            is_hl = i == highlight_bucket
            border = config.HIGHLIGHT_COLOR if is_hl else config.DIVIDER_COLOR
            bg = config.CODE_BG

            pygame.draw.rect(surface, bg, box_rect, border_radius=4)
            pygame.draw.rect(surface, border, box_rect,
                             width=2, border_radius=4)

            idx_surf = self._font.render(str(i), True, config.SUBTEXT_COLOR)
            idx_r = idx_surf.get_rect(
                center=(box_rect.centerx, box_rect.top - 12),
            )
            surface.blit(idx_surf, idx_r)

            small_font = pygame.font.SysFont("monospace", 11, bold=True)
            for j, (k, v) in enumerate(bucket):
                hl = k == highlight_key
                txt = f"{k}:{v}"
                color = config.HIGHLIGHT_COLOR if hl else config.TEXT_COLOR
                ts = small_font.render(txt, True, color)
                entry_y = box_rect.y + 4 + j * 14
                if box_rect.y + 4 + (j + 1) * 14 > box_rect.bottom - 2:
                    more = f"+{len(bucket) - j}"
                    ts = small_font.render(more, True, config.SUBTEXT_COLOR)
                    surface.blit(ts, (box_rect.x + 4,
                                      box_rect.bottom - 16))
                    break
                surface.blit(ts, (box_rect.x + 4, entry_y))

    def _draw_insert_collision(self, surface: pygame.Surface,
                                rect: pygame.Rect) -> None:
        p = self.progress()
        if p < 0.3:
            self._draw_buckets(surface, rect, self._buckets_snapshot())
        elif p < 0.6:
            buckets = self._buckets_snapshot()
            buckets[1].append(("Zoe", 25))
            self._draw_buckets(surface, rect, buckets,
                               highlight_bucket=1, highlight_key="Zoe")
        else:
            buckets = self._buckets_snapshot()
            buckets[1].append(("Zoe", 25))
            self._draw_buckets(surface, rect, buckets, highlight_bucket=1)

    def _draw_search(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        target_bucket = self._hash_fn("Ana")
        if p < 0.3:
            self._draw_buckets(surface, rect, self._buckets_snapshot())
        elif p < 0.7:
            self._draw_buckets(surface, rect, self._buckets_snapshot(),
                               highlight_bucket=target_bucket)
        else:
            self._draw_buckets(surface, rect, self._buckets_snapshot(),
                               highlight_bucket=target_bucket,
                               highlight_key="Ana")

    def _draw_delete(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        p = self.progress()
        target = self._hash_fn("Reno")
        if p < 0.2:
            self._draw_buckets(surface, rect, self._buckets_snapshot(),
                               highlight_bucket=target, highlight_key="Reno")
        elif p < 0.5:
            buckets = self._buckets_snapshot()
            bucket = buckets[target]
            for i, (k, _) in enumerate(bucket):
                if k == "Reno":
                    bucket.pop(i)
                    break
            self._draw_buckets(surface, rect, buckets,
                               highlight_bucket=target)
        else:
            buckets = self._buckets_snapshot()
            bucket = buckets[target]
            for i, (k, _) in enumerate(bucket):
                if k == "Reno":
                    bucket.pop(i)
                    break
            self._draw_buckets(surface, rect, buckets)

    def _draw_insert_new(self, surface: pygame.Surface,
                          rect: pygame.Rect) -> None:
        p = self.progress()
        target = self._hash_fn("Lia")
        if p < 0.3:
            self._draw_buckets(surface, rect, self._buckets_snapshot())
        elif p < 0.6:
            buckets = self._buckets_snapshot()
            buckets[target].append(("Lia", 35))
            self._draw_buckets(surface, rect, buckets,
                               highlight_bucket=target, highlight_key="Lia")
        else:
            buckets = self._buckets_snapshot()
            buckets[target].append(("Lia", 35))
            self._draw_buckets(surface, rect, buckets,
                               highlight_bucket=target)
