"""Panel de información: parsea y renderiza archivos markdown."""

import re
from pathlib import Path

import pygame
from ds_visualizer import config


class InfoPanel:
    """Carga un archivo .md y lo dibuja con formato en el panel izquierdo."""

    def __init__(self) -> None:
        self.scroll_y = 0.0
        self.max_scroll = 0
        self.content_surface = None
        self.content_height = 0
        self._visible_width = 0
        self._visible_height = 0
        self._title_font = None
        self._header_font = None
        self._text_font = None
        self._code_font = None
        self._small_font = None

    def _init_fonts(self) -> None:
        self._title_font = pygame.font.SysFont(
            config.FONT_FAMILY, config.FONT_SIZE_TITLE, bold=True
        )
        self._header_font = pygame.font.SysFont(
            config.FONT_FAMILY, config.FONT_SIZE_HEADER, bold=True
        )
        self._text_font = pygame.font.SysFont(
            config.FONT_FAMILY, config.FONT_SIZE_NORMAL
        )
        self._code_font = pygame.font.SysFont(
            config.FONT_FAMILY, config.FONT_SIZE_SMALL
        )
        self._small_font = pygame.font.SysFont(
            config.FONT_FAMILY, config.FONT_SIZE_SMALL
        )

    def load_markdown(self, filepath: str, visible_width: int, visible_height: int) -> None:
        self._init_fonts()
        self._visible_width = visible_width
        self._visible_height = visible_height
        self.scroll_y = 0.0

        content_width = visible_width - 2 * config.INFO_PANEL_PADDING
        blocks = self._parse_markdown(filepath)
        total_height = self._calculate_height(blocks, content_width)
        total_height += config.INFO_PANEL_PADDING * 2

        self.content_surface = pygame.Surface((visible_width, total_height))
        self.content_surface.fill(config.PANEL_BG)
        self.content_height = total_height
        self._render_blocks(blocks, content_width, total_height)
        self.max_scroll = max(0, total_height - visible_height)

    def scroll(self, dy: float) -> None:
        self.scroll_y = max(0.0, min(self.scroll_y + dy, self.max_scroll))

    def draw(self, screen: pygame.Surface, x: int, y: int) -> None:
        if self.content_surface is None:
            return

        clip_rect = pygame.Rect(x, y, self._visible_width, self._visible_height)
        screen.set_clip(clip_rect)
        src_rect = pygame.Rect(0, int(self.scroll_y), self._visible_width, self._visible_height)
        screen.blit(self.content_surface, (x, y - int(self.scroll_y)))
        screen.set_clip(None)

    def _parse_markdown(self, filepath: str) -> list[tuple[str, str]]:
        blocks: list[tuple[str, str]] = []
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].rstrip()

            if not line:
                blocks.append(("blank", ""))
                i += 1
                continue

            if line.startswith("### "):
                blocks.append(("subheader", line[4:]))
            elif line.startswith("## "):
                blocks.append(("header", line[3:]))
            elif line.startswith("# "):
                blocks.append(("title", line[2:]))
            elif line.startswith("- "):
                blocks.append(("list_item", line[2:]))
            elif line.startswith("```"):
                code_lines: list[str] = []
                i += 1
                while i < len(lines) and not lines[i].rstrip().startswith("```"):
                    code_lines.append(lines[i].rstrip())
                    i += 1
                blocks.append(("code", "\n".join(code_lines)))
            else:
                blocks.append(("text", line))

            i += 1

        return blocks

    def _calculate_height(self, blocks: list[tuple[str, str]], content_width: int) -> float:
        y = config.INFO_PANEL_PADDING

        for block_type, content in blocks:
            if block_type == "title":
                y += self._title_font.get_linesize() + 18
            elif block_type == "header":
                y += self._header_font.get_linesize() + 14
            elif block_type == "subheader":
                y += self._text_font.get_linesize() + 10
            elif block_type == "list_item":
                wrapped = self._wrap_text("• " + content, self._text_font, content_width - 20)
                y += len(wrapped) * self._text_font.get_linesize() + 2
            elif block_type == "text":
                wrapped = self._wrap_text(content, self._text_font, content_width)
                y += len(wrapped) * self._text_font.get_linesize() + 2
            elif block_type == "code":
                code_lines = content.split("\n")
                line_height = self._code_font.get_linesize()
                y += len(code_lines) * line_height + 16
            elif block_type == "blank":
                y += 10

        return y

    def _render_blocks(
        self, blocks: list[tuple[str, str]], content_width: int, total_height: int
    ) -> None:
        x_offset = config.INFO_PANEL_PADDING
        y = config.INFO_PANEL_PADDING

        for block_type, content in blocks:
            if block_type == "title":
                y = self._draw_title_block(content, x_offset, y)
            elif block_type == "header":
                y = self._draw_header_block(content, x_offset, y, self._header_font)
            elif block_type == "subheader":
                y = self._draw_header_block(
                    content, x_offset, y, self._text_font
                )
            elif block_type == "list_item":
                y = self._draw_wrapped_block(
                    "• " + content, x_offset + 10, y,
                    self._text_font, config.TEXT_COLOR, content_width - 20,
                )
            elif block_type == "text":
                y = self._draw_wrapped_block(
                    content, x_offset, y,
                    self._text_font, config.TEXT_COLOR, content_width,
                )
            elif block_type == "code":
                y = self._draw_code_block(content, x_offset, y, content_width)
            elif block_type == "blank":
                y += 10

    def _draw_title_block(self, text: str, x: int, y: int) -> float:
        surf = self._title_font.render(text, True, config.MENU_TITLE_COLOR)
        self.content_surface.blit(surf, (x, y))
        return y + self._title_font.get_linesize() + 18

    def _draw_header_block(
        self, text: str, x: int, y: int, font: pygame.font.Font
    ) -> float:
        surf = font.render(text, True, config.ACCENT_COLOR)
        self.content_surface.blit(surf, (x, y))
        return y + font.get_linesize() + 14

    def _draw_wrapped_block(
        self, text: str, x: int, y: int,
        font: pygame.font.Font, color: tuple[int, int, int],
        max_width: int,
    ) -> float:
        lines = self._wrap_text(text, font, max_width)
        line_height = font.get_linesize()
        for line in lines:
            surf = font.render(line, True, color)
            self.content_surface.blit(surf, (x, y))
            y += line_height
        return y + 2

    def _draw_code_block(
        self, code: str, x: int, y: int, max_width: int,
    ) -> float:
        code_lines = code.split("\n")
        line_height = self._code_font.get_linesize()

        block_height = len(code_lines) * line_height + 12
        block_rect = pygame.Rect(x - 4, y - 2, max_width + 2, block_height)
        pygame.draw.rect(
            self.content_surface, config.CODE_BG, block_rect, border_radius=4
        )

        y += 6
        for line in code_lines:
            surf = self._code_font.render(line, True, config.TEXT_COLOR)
            self.content_surface.blit(surf, (x + 4, y))
            y += line_height
        return y + 10

    @staticmethod
    def _wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        words = text.split(" ")
        lines: list[str] = []
        current_line: list[str] = []

        for word in words:
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                if font.size(word)[0] > max_width:
                    current_line = []
                    lines.append(word)
                else:
                    current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines if lines else [""]
