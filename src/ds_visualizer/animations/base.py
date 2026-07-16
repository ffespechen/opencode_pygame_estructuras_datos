"""Clase base para todas las animaciones de estructuras de datos."""

from __future__ import annotations

import re
from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class Operation:
    """Operación interactiva disparable por tecla.

    Si ``prompt`` no es None, antes de aplicar se pide texto al usuario.
    ``example`` se muestra como pista (ej. \"B F\").
    """

    key: int
    label: str
    op_id: str
    prompt: str | None = None
    example: str = ""


class BaseAnimation:
    """Interfaz común: demo automática + modo interactivo con operaciones."""

    LIVE_ANIM_DURATION = 0.85
    STATUS_DURATION = 2.8

    def __init__(self) -> None:
        self.action_index = 0
        self.action_timer = 0.0
        self.actions: list[tuple[str, float]] = []
        self.current_action = ""
        self._font = None
        self._prompt_font = None

        self.interactive = False
        self.operations: list[Operation] = []
        self.next_value = 100
        self.highlight_idx = -1
        self.highlight_set: set[int] = set()
        self.status_message = ""
        self._status_timer = 0.0
        self.live_op: str | None = None
        self._live_timer = 0.0

        # Entrada de texto para operaciones que piden datos
        self.input_active = False
        self._input_op: Operation | None = None
        self._input_buffer = ""

    def _init_font(self) -> None:
        self._font = pygame.font.SysFont("monospace", 14, bold=True)
        self._prompt_font = pygame.font.SysFont("monospace", 16, bold=True)

    def set_operations(self, ops: list[Operation]) -> None:
        self.operations = list(ops)

    def toggle_interactive(self) -> None:
        self.cancel_input()
        self.interactive = not self.interactive
        self.live_op = None
        self._live_timer = 0.0
        self.highlight_idx = -1
        self.highlight_set = set()
        if self.interactive:
            self.status_message = "Modo interactivo — teclas numéricas"
            self._status_timer = self.STATUS_DURATION
        else:
            self.reset()
            self.status_message = "Modo demo (automático)"
            self._status_timer = self.STATUS_DURATION
            self.action_timer = 0.0

    def reset(self) -> None:
        """Restaura el estado inicial. Las subclases deben sobrescribirlo."""
        self.cancel_input()
        self.next_value = 100
        self.highlight_idx = -1
        self.highlight_set = set()
        self.live_op = None
        self._live_timer = 0.0
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
        self._input_buffer = ""
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
        self.live_op = op.op_id
        self._live_timer = 0.0
        msg = self.apply_operation(op.op_id, text)
        self.status_message = msg or op.label
        self._status_timer = self.STATUS_DURATION
        self.current_action = self.status_message

    def handle_text(self, text: str) -> bool:
        """Recibe TEXTINPUT de pygame. Devuelve True si se consumió."""
        if not self.input_active:
            return False
        # Evitar que teclas de control se cuelen
        if text and text.isprintable() and text not in "\r\n\t":
            self._input_buffer += text
        return True

    def handle_key(self, key: int) -> bool:
        """Procesa teclas del modo interactivo. Devuelve True si se consumió."""
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
            # Las demás teclas las maneja TEXTINPUT
            return True

        if key == pygame.K_i:
            self.toggle_interactive()
            return True

        if key == pygame.K_r:
            if not self.interactive:
                self.interactive = True
            self.reset()
            return True

        matching = [op for op in self.operations if op.key == key]
        if not matching:
            return False

        if not self.interactive:
            self.interactive = True

        op = matching[0]
        if op.prompt is not None:
            self.begin_input(op)
            return True

        self.live_op = op.op_id
        self._live_timer = 0.0
        msg = self.apply_operation(op.op_id, None)
        self.status_message = msg or op.label
        self._status_timer = self.STATUS_DURATION
        self.current_action = self.status_message
        return True

    def live_progress(self) -> float:
        if not self.live_op:
            return 1.0
        return min(self._live_timer / self.LIVE_ANIM_DURATION, 0.999)

    def operations_hint(self) -> str:
        if not self.operations:
            return "I: modo interactivo"
        return "  ".join(
            f"{pygame.key.name(op.key).upper()}:{op.label}"
            for op in self.operations
        )

    def update(self, dt: float) -> None:
        if self.input_active:
            op = self._input_op
            example = f"  (ej: {op.example})" if op and op.example else ""
            prompt = op.prompt if op else "Valor"
            self.current_action = f"{prompt} {self._input_buffer}█{example}"
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
        line = f"{op.prompt} {self._input_buffer}█{example}   [Enter] OK  [Esc] cancelar"
        text = self._prompt_font.render(line, True, config.HIGHLIGHT_COLOR)
        # Recortar si es muy largo
        max_w = bar.width - 16
        if text.get_width() > max_w:
            text = self._prompt_font.render(
                f"{op.prompt} {self._input_buffer}█", True, config.HIGHLIGHT_COLOR
            )
        surface.blit(text, text.get_rect(midleft=(bar.x + 10, bar.centery)))

    def progress(self) -> float:
        """Devuelve el progreso de la acción actual en rango [0, 1)."""
        if self.interactive and self.live_op:
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
