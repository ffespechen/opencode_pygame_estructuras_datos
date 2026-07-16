"""Estado de visualización: animación, info, toolbar y atajos."""

import pygame
from ds_visualizer import config
from ds_visualizer.ui import InfoPanel, OpToolbar, ShortcutsBar
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
    UnionFindAnimation,
    HashSetAnimation,
    PriorityQueueAnimation,
    SparseMatrixAnimation,
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
    "union_find": UnionFindAnimation,
    "hash_set": HashSetAnimation,
    "priority_queue": PriorityQueueAnimation,
    "sparse_matrix": SparseMatrixAnimation,
    "hash_map": HashmapAnimation,
    "binary_tree": BinaryTreeAnimation,
    "heap": HeapAnimation,
    "graph": GraphAnimation,
}

ANIM_RATIO = 0.45


class VisualizationState:
    """Vista vertical: anim | info | toolbar ops | atajos."""

    def __init__(self) -> None:
        self.info_panel = InfoPanel()
        self.shortcuts_bar = ShortcutsBar()
        self.op_toolbar = OpToolbar()
        self.animation = None
        self.ds_key = ""
        self.back_to_menu = False
        self._anim_rect = pygame.Rect(0, 0, 0, 0)
        self._toolbar_y = 0

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

    def _chrome_height(self) -> int:
        return config.SHORTCUT_BAR_HEIGHT + config.OP_TOOLBAR_HEIGHT

    def _reload_content(self, width: int, height: int) -> None:
        content_h = height - self._chrome_height()
        anim_h = int(content_h * ANIM_RATIO)
        info_h = content_h - anim_h

        md_path = config.DATA_DIR / f"{self.ds_key}.md"
        info_width = width - 2 * config.INFO_PANEL_PADDING
        info_height = info_h - 2

        self.info_panel.load_markdown(str(md_path), info_width, info_height)

    def _handle_toolbar_extra(self, action_id: str) -> None:
        if not self.animation:
            return
        anim = self.animation
        if action_id == "undo":
            anim.undo()
        elif action_id == "reset":
            anim.reset()
        elif action_id == "challenge":
            anim.start_challenge()
        elif action_id == "hint":
            anim.status_message = anim.challenge_hint()
            anim._status_timer = anim.STATUS_DURATION * 2

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.TEXTINPUT:
                if self.animation and self.animation.handle_text(event.text):
                    continue
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.animation and self.animation.cancel_input():
                        continue
                    if self.animation and self.animation.step_mode:
                        self.animation.clear_steps()
                        continue
                    self.back_to_menu = True
                elif self.animation and self.animation.handle_key(event.key):
                    continue
            elif event.type == pygame.MOUSEWHEEL:
                self.info_panel.scroll(event.y * 30)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hit = self.op_toolbar.hit(event.pos)
                if hit is not None and self.animation:
                    kind, hid = hit
                    if kind == "op":
                        self.animation.run_operation_by_id(hid)
                    else:
                        self._handle_toolbar_extra(hid)
                    continue
                if self.animation and self._anim_rect.collidepoint(event.pos):
                    self.animation.handle_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.animation:
                    self.animation.handle_mouse_up(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if self.animation and self.animation.dragging_id:
                    self.animation.handle_mouse_motion(event.pos)

    def update(self, dt: float) -> None:
        if self.animation:
            self.animation.update(dt)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.info_panel.scroll(-300 * dt)
        if keys[pygame.K_DOWN]:
            self.info_panel.scroll(300 * dt)

    def draw(self, screen: pygame.Surface, width: int, height: int) -> None:
        chrome = self._chrome_height()
        content_h = height - chrome
        anim_h = int(content_h * ANIM_RATIO)
        info_h = content_h - anim_h
        self._toolbar_y = height - chrome

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
            self._anim_rect = anim_rect
            self.animation.clear_hit_targets()
            self.animation.draw(screen, anim_rect)
            self.animation.draw_overlays(screen, anim_rect)

        info_y = anim_h + 1
        self.info_panel.draw(screen, 0, info_y)

        ops = self.animation.operations if self.animation else []
        extras = [
            ("undo", "U Undo"),
            ("reset", "R Reset"),
            ("challenge", "C Reto"),
            ("hint", "H Hint"),
        ]
        self.op_toolbar.draw_with_labels(
            screen, width, self._toolbar_y, ops, extras
        )

        current_action = self.animation.current_action if self.animation else ""
        mode_hint = (
            "→Demo" if (self.animation and self.animation.interactive)
            else "→Interactivo"
        )
        shortcuts = (
            f"ESC: Menú  |  I: {mode_hint}  |  Click: sel  |  "
            "Space: paso  |  P: auto  |  U: undo  |  C: reto  |  Ctrl+Q"
        )
        self.shortcuts_bar.draw(
            screen, width, height, shortcuts, current_action,
        )
