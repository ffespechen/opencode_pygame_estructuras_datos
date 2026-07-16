"""Estado de visualización: pantalla dividida con animación, info y barra de atajos."""

import pygame
from ds_visualizer import config
from ds_visualizer.ui import InfoPanel, ShortcutsBar
from ds_visualizer.animations import (
    ArrayAnimation,
    LinkedListAnimation,
    DoublyLinkedListAnimation,
    DequeAnimation,
    StackAnimation,
    StackLinkedListAnimation,
    QueueAnimation,
    QueueLinkedListAnimation,
    TrieAnimation,
    AvlAnimation,
    HashmapAnimation,
    BinaryTreeAnimation,
    HeapAnimation,
    GraphAnimation,
)


ANIMATION_MAP = {
    "array": ArrayAnimation,
    "linked_list": LinkedListAnimation,
    "doubly_linked_list": DoublyLinkedListAnimation,
    "deque": DequeAnimation,
    "stack": StackAnimation,
    "stack_linked_list": StackLinkedListAnimation,
    "queue": QueueAnimation,
    "queue_linked_list": QueueLinkedListAnimation,
    "trie": TrieAnimation,
    "avl": AvlAnimation,
    "hash_map": HashmapAnimation,
    "binary_tree": BinaryTreeAnimation,
    "heap": HeapAnimation,
    "graph": GraphAnimation,
}

ANIM_RATIO = 0.45


class VisualizationState:
    """Gestiona la vista dividida verticalmente: anim (arr), info (medio), atajos (inf)."""

    def __init__(self) -> None:
        self.info_panel = InfoPanel()
        self.shortcuts_bar = ShortcutsBar()
        self.animation = None
        self.ds_key = ""
        self.back_to_menu = False

    def on_enter(
        self, ds_key: str, screen: pygame.Surface,
        window_width: int, window_height: int,
    ) -> None:
        self.ds_key = ds_key
        self.back_to_menu = False
        self._reload_content(window_width, window_height)

        anim_cls = ANIMATION_MAP[ds_key]
        self.animation = anim_cls()

    def on_resize(self, screen: pygame.Surface, width: int, height: int) -> None:
        if self.ds_key:
            self._reload_content(width, height)

    def _reload_content(self, width: int, height: int) -> None:
        content_h = height - config.SHORTCUT_BAR_HEIGHT
        anim_h = int(content_h * ANIM_RATIO)
        info_h = content_h - anim_h

        md_path = config.DATA_DIR / f"{self.ds_key}.md"
        info_width = width - 2 * config.INFO_PANEL_PADDING
        info_height = info_h - 2

        self.info_panel.load_markdown(str(md_path), info_width, info_height)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.back_to_menu = True
            elif event.type == pygame.MOUSEWHEEL:
                self.info_panel.scroll(event.y * 30)

    def update(self, dt: float) -> None:
        if self.animation:
            self.animation.update(dt)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.info_panel.scroll(-300 * dt)
        if keys[pygame.K_DOWN]:
            self.info_panel.scroll(300 * dt)

    def draw(self, screen: pygame.Surface, width: int, height: int) -> None:
        content_h = height - config.SHORTCUT_BAR_HEIGHT
        anim_h = int(content_h * ANIM_RATIO)
        info_h = content_h - anim_h

        anim_bg = pygame.Rect(0, 0, width, anim_h)
        pygame.draw.rect(screen, config.PANEL_BG, anim_bg)

        info_bg = pygame.Rect(0, anim_h, width, info_h)
        pygame.draw.rect(screen, config.PANEL_BG, info_bg)

        pygame.draw.line(
            screen, config.DIVIDER_COLOR,
            (0, anim_h), (width, anim_h),
            width=2,
        )

        if self.animation:
            anim_rect = pygame.Rect(
                config.ANIMATION_PANEL_PADDING,
                config.ANIMATION_PANEL_PADDING,
                width - 2 * config.ANIMATION_PANEL_PADDING,
                anim_h - 2 * config.ANIMATION_PANEL_PADDING,
            )
            self.animation.draw(screen, anim_rect)

        info_y = anim_h + 1
        self.info_panel.draw(screen, 0, info_y)

        current_action = self.animation.current_action if self.animation else ""
        shortcuts = (
            "ESC: Menú  |  ↑↓ o Rueda: Desplazar info  |  Ctrl+Q: Salir"
        )
        self.shortcuts_bar.draw(
            screen, width, height, shortcuts, current_action,
        )
