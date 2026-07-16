"""Clase base para todas las animaciones de estructuras de datos.

Etapa 1: click/selección, stepper, undo, feedback de complejidad.
Etapa 2: hooks para toolbar (run_operation_by_id).
Etapa 3: drag & drop + hooks de challenges.
"""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from typing import Any, Callable

import pygame


@dataclass(frozen=True)
class Operation:
    """Operación interactiva disparable por tecla o toolbar.

    Si ``prompt`` no es None, antes de aplicar se pide texto al usuario.
    ``example`` se muestra como pista (ej. \"B F\").
    ``complexity`` se muestra en el feedback tras ejecutar (ej. \"O(1)\").
    ``mutates`` indica si la op debe guardarse en el historial de undo.
    ``uses_selection`` si True y hay selección, puede omitir el prompt.
    """

    key: int
    label: str
    op_id: str
    prompt: str | None = None
    example: str = ""
    complexity: str = ""
    mutates: bool = True
    uses_selection: bool = False


@dataclass
class HitTarget:
    """Zona clickeable de un elemento dibujado."""

    target_id: str
    rect: pygame.Rect
    label: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnimStep:
    """Un frame del stepper pedagógico."""

    message: str
    highlight_idx: int = -1
    highlight_set: frozenset[int] = field(default_factory=frozenset)
    highlight_ids: frozenset[str] = field(default_factory=frozenset)
    note: str = ""


@dataclass
class Challenge:
    """Reto corto sobre el estado actual de la estructura."""

    challenge_id: str
    title: str
    description: str
    hint: str
    check: Callable[[Any], bool]
    success: str = "¡Reto cumplido!"


