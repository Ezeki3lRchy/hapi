"""Shared academic/publication-style helpers for the CH4/HITRAN/ExoMol process figures.

Conventions
-----------
- Monochrome palette: emphasis via grayscale fill, not color.
- Thin strokes (0.7 pt boxes, 0.8 pt arrows, 1.2 pt output box).
- Sans-serif body with matching sans-serif mathtext (mathtext.fontset='dejavusans')
  so equations sit at the same visual weight as the surrounding labels.
- Subtle rounded corners (3 pt).
- Box types: 'input' (light gray, external data), 'emphasis' (medium gray, key
  physics step), 'process' (white, intermediate computation), 'output' (white
  with thicker border, final result).

All three figures (ch4_nu3_process_diagram, hitran_standard_workflow,
exomol_standard_workflow) share these helpers so they read as one visual family.
"""

from __future__ import annotations

from dataclasses import dataclass

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


mpl.rcParams["mathtext.fontset"] = "dejavusans"
mpl.rcParams["font.family"] = "DejaVu Sans"


BG_COLOR = "#ffffff"
TEXT_COLOR = "#111111"
SUBTITLE_COLOR = "#444444"
STROKE_COLOR = "#222222"
STROKE_COLOR_BOLD = "#000000"
ARROW_COLOR = "#000000"

PALETTE = {
    "input":    {"fc": "#f4f4f4", "ec": STROKE_COLOR,      "lw": 0.7},
    "emphasis": {"fc": "#e4e4e4", "ec": STROKE_COLOR_BOLD, "lw": 0.7},
    "process":  {"fc": "#ffffff", "ec": STROKE_COLOR,      "lw": 0.7},
    "output":   {"fc": "#ffffff", "ec": STROKE_COLOR_BOLD, "lw": 1.2},
}

BOX_ROUNDING = 3
PAD_X = 14
TITLE_FONTSIZE = 12.5
SUBTITLE_FONTSIZE = 9.5
BOX_TITLE_FONTSIZE = 10
MATH_FONTSIZE = 10


@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float
    style: str
    title: str
    math: str = ""
    subtitle: str = ""
    tag: str = ""      # optional prefix like "(a)", "3a.", etc.

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def top(self) -> float:
        return self.y + self.h

    @property
    def bottom(self) -> float:
        return self.y


def setup_figure(width: float, height: float):
    """Create a bare-canvas figure sized in pixels (100 dpi equivalent)."""
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_axis_off()
    fig.set_facecolor(BG_COLOR)
    return fig, ax


def draw_title(ax, x: float, y: float, title: str, subtitle: str = "") -> None:
    ax.text(
        x, y, title,
        ha="center", va="top",
        fontsize=TITLE_FONTSIZE, fontweight="bold", color=TEXT_COLOR,
    )
    if subtitle:
        ax.text(
            x, y - 22, subtitle,
            ha="center", va="top",
            fontsize=SUBTITLE_FONTSIZE, fontstyle="italic", color=SUBTITLE_COLOR,
        )


def draw_box(ax, box: Box) -> None:
    colors = PALETTE[box.style]
    patch = FancyBboxPatch(
        (box.x, box.y),
        box.w,
        box.h,
        boxstyle=f"round,pad=0.0,rounding_size={BOX_ROUNDING}",
        linewidth=colors["lw"],
        facecolor=colors["fc"],
        edgecolor=colors["ec"],
    )
    ax.add_patch(patch)

    title_text = f"{box.tag}  {box.title}".strip() if box.tag else box.title

    if box.math:
        ax.text(
            box.x + PAD_X, box.top - 14, title_text,
            ha="left", va="top",
            fontsize=BOX_TITLE_FONTSIZE, fontweight="bold", color=TEXT_COLOR,
        )
        if box.subtitle:
            ax.text(
                box.x + PAD_X, box.top - 28, box.subtitle,
                ha="left", va="top",
                fontsize=SUBTITLE_FONTSIZE, fontstyle="italic", color=SUBTITLE_COLOR,
            )
        ax.text(
            box.x + PAD_X, box.bottom + 12, box.math,
            ha="left", va="bottom",
            fontsize=MATH_FONTSIZE, color=TEXT_COLOR,
        )
    else:
        ax.text(
            box.x + PAD_X, box.y + box.h / 2, title_text,
            ha="left", va="center",
            fontsize=BOX_TITLE_FONTSIZE, fontweight="bold", color=TEXT_COLOR,
        )


def draw_arrow(ax, x0: float, y0: float, x1: float, y1: float) -> None:
    arrow = FancyArrowPatch(
        (x0, y0), (x1, y1),
        arrowstyle="-|>",
        mutation_scale=10,
        linewidth=0.8,
        color=ARROW_COLOR,
        shrinkA=0,
        shrinkB=0,
    )
    ax.add_patch(arrow)
