"""Configuración global: colores, fuentes, dimensiones y opciones del menú."""

from pathlib import Path

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
MIN_WIDTH = 800
MIN_HEIGHT = 600
FPS = 60

BG_COLOR = (18, 18, 28)
PANEL_BG = (35, 42, 58)
TEXT_COLOR = (220, 220, 230)
ACCENT_COLOR = (100, 200, 255)
HIGHLIGHT_COLOR = (255, 200, 50)
CODE_BG = (45, 48, 68)
DIVIDER_COLOR = (60, 60, 80)
SHORTCUT_BG = (22, 22, 35)
MENU_SELECTED_BG = (40, 40, 60)
MENU_UNSELECTED_BG = (28, 28, 40)
MENU_TITLE_COLOR = (255, 220, 100)
SUBTEXT_COLOR = (150, 150, 170)

FONT_FAMILY = "monospace"
FONT_SIZE_TITLE = 28
FONT_SIZE_HEADER = 20
FONT_SIZE_NORMAL = 16
FONT_SIZE_SMALL = 13
FONT_SIZE_MENU = 22

SHORTCUT_FONT_SIZE = 15

SHORTCUT_BAR_HEIGHT = 46
LEFT_PANEL_RATIO = 0.5
INFO_PANEL_PADDING = 18
ANIMATION_PANEL_PADDING = 10

DATA_DIR = Path(__file__).parent / "data"

DS_OPTIONS = [
    ("Array o Lista", "array"),
    ("Linked List", "linked_list"),
    ("Doubly Linked List", "doubly_linked_list"),
    ("Stack o Pila", "stack"),
    ("Stack (lista enlazada)", "stack_linked_list"),
    ("Queue o Cola", "queue"),
    ("Queue (lista enlazada)", "queue_linked_list"),
    ("Deque", "deque"),
    ("Priority Queue", "priority_queue"),
    ("Hash Maps o Diccionarios", "hash_map"),
    ("Hash Set", "hash_set"),
    ("Binary Tree", "binary_tree"),
    ("AVL Tree", "avl"),
    ("Heap", "heap"),
    ("Trie", "trie"),
    ("Grafo", "graph"),
    ("Union-Find", "union_find"),
    ("Sparse Matrix", "sparse_matrix"),
    ("Salir", "__quit__"),
]
