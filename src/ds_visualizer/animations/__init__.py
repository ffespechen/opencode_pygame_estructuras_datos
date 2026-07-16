"""Animaciones visuales para cada estructura de datos."""

from .base import BaseAnimation
from .array import ArrayAnimation
from .linked_list import LinkedListAnimation
from .doubly_linked_list import DoublyLinkedListAnimation
from .deque import DequeAnimation
from .stack import StackAnimation
from .stack_linked_list import StackLinkedListAnimation
from .queue import QueueAnimation
from .queue_linked_list import QueueLinkedListAnimation
from .trie import TrieAnimation
from .avl import AvlAnimation
from .hash_map import HashmapAnimation
from .binary_tree import BinaryTreeAnimation
from .heap import HeapAnimation
from .graph import GraphAnimation

__all__ = [
    "BaseAnimation",
    "ArrayAnimation",
    "LinkedListAnimation",
    "DoublyLinkedListAnimation",
    "DequeAnimation",
    "StackAnimation",
    "StackLinkedListAnimation",
    "QueueAnimation",
    "QueueLinkedListAnimation",
    "TrieAnimation",
    "AvlAnimation",
    "HashmapAnimation",
    "BinaryTreeAnimation",
    "HeapAnimation",
    "GraphAnimation",
]