class BaseAnimation:
    """Interfaz común: demo + interactivo + selección + stepper + undo."""

    LIVE_ANIM_DURATION = 0.85
    STATUS_DURATION = 2.8
    UNDO_LIMIT = 40

    def __init__(self) -> None:
        self.action_index = 0
        self.action_timer = 0.0
        self.actions: list[tuple[str, float]] = []
        self.current_action = ""
        self._font = None
        self._prompt_font = None
        self._small_font = None

        self.interactive = False
        self.operations: list[Operation] = []
        self.next_value = 100
        self.highlight_idx = -1
        self.highlight_set: set[int] = set()
        self.status_message = ""
        self._status_timer = 0.0
        self.live_op: str | None = None
        self._live_timer = 0.0

        self.input_active = False
        self._input_op: Operation | None = None
        self._input_buffer = ""

        # Etapa 1 — selección / hit-test
        self._hit_targets: list[HitTarget] = []
        self.selected_id: str | None = None
        self.selected_label: str = ""
        self.complexity_label: str = ""
        self.feedback_detail: str = ""

        # Etapa 1 — stepper
        self.step_mode = False
        self.steps: list[AnimStep] = []
        self.step_index = 0
        self.step_auto = False

        # Etapa 1 — undo
        self._undo_stack: list[dict[str, Any]] = []

        # Etapa 3 — drag
        self.drag_enabled = True
        self.dragging_id: str | None = None
        self.drag_label: str = ""
        self.drag_pos: tuple[int, int] | None = None
        self._drag_origin: str | None = None

        # Etapa 3 — challenges
        self.challenges: list[Challenge] = []
        self.active_challenge: Challenge | None = None
        self.challenge_index = -1
        self.challenge_done = False

        # Último rect de dibujo (para overlays)
        self._last_draw_rect: pygame.Rect | None = None

    def _init_font(self) -> None:
        self._font = pygame.font.SysFont("monospace", 14, bold=True)
        self._prompt_font = pygame.font.SysFont("monospace", 16, bold=True)
        self._small_font = pygame.font.SysFont("monospace", 13, bold=True)

    def set_operations(self, ops: list[Operation]) -> None:
        self.operations = list(ops)

    def set_challenges(self, challenges: list[Challenge]) -> None:
        self.challenges = list(challenges)

    # Atributos típicos de las estructuras (undo automático).
    _AUTO_STATE_ATTRS = (
        "values", "base_values", "heap", "vertices", "edges",
        "_next_vertex_id", "_highlighted", "_last_order", "_search_target",
        "_highlight_indices", "parent", "rank", "tree", "root",
        "triplets", "nodes", "children", "entries", "items",
        "set_data", "queue", "prio_items", "word", "inserted",
        "extra_vertex", "extra_edge", "buckets", "keys", "data",
        "_buckets", "bst_values", "words", "_key_counter",
        "_highlight_bucket", "_highlight_key", "_highlight_cell",
        "_highlight_val", "_word_idx", "_find_element", "_union_pair",
        "_highlight_edges", "_label_idx", "_name_idx", "_val_counter",
        "_last_inserted", "_highlight_idx",
    )

    # --- estado / undo ---------------------------------------------------

    def capture_state(self) -> dict[str, Any]:
        """Snapshot restaurable; incluye atributos conocidos de cada estructura."""
        state: dict[str, Any] = {
            "highlight_idx": self.highlight_idx,
            "highlight_set": set(self.highlight_set),
            "next_value": self.next_value,
            "selected_id": self.selected_id,
            "selected_label": self.selected_label,
        }
        for attr in self._AUTO_STATE_ATTRS:
            if hasattr(self, attr):
                state[attr] = copy.deepcopy(getattr(self, attr))
        return state

    def restore_state(self, state: dict[str, Any]) -> None:
        self.highlight_idx = state.get("highlight_idx", -1)
        self.highlight_set = set(state.get("highlight_set", set()))
        self.next_value = state.get("next_value", self.next_value)
        self.selected_id = state.get("selected_id")
        self.selected_label = state.get("selected_label", "")
        for attr in self._AUTO_STATE_ATTRS:
            if attr in state and hasattr(self, attr):
                setattr(self, attr, copy.deepcopy(state[attr]))

    def push_undo(self) -> None:
        snap = copy.deepcopy(self.capture_state())
        self._undo_stack.append(snap)
        if len(self._undo_stack) > self.UNDO_LIMIT:
            self._undo_stack.pop(0)

    def undo(self) -> str:
        self.cancel_input()
        self.clear_steps()
        if not self._undo_stack:
            return "Nada que deshacer"
        state = self._undo_stack.pop()
        self.restore_state(state)
        self.live_op = None
        self._live_timer = 0.0
        self.complexity_label = ""
        self.feedback_detail = "Undo"
        self.status_message = "Deshacer — estado anterior restaurado"
        self._status_timer = self.STATUS_DURATION
        self.current_action = self.status_message
        self._check_challenge()
        return self.status_message

    # --- selección / hits ------------------------------------------------

    def clear_hit_targets(self) -> None:
        self._hit_targets = []

    def register_hit(
        self,
        target_id: str,
        rect: pygame.Rect,
        label: str = "",
        **meta: Any,
    ) -> None:
        self._hit_targets.append(
            HitTarget(target_id, pygame.Rect(rect), label or target_id, meta)
        )

    def hit_at(self, pos: tuple[int, int]) -> HitTarget | None:
        for target in reversed(self._hit_targets):
            if target.rect.collidepoint(pos):
                return target
        return None

    def select_target(self, target: HitTarget | None) -> None:
        if target is None:
            self.selected_id = None
            self.selected_label = ""
            self.status_message = "Selección limpiada"
            self._status_timer = self.STATUS_DURATION
            return
        self.selected_id = target.target_id
        self.selected_label = target.label
        self.status_message = f"Seleccionado: {target.label}"
        self.feedback_detail = target.label
        self._status_timer = self.STATUS_DURATION
        if not self.interactive:
            self.interactive = True
        self.on_select(target)

    def on_select(self, target: HitTarget) -> None:
        """Hook opcional: p.ej. resaltar índice al seleccionar."""
        if "index" in target.meta:
            self.highlight_idx = int(target.meta["index"])

    def selection_as_input(self, op: Operation) -> str | None:
        """Deriva texto de prompt desde la selección actual."""
        if not op.uses_selection or not self.selected_id:
            return None

        target = None
        for t in self._hit_targets:
            if t.target_id == self.selected_id:
                target = t
                break

        if target is not None:
            meta = target.meta
            # Sparse matrix: fila col
            if "row" in meta and "col" in meta and op.op_id in (
                "search", "insert", "delete",
            ):
                return f"{meta['row']} {meta['col']}"
            # Hash map / set: clave o valor
            if "key" in meta and op.op_id in ("get", "remove", "contains", "search"):
                return str(meta["key"])
            # Delete/search por valor (listas) vs por índice (array)
            if "index" in meta and op.op_id == "delete":
                prompt = (op.prompt or "").lower()
                if "índice" in prompt or "indice" in prompt:
                    return str(meta["index"])
            if "value" in meta and op.op_id in (
                "delete", "search", "contains", "remove", "find",
            ):
                return str(meta["value"])
            if "label" in meta and op.op_id in ("find", "bfs", "dfs", "add_edge"):
                return str(meta["label"])

        if self.selected_label:
            label = self.selected_label
            if "=" in label and label.startswith("["):
                try:
                    idx_part, val_part = label.split("=", 1)
                    idx = idx_part.strip("[]")
                    if op.op_id == "delete":
                        prompt = (op.prompt or "").lower()
                        if "índice" in prompt or "indice" in prompt:
                            return idx
                        return val_part.strip()
                    if op.op_id == "search":
                        return val_part.strip()
                except ValueError:
                    pass
            token = label.split()[0].strip("[]→")
            if token:
                return token
        return self.selected_id

    # --- stepper ---------------------------------------------------------

    def clear_steps(self) -> None:
        self.steps = []
        self.step_index = 0
        self.step_mode = False
        self.step_auto = False

    def begin_steps(self, steps: list[AnimStep], complexity: str = "") -> None:
        if not steps:
            self.clear_steps()
            return
        self.steps = list(steps)
        self.step_index = 0
        self.step_mode = True
        self.step_auto = False
        self.live_op = None
        self._live_timer = 0.0
        if complexity:
            self.complexity_label = complexity
        self._apply_current_step()

    def build_steps(
        self, op_id: str, user_input: str | None = None
    ) -> list[AnimStep]:
        """Subclases: devolver pasos pedagógicos; vacío = animación live corta."""
        return []

    def _apply_current_step(self) -> None:
        if not self.steps:
            return
        step = self.steps[self.step_index]
        self.highlight_idx = step.highlight_idx
        self.highlight_set = set(step.highlight_set)
        self.status_message = (
            f"Paso {self.step_index + 1}/{len(self.steps)}: {step.message}"
        )
        if step.note:
            self.feedback_detail = step.note
        self._status_timer = 9999.0
        self.current_action = self.status_message

    def step_next(self) -> bool:
        if not self.step_mode or not self.steps:
            return False
        if self.step_index >= len(self.steps) - 1:
            self.clear_steps()
            self.status_message = "Stepper terminado"
            self._status_timer = self.STATUS_DURATION
            return True
        self.step_index += 1
        self._apply_current_step()
        return True

    def step_prev(self) -> bool:
        if not self.step_mode or not self.steps:
            return False
        if self.step_index <= 0:
            return True
        self.step_index -= 1
        self._apply_current_step()
        return True

    def step_finish(self) -> bool:
        if not self.step_mode or not self.steps:
            return False
        self.step_index = len(self.steps) - 1
        self._apply_current_step()
        self.clear_steps()
        self.status_message = "Stepper: fin"
        self._status_timer = self.STATUS_DURATION
        return True

    # --- challenges (etapa 3) --------------------------------------------

    def start_challenge(self, index: int | None = None) -> str:
        if not self.challenges:
            return "Esta estructura no tiene retos aún"
        if index is None:
            index = (self.challenge_index + 1) % len(self.challenges)
        index = max(0, min(index, len(self.challenges) - 1))
        self.challenge_index = index
        self.active_challenge = self.challenges[index]
        self.challenge_done = False
        ch = self.active_challenge
        self.status_message = f"Reto: {ch.title}"
        self.feedback_detail = ch.description
        self._status_timer = 9999.0
        if not self.interactive:
            self.interactive = True
        return self.status_message

    def clear_challenge(self) -> None:
        self.active_challenge = None
        self.challenge_done = False

    def _check_challenge(self) -> None:
        ch = self.active_challenge
        if ch is None or self.challenge_done:
            return
        try:
            ok = bool(ch.check(self))
        except Exception:
            return
        if ok:
            self.challenge_done = True
            self.status_message = ch.success
            self.feedback_detail = ch.title
            self.complexity_label = "✓"
            self._status_timer = self.STATUS_DURATION * 2

    def challenge_hint(self) -> str:
        if self.active_challenge is None:
            return "Sin reto activo (C para iniciar)"
        return f"Hint: {self.active_challenge.hint}"

    # --- drag (etapa 3) --------------------------------------------------

    def can_drag(self, target: HitTarget) -> bool:
        return self.drag_enabled and target.meta.get("draggable", True)

    def on_drop(self, source_id: str, dest: HitTarget | None) -> str:
        """Subclases: reaccionar a soltar un elemento. Vacío = no soportado."""
        return ""

    def handle_mouse_down(self, pos: tuple[int, int]) -> bool:
        target = self.hit_at(pos)
        if target is None:
            if self.selected_id is not None:
                self.select_target(None)
                return True
            return False
        if not self.interactive:
            self.interactive = True
        self.select_target(target)
        if self.can_drag(target):
            self.dragging_id = target.target_id
            self.drag_label = target.label
            self._drag_origin = target.target_id
            self.drag_pos = pos
        return True

    def handle_mouse_up(self, pos: tuple[int, int]) -> bool:
        if self.dragging_id is None:
            return False
        source = self.dragging_id
        self.dragging_id = None
        self.drag_pos = None
        dest = self.hit_at(pos)
        if dest is not None and dest.target_id != source:
            self.push_undo()
            msg = self.on_drop(source, dest)
            if msg:
                self.status_message = msg
                self._status_timer = self.STATUS_DURATION
                self.current_action = msg
                self._check_challenge()
                return True
            # drop sin efecto → deshacer el push vacío de undo
            if self._undo_stack:
                self._undo_stack.pop()
        self._drag_origin = None
        return True

    def handle_mouse_motion(self, pos: tuple[int, int]) -> bool:
        if self.dragging_id is None:
            return False
        self.drag_pos = pos
        return True

    # --- ciclo de operaciones --------------------------------------------

    def toggle_interactive(self) -> None:
        self.cancel_input()
        self.clear_steps()
        self.interactive = not self.interactive
        self.live_op = None
        self._live_timer = 0.0
        self.highlight_idx = -1
        self.highlight_set = set()
        if self.interactive:
            self.status_message = (
                "Interactivo — click, 1…N, Space=paso, U=undo"
            )
            self._status_timer = self.STATUS_DURATION
        else:
            self.reset()
            self.status_message = "Modo demo (automático)"
            self._status_timer = self.STATUS_DURATION
            self.action_timer = 0.0

    def reset(self) -> None:
        """Restaura el estado inicial. Las subclases deben sobrescribirlo."""
        self.cancel_input()
        self.clear_steps()
        self._undo_stack.clear()
        self.next_value = 100
        self.highlight_idx = -1
        self.highlight_set = set()
        self.live_op = None
        self._live_timer = 0.0
        self.selected_id = None
        self.selected_label = ""
        self.complexity_label = ""
        self.feedback_detail = ""
        self.dragging_id = None
        self.drag_pos = None
        self.challenge_done = False
        self.status_message = "Estructura reiniciada"
        self._status_timer = self.STATUS_DURATION

    def apply_operation(self, op_id: str, user_input: str | None = None) -> str:
        """Aplica la operación. ``user_input`` viene del prompt si aplica."""
        return ""

    def take_next_value(self) -> int:
        value = self.next_value
        self.next_value += 7
        if self.next_value > 199:
            self.next_value = 11
        return value

    def find_operation(self, op_id: str) -> Operation | None:
        for op in self.operations:
            if op.op_id == op_id:
                return op
        return None

    def run_operation_by_id(self, op_id: str) -> bool:
        """Dispara una operación (teclado o toolbar)."""
        op = self.find_operation(op_id)
        if op is None:
            return False
        return self._start_operation(op)

    def _start_operation(self, op: Operation) -> bool:
        if not self.interactive:
            self.interactive = True
        self.clear_steps()

        if op.prompt is not None:
            if op.uses_selection and self.selected_id:
                derived = self.selection_as_input(op)
                if derived is not None:
                    self._execute_operation(op, derived)
                    return True
                # Selección parcial (ej. primer extremo de arista)
                if self._status_timer > 0 and "elegí" in self.status_message.lower():
                    return True
            self.begin_input(op)
            return True

        # Sin prompt: aún puede usar selección como input implícito
        derived = self.selection_as_input(op)
        self._execute_operation(op, derived)
        return True

    def _execute_operation(self, op: Operation, user_input: str | None) -> None:
        if op.mutates:
            self.push_undo()
        self.live_op = op.op_id
        self._live_timer = 0.0
        msg = self.apply_operation(op.op_id, user_input)
        # Si falló validación, revertir undo
        fail_tokens = (
            "Ingresá", "Indicá", "no existe", "vacío", "vacía",
            "fuera de rango", "Formato", "Usá", "ya existe", "Nada",
        )
        failed = any(tok.lower() in (msg or "").lower() for tok in (
            "ingresá", "indicá", "no existe", "fuera de rango",
            "formato", "ya existe", "máx",
        )) and op.mutates
        # No revertir en estructuras vacías legítimas (pop en vacío)
        empty_ok = "vací" in (msg or "").lower()
        if failed and not empty_ok and self._undo_stack:
            # Validación fallida típica: mensaje pide reintentar
            if any(
                x in (msg or "")
                for x in (
                    "Ingresá", "Indicá", "Formato", "fuera de rango",
                    "no existe", "ya existe", "Usá", "máx",
                )
            ):
                self._undo_stack.pop()
                self.live_op = None

        self.complexity_label = op.complexity
        self.feedback_detail = msg or op.label
        self.status_message = msg or op.label
        if op.complexity and msg and not failed:
            self.status_message = f"{msg}  [{op.complexity}]"
        self._status_timer = self.STATUS_DURATION
        self.current_action = self.status_message

        steps = self.build_steps(op.op_id, user_input)
        if steps and not failed:
            self.begin_steps(steps, op.complexity)
        self._check_challenge()

    # --- parsing helpers -------------------------------------------------

    @staticmethod
    def parse_int(text: str) -> int | None:
        text = text.strip()
        if not re.fullmatch(r"-?\d+", text):
            return None
        return int(text)

    @staticmethod
    def parse_token(text: str) -> str | None:
        text = text.strip()
        if not text:
            return None
        return text.split()[0]

    @staticmethod
    def parse_pair(text: str) -> tuple[str, str] | None:
        """Acepta 'B F', 'B-F', 'B,F', 'BF' (2 chars)."""
        text = text.strip().upper()
        if not text:
            return None
        parts = re.split(r"[\s,\-–—:/]+", text)
        parts = [p for p in parts if p]
        if len(parts) == 2:
            return parts[0], parts[1]
        if len(parts) == 1 and len(parts[0]) == 2:
            return parts[0][0], parts[0][1]
        return None

    @staticmethod
    def parse_int_pair(text: str) -> tuple[int, int] | None:
        text = text.strip()
        parts = re.split(r"[\s,\-–—:/]+", text)
        parts = [p for p in parts if p]
        if len(parts) != 2:
            return None
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            return None

    @staticmethod
    def parse_int_triple(text: str) -> tuple[int, int, int] | None:
        text = text.strip()
        parts = re.split(r"[\s,\-–—:/]+", text)
        parts = [p for p in parts if p]
        if len(parts) != 3:
            return None
        try:
            return int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError:
            return None

    @staticmethod
    def parse_key_value(text: str) -> tuple[str, int] | None:
        """'Zoe 99' o 'Zoe:99'."""
        text = text.strip()
        parts = re.split(r"[\s=:]+", text)
        parts = [p for p in parts if p]
        if len(parts) != 2:
            return None
        try:
            return parts[0], int(parts[1])
        except ValueError:
            return None

    @staticmethod
    def parse_prio_label(text: str) -> tuple[int, str] | None:
        """'2 NET' o '2:NET'."""
        text = text.strip()
        parts = re.split(r"[\s=:]+", text)
        parts = [p for p in parts if p]
        if len(parts) != 2:
            return None
        try:
            return int(parts[0]), parts[1].upper()
        except ValueError:
            return None

    # --- input prompt ----------------------------------------------------

    def begin_input(self, op: Operation) -> None:
        self.input_active = True
        self._input_op = op
        # Prefill desde selección si aplica
        derived = self.selection_as_input(op)
        self._input_buffer = derived or ""
        self.status_message = op.prompt or "Ingresá un valor"
        self._status_timer = 9999.0
        try:
            pygame.key.start_text_input()
        except pygame.error:
            pass

    def cancel_input(self) -> bool:
        """Cancela el prompt activo. Devuelve True si había uno."""
        if not self.input_active:
            return False
        self.input_active = False
        self._input_op = None
        self._input_buffer = ""
        self.status_message = "Entrada cancelada"
        self._status_timer = self.STATUS_DURATION
        try:
            pygame.key.stop_text_input()
        except pygame.error:
            pass
        return True

    def _submit_input(self) -> None:
        op = self._input_op
        text = self._input_buffer.strip()
        self.input_active = False
        self._input_op = None
        self._input_buffer = ""
        try:
            pygame.key.stop_text_input()
        except pygame.error:
            pass
        if op is None:
            return
        if not text:
            self.status_message = "Entrada vacía — cancelado"
            self._status_timer = self.STATUS_DURATION
            return
        self._execute_operation(op, text)

    def handle_text(self, text: str) -> bool:
        """Recibe TEXTINPUT de pygame. Devuelve True si se consumió."""
        if not self.input_active:
            return False
        if text and text.isprintable() and text not in "\r\n\t":
            self._input_buffer += text
        return True

    def handle_key(self, key: int) -> bool:
        """Procesa teclas del modo interactivo. Devuelve True si se consumió."""
        mods = pygame.key.get_mods()

        if self.input_active:
            if key == pygame.K_ESCAPE:
                self.cancel_input()
                return True
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._submit_input()
                return True
            if key == pygame.K_BACKSPACE:
                self._input_buffer = self._input_buffer[:-1]
                return True
            return True

        if key == pygame.K_i:
            self.toggle_interactive()
            return True

        if key == pygame.K_r:
            if not self.interactive:
                self.interactive = True
            self.reset()
            return True

        if key == pygame.K_u:
            if not self.interactive:
                self.interactive = True
            self.undo()
            return True

        if key == pygame.K_c:
            if mods & pygame.KMOD_SHIFT:
                self.clear_challenge()
                self.status_message = "Reto cancelado"
                self._status_timer = self.STATUS_DURATION
            else:
                self.start_challenge()
            return True

        if key == pygame.K_h and self.active_challenge is not None:
            self.status_message = self.challenge_hint()
            self._status_timer = self.STATUS_DURATION * 2
            return True

        # Stepper
        if self.step_mode:
            if key in (pygame.K_SPACE, pygame.K_RIGHT, pygame.K_PERIOD):
                self.step_next()
                return True
            if key in (pygame.K_LEFT, pygame.K_COMMA):
                self.step_prev()
                return True
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_END):
                self.step_finish()
                return True

        matching = [op for op in self.operations if op.key == key]
        if not matching:
            return False

        return self._start_operation(matching[0])

    def live_progress(self) -> float:
        if self.step_mode and self.steps:
            if len(self.steps) <= 1:
                return 0.999
            return min(self.step_index / (len(self.steps) - 1), 0.999)
        if not self.live_op:
            return 1.0
        return min(self._live_timer / self.LIVE_ANIM_DURATION, 0.999)

    def operations_hint(self) -> str:
        if not self.operations:
            return "I: modo interactivo"
        parts = [
            f"{pygame.key.name(op.key).upper()}:{op.label}"
            for op in self.operations
        ]
        return "  ".join(parts)

    def update(self, dt: float) -> None:
        if self.input_active:
            op = self._input_op
            example = f"  (ej: {op.example})" if op and op.example else ""
            prompt = op.prompt if op else "Valor"
            self.current_action = f"{prompt} {self._input_buffer}█{example}"
            return

        if self.step_mode:
            if self.steps:
                step = self.steps[self.step_index]
                self.current_action = (
                    f"Paso {self.step_index + 1}/{len(self.steps)}: "
                    f"{step.message}  [Space/←→]"
                )
            return

        if self._status_timer > 0:
            self._status_timer = max(0.0, self._status_timer - dt)

        if self.interactive:
            if self.live_op:
                self._live_timer += dt
                if self._live_timer >= self.LIVE_ANIM_DURATION:
                    self.live_op = None
                    self._live_timer = 0.0
            if self.status_message and self._status_timer > 0:
                self.current_action = self.status_message
            else:
                self.current_action = self.operations_hint()
            return

        if not self.actions:
            return

        self.action_timer += dt
        _, duration = self.actions[self.action_index]
        if self.action_timer >= duration:
            self.action_timer = 0.0
            self.action_index = (self.action_index + 1) % len(self.actions)

        self.current_action = self.actions[self.action_index][0]

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        raise NotImplementedError

    def draw_overlays(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Overlays de selección, complejidad, reto y drag."""
        self._last_draw_rect = rect
        if self._small_font is None:
            self._init_font()
        from ds_visualizer import config

        # Anillo de selección
        if self.selected_id:
            for t in self._hit_targets:
                if t.target_id == self.selected_id:
                    pygame.draw.rect(
                        surface, config.ACCENT_COLOR, t.rect.inflate(8, 8),
                        width=2, border_radius=8,
                    )
                    break

        # Badge complejidad / selección
        badges: list[str] = []
        if self.complexity_label:
            badges.append(self.complexity_label)
        if self.selected_label:
            badges.append(f"sel:{self.selected_label}")
        if self.active_challenge is not None:
            mark = "✓" if self.challenge_done else "…"
            badges.append(f"reto:{mark} {self.active_challenge.title}")
        if badges:
            line = "  |  ".join(badges)
            surf = self._small_font.render(line, True, config.ACCENT_COLOR)
            surface.blit(surf, (rect.x + 8, rect.y + 6))

        # Fantasma de drag
        if self.dragging_id and self.drag_pos:
            ghost = self._small_font.render(
                self.drag_label or self.dragging_id, True, config.HIGHLIGHT_COLOR
            )
            surface.blit(
                ghost,
                (self.drag_pos[0] + 12, self.drag_pos[1] - 10),
            )

        self.draw_input_overlay(surface, rect)

    def draw_input_overlay(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Barra de prompt sobre el panel de animación."""
        from ds_visualizer import config

        if not self.input_active or self._input_op is None:
            return
        if self._prompt_font is None:
            self._init_font()

        bar_h = 40
        bar = pygame.Rect(rect.x + 8, rect.bottom - bar_h - 6, rect.width - 16, bar_h)
        pygame.draw.rect(surface, config.SHORTCUT_BG, bar, border_radius=6)
        pygame.draw.rect(surface, config.ACCENT_COLOR, bar, width=2, border_radius=6)

        op = self._input_op
        example = f"  ej: {op.example}" if op.example else ""
        line = (
            f"{op.prompt} {self._input_buffer}█{example}   "
            "[Enter] OK  [Esc] cancelar"
        )
        text = self._prompt_font.render(line, True, config.HIGHLIGHT_COLOR)
        max_w = bar.width - 16
        if text.get_width() > max_w:
            text = self._prompt_font.render(
                f"{op.prompt} {self._input_buffer}█", True, config.HIGHLIGHT_COLOR
            )
        surface.blit(text, text.get_rect(midleft=(bar.x + 10, bar.centery)))

    def progress(self) -> float:
        """Devuelve el progreso de la acción actual en rango [0, 1)."""
        if self.interactive and (self.live_op or self.step_mode):
            return self.live_progress()
        if not self.actions:
            return 0.0
        _, duration = self.actions[self.action_index]
        if duration == 0:
            return 0.0
        return min(self.action_timer / duration, 0.999)

    def draw_empty(
        self, surface: pygame.Surface, rect: pygame.Rect, text: str = "(vacío)"
    ) -> None:
        from ds_visualizer import config

        if self._font is None:
            self._init_font()
        lbl = self._font.render(text, True, config.SUBTEXT_COLOR)
        surface.blit(lbl, lbl.get_rect(center=rect.center))
