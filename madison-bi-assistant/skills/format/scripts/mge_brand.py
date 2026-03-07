"""
MGE Brand Constants — Single source of truth for all document generation.

Every colour, font size, spacing value, and number format used by mge_excel.py
and mge_word.py is defined here. No openpyxl or python-docx imports — those
live in the format-specific modules. This module is pure data.

Design rationale is documented inline. Key references:
- MGE Brand Governance PDF (Identity section, pages 20-32)
- Enterprise design specification (scratch/design-docs/)
- WCAG 2.1 contrast analysis (Connect Grey 7.96:1 on white — exceeds AAA)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ─── Colour System ──────────────────────────────────────────────────────────
#
# Two representations: aRGB strings for openpyxl (FF prefix), RGB tuples for
# python-docx RGBColor(). HEX strings without prefix for general use.
#
# Connect Grey #3F5364 is the primary brand colour. WCAG AAA on white (7.96:1).
# Accent Red #CF152D is accent only — negatives and alerts, never dominant.
# CG 50% #9FA9B2 FAILS all WCAG text requirements (2.39:1) — borders/decoration only.


@dataclass(frozen=True)
class Colour:
    """A brand colour with all format representations pre-computed."""

    name: str
    hex: str  # 6-char hex without prefix, e.g. "3F5364"
    rgb: tuple[int, int, int]
    argb: str  # 8-char aRGB for openpyxl, e.g. "FF3F5364"

    @staticmethod
    def from_hex(name: str, hex_str: str) -> "Colour":
        h = hex_str.lstrip("#")
        return Colour(
            name=name,
            hex=h,
            rgb=(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)),
            argb=f"FF{h}",
        )


# Primary palette (from brand PDF)
CONNECT_GREY = Colour.from_hex("Connect Grey", "3F5364")
ACCENT_RED = Colour.from_hex("Accent Red", "CF152D")
SATIN_GREY = Colour.from_hex("Satin Grey", "E4E5E6")
DARK_GREY = Colour.from_hex("Dark Grey", "243747")
CONNECT_GREY_50 = Colour.from_hex("50% Connect Grey", "9FA9B2")

# Extended tints (derived from primaries)
CONNECT_GREY_30 = Colour.from_hex("30% Connect Grey", "B9C1C8")
CONNECT_GREY_20 = Colour.from_hex("20% Connect Grey", "D9DDE1")
CONNECT_GREY_10 = Colour.from_hex("10% Connect Grey", "ECEEF0")
CONNECT_GREY_05 = Colour.from_hex("5% Connect Grey", "F5F6F7")
ACCENT_RED_30 = Colour.from_hex("30% Accent Red", "F2B5BC")
ACCENT_RED_20 = Colour.from_hex("20% Accent Red", "F8D0D5")
ACCENT_RED_10 = Colour.from_hex("10% Accent Red", "FCE8EA")
DARK_GREY_80 = Colour.from_hex("80% Dark Grey", "3E4F5C")

# Neutrals
WHITE = Colour.from_hex("White", "FFFFFF")
BLACK = Colour.from_hex("Black", "000000")

# Chart colour sequence — cycle through in this order for multi-series charts.
# Binary charts: CONNECT_GREY = positive, ACCENT_RED = negative.
CHART_COLOURS = [CONNECT_GREY, ACCENT_RED, CONNECT_GREY_50, SATIN_GREY, DARK_GREY, CONNECT_GREY_30]

# Sheet tab colours by purpose
TAB_COLOUR_SUMMARY = ACCENT_RED.hex      # Dashboard / summary tabs
TAB_COLOUR_DATA = CONNECT_GREY.hex       # Data / detail tabs
TAB_COLOUR_INPUT = CONNECT_GREY_50.hex   # Input / assumptions tabs
TAB_COLOUR_REF = SATIN_GREY.hex          # Reference / lookup tabs


# ─── Typography ─────────────────────────────────────────────────────────────
#
# Brand font: Hurme Geometric Sans (commercial, not available programmatically).
# Automated output: Arial throughout — explicitly named as fallback in brand PDF.
#
# Word type scale: Major Third ratio (1.25). Conservative, enterprise-appropriate.
#   10pt body → 13pt H3 → 16pt H2 → 20pt H1 → 28pt Title
#   Why 1.25: banks, law firms, enterprise tech use 1.125-1.25. The 1.333 ratio
#   creates size jumps too large for data-dense financial reports.
#
# Excel type scale: Tighter 1.2 ratio to fit row height constraints.
#   9pt body → 11pt section → 14pt title

FONT_NAME = "Arial"

# Word type scale (sizes in points)
@dataclass(frozen=True)
class TypeLevel:
    """A level in the type scale with all properties."""
    size_pt: float
    bold: bool
    colour: Colour
    space_before_pt: float = 0
    space_after_pt: float = 0
    line_spacing: float = 1.15  # Multiple


WORD_TITLE = TypeLevel(28, True, CONNECT_GREY, 0, 12)
WORD_SUBTITLE = TypeLevel(16, False, CONNECT_GREY_50, 0, 24)
WORD_H1 = TypeLevel(20, True, CONNECT_GREY, 24, 8, 1.0)
WORD_H2 = TypeLevel(16, True, CONNECT_GREY, 18, 6, 1.0)
WORD_H3 = TypeLevel(13, True, DARK_GREY, 14, 4, 1.0)
WORD_H4 = TypeLevel(11, True, DARK_GREY, 10, 4, 1.0)
WORD_BODY = TypeLevel(10.5, False, BLACK, 0, 6)
WORD_BODY_SMALL = TypeLevel(9.5, False, BLACK, 0, 4)
WORD_CAPTION = TypeLevel(9, False, CONNECT_GREY_50, 4, 2)
WORD_FOOTNOTE = TypeLevel(8, False, CONNECT_GREY_50, 0, 2)
WORD_TABLE_HEADER = TypeLevel(10, True, WHITE)
WORD_TABLE_BODY = TypeLevel(9.5, False, BLACK)
WORD_TABLE_TOTAL = TypeLevel(10, True, BLACK)
WORD_CALLOUT_TITLE = TypeLevel(11, True, CONNECT_GREY, 6, 4)
WORD_CALLOUT_BODY = TypeLevel(10, False, DARK_GREY, 0, 4)
WORD_KPI_VALUE = TypeLevel(24, True, CONNECT_GREY, 0, 2)
WORD_KPI_LABEL = TypeLevel(9, False, CONNECT_GREY_50, 0, 0)

# Excel type scale (sizes in points)
EXCEL_TITLE = TypeLevel(14, True, CONNECT_GREY)
EXCEL_SUBTITLE = TypeLevel(10, False, CONNECT_GREY_50)
EXCEL_SECTION = TypeLevel(11, True, DARK_GREY)
EXCEL_HEADER = TypeLevel(9, True, WHITE)
EXCEL_BODY = TypeLevel(9, False, BLACK)
EXCEL_TOTAL = TypeLevel(9, True, BLACK)
EXCEL_SUBTOTAL = TypeLevel(9, True, CONNECT_GREY)
EXCEL_NEGATIVE = TypeLevel(9, False, ACCENT_RED)
EXCEL_FOOTER = TypeLevel(8, False, CONNECT_GREY_50)


# ─── Spacing & Layout ──────────────────────────────────────────────────────
#
# Word: margins in inches (python-docx Inches()), spacing in points (Pt()).
# Excel: row heights in points, column widths in character units.
# DXA = twentieths of a point (used in OOXML). 1 inch = 1440 DXA.

# Word page layout (A4 portrait)
WORD_PAGE_WIDTH_DXA = 11906       # A4 width
WORD_PAGE_HEIGHT_DXA = 16838      # A4 height
WORD_MARGIN_INCHES = 1.0          # 2.54cm — all four sides
WORD_CONTENT_WIDTH_DXA = 9026     # 11906 - 2*1440
WORD_HEADER_DIST_DXA = 720        # 12mm from page edge
WORD_FOOTER_DIST_DXA = 720

# Excel page layout (A4)
EXCEL_MARGIN_LEFT = 0.7           # inches
EXCEL_MARGIN_RIGHT = 0.7
EXCEL_MARGIN_TOP = 0.75
EXCEL_MARGIN_BOTTOM = 0.75
EXCEL_MARGIN_HEADER = 0.3
EXCEL_MARGIN_FOOTER = 0.3

# Excel row heights (points) — the primary vertical padding mechanism.
# Default auto-height (12.75pt) looks cramped. 18-20pt is the modern standard
# for 9pt data text, giving ~3-4pt padding top/bottom.
EXCEL_ROW_HEIGHT_DATA = 18.0
EXCEL_ROW_HEIGHT_HEADER = 24.0
EXCEL_ROW_HEIGHT_TITLE = 30.0
EXCEL_ROW_HEIGHT_SPACER = 6.0

# Excel sheet structure — standard layout
EXCEL_TITLE_ROW = 2        # Row 1 is blank (breathing room)
EXCEL_SUBTITLE_ROW = 3
EXCEL_HEADER_ROW = 5       # Row 4 is blank separator
EXCEL_DATA_START_ROW = 6
EXCEL_LABEL_COL = 2        # Column A (1) is blank left margin; data starts col B (2)


# ─── Number Formats ─────────────────────────────────────────────────────────
#
# Australian conventions: comma for thousands, period for decimal, DD/MM dates.
#
# CRITICAL: Never use [Red] or [Color] codes in format strings — they override
# cell font colour with Excel's built-in red, not our brand Accent Red #CF152D.
# Apply negative colour via conditional formatting or cell-level font colour.

NUM_FMT_CURRENCY = '$#,##0'
NUM_FMT_CURRENCY_DETAIL = '$#,##0.00'
NUM_FMT_CURRENCY_NEG = '$#,##0;($#,##0)'          # Parentheses, no colour code
NUM_FMT_CURRENCY_DETAIL_NEG = '$#,##0.00;($#,##0.00)'
NUM_FMT_CURRENCY_K = '$#,##0,"K"'                  # Thousands
NUM_FMT_CURRENCY_M = '$#,##0.0,,"M"'               # Millions
NUM_FMT_CURRENCY_DYNAMIC = '[>=1000000]$#,##0.0,,"M";[>=1000]$#,##0.0,"K";$#,##0'
NUM_FMT_ACCOUNTING = '_($* #,##0_);_($* (#,##0);_($* "-"_);_(@_)'
NUM_FMT_PCT = '0.0%'
NUM_FMT_PCT_PRECISE = '0.00%'
NUM_FMT_PCT_NEG = '0.0%;(0.0%)'
NUM_FMT_VARIANCE_PCT = '+0.0%;(0.0%);"-"'
NUM_FMT_INTEGER = '#,##0'
NUM_FMT_DECIMAL = '#,##0.00'
NUM_FMT_RATIO = '0.0"x"'
NUM_FMT_DATE = 'DD/MM/YYYY'
NUM_FMT_DATE_SHORT = 'DD/MM/YY'
NUM_FMT_DATE_DISPLAY = 'DD MMM YYYY'
NUM_FMT_MONTH_YEAR = 'MMM YYYY'


# ─── Border Weights ─────────────────────────────────────────────────────────
#
# Three-tier system:
#   Decorative (cell dividers): CG 20% — visible but unobtrusive
#   Structural (section dividers, table outlines): CG 50%
#   Emphatic (totals, key separators): full Connect Grey
#
# Minimum 0.5pt for any border that must survive printing (laser printers).
# "hair" style in openpyxl is unreliable in print — use "thin" minimum.

BORDER_COLOUR_DECORATIVE = CONNECT_GREY_20
BORDER_COLOUR_STRUCTURAL = CONNECT_GREY_50
BORDER_COLOUR_EMPHATIC = CONNECT_GREY


# ─── Trend Indicators ──────────────────────────────────────────────────────
#
# Filled triangles render reliably in Arial across Excel, Word, and PDF.
# No Wingdings (font-dependent), no emoji (unprofessional, fixed colour).

TREND_UP = "\u25B2"       # ▲ — positive change, Connect Grey bold
TREND_DOWN = "\u25BC"     # ▼ — negative change, Accent Red bold
TREND_FLAT = "\u2014"     # — (em dash) — no change, muted grey


# ─── Font Metrics (Arial) ──────────────────────────────────────────────────
#
# Per-character width lookup for estimating Excel column widths without a
# rendering engine. Values are relative widths normalised so that the digit
# "0" = 1.0 (since openpyxl measures column width in "0"-character units).
#
# Source: Arial TrueType metrics at 96 DPI, verified against the enterprise
# design specification. ~6% estimation error vs ~17% from constant average.

ARIAL_CHAR_WIDTHS: dict[str, float] = {
    # Narrow characters (~0.35-0.45 of "0")
    "i": 0.37, "j": 0.37, "l": 0.37, "!": 0.37, ":": 0.37, ";": 0.37,
    ".": 0.37, ",": 0.37, "'": 0.24, '"': 0.47, "|": 0.37, "I": 0.37,
    "f": 0.45, "r": 0.52, "t": 0.45, " ": 0.45,
    "(": 0.45, ")": 0.45, "[": 0.45, "]": 0.45, "{": 0.45, "}": 0.45,

    # Medium characters (~0.60-0.75 of "0")
    "a": 0.72, "b": 0.72, "c": 0.66, "d": 0.72, "e": 0.72,
    "g": 0.72, "h": 0.72, "k": 0.66, "n": 0.72, "o": 0.72,
    "p": 0.72, "q": 0.72, "s": 0.60, "u": 0.72, "v": 0.66,
    "x": 0.66, "y": 0.66, "z": 0.60,

    # Digits — all equal width (tabular figures in Arial)
    "0": 1.00, "1": 1.00, "2": 1.00, "3": 1.00, "4": 1.00,
    "5": 1.00, "6": 1.00, "7": 1.00, "8": 1.00, "9": 1.00,

    # Wide characters
    "m": 1.07, "w": 1.00, "M": 1.07, "W": 1.14,
    "A": 0.86, "B": 0.79, "C": 0.86, "D": 0.86, "E": 0.72,
    "F": 0.66, "G": 0.93, "H": 0.86, "J": 0.52, "K": 0.79,
    "L": 0.66, "N": 0.86, "O": 0.93, "P": 0.72, "Q": 0.93,
    "R": 0.79, "S": 0.72, "T": 0.72, "U": 0.86, "V": 0.79,
    "X": 0.79, "Y": 0.72, "Z": 0.72,

    # Common symbols
    "$": 0.72, "%": 1.14, "&": 0.86, "@": 1.21, "#": 0.72,
    "+": 0.75, "-": 0.45, "=": 0.75, "/": 0.45, "\\": 0.45,
    "_": 0.72, "~": 0.75, "^": 0.75, "*": 0.52, "<": 0.75,
    ">": 0.75,
}

# Default width for characters not in the lookup
ARIAL_CHAR_WIDTH_DEFAULT = 0.72


def estimate_text_width(
    text: str,
    font_size: float = 9.0,
    bold: bool = False,
    padding_chars: float = 2.0,
) -> float:
    """
    Estimate Excel column width in character units for a given text string.

    Uses per-character Arial metrics. Returns width in openpyxl column-width
    units (approximately number of "0" characters). Add padding_chars for
    breathing room (2-4 recommended).

    Args:
        text: The string to measure.
        font_size: Font size in points. Base reference is 11pt.
        bold: Whether text is bold (adds ~10% width).
        padding_chars: Extra character units for breathing room.

    Returns:
        Estimated column width in openpyxl character units.
    """
    raw = sum(ARIAL_CHAR_WIDTHS.get(c, ARIAL_CHAR_WIDTH_DEFAULT) for c in str(text))
    # Scale relative to openpyxl's reference size (11pt)
    scaled = raw * (font_size / 11.0)
    if bold:
        scaled *= 1.1
    return scaled + padding_chars


def estimate_column_width(
    values: list[str],
    header: str = "",
    font_size: float = 9.0,
    header_bold: bool = True,
    min_width: float = 8.0,
    max_width: float = 50.0,
    padding_chars: float = 2.5,
) -> float:
    """
    Estimate optimal column width for a list of cell values plus header.

    Finds the maximum width across all values and the header, clamped to
    min/max bounds.
    """
    widths = [estimate_text_width(v, font_size, False, padding_chars) for v in values]
    if header:
        widths.append(estimate_text_width(header, font_size, header_bold, padding_chars))
    if not widths:
        return min_width
    return max(min_width, min(max(widths), max_width))


# ─── Logo Path Resolution ──────────────────────────────────────────────────
#
# Logo PNGs live in assets/logos/ relative to this script. All at 300 DPI,
# RGBA, standardised names. Scripts must handle missing files gracefully
# (placeholder text, not crash).

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "logos"

# Known logo files
_LOGO_MAP: dict[str, str] = {
    # Colour variants
    "mge": "mge-colour.png",
    "mge-wide": "mge-colour-wide.png",
    "mav": "mav-colour.png",
    "mex": "mex-colour.png",
    "mt": "mt-colour.png",
    "mcs": "mcs-colour.png",
    "kallipr": "kallipr-colour.png",
    # Grey variants
    "mge-grey": "mge-grey.png",
    "mav-grey": "mav-grey.png",
    "mex-grey": "mex-grey.png",
    "mt-grey": "mt-grey.png",
    "mcs-grey": "mcs-grey.png",
    "kallipr-grey": "kallipr-grey.png",
    # Corner device (L-shape brand element for cover pages)
    "corner-device-red": "corner-device-red.png",
    "corner-device-white": "corner-device-white.png",
}


def logo_path(brand: str, grey: bool = False) -> Optional[Path]:
    """
    Resolve a brand logo file path. Returns None if the file doesn't exist.

    Args:
        brand: Brand key — "mge", "mav", "mex", "mt", "mcs", "kallipr".
                Use "mge-wide" for the horizontal MGE logo (cover pages).
        grey: If True, return the grey variant (headers/footers on white).

    Returns:
        Path to the PNG file, or None if not found.
    """
    key = brand.lower().strip()
    if grey and not key.endswith("-grey") and key != "mge-wide":
        key = f"{key}-grey"
    filename = _LOGO_MAP.get(key)
    if filename is None:
        return None
    path = _ASSETS_DIR / filename
    return path if path.exists() else None


def logo_path_str(brand: str, grey: bool = False) -> Optional[str]:
    """Same as logo_path() but returns a string path, or None."""
    p = logo_path(brand, grey)
    return str(p) if p else None


# ─── Convenience Aliases ────────────────────────────────────────────────────
#
# For quick access in generated scripts without importing individual constants.

COLOURS = {
    "connect_grey": CONNECT_GREY,
    "accent_red": ACCENT_RED,
    "satin_grey": SATIN_GREY,
    "dark_grey": DARK_GREY,
    "cg50": CONNECT_GREY_50,
    "cg30": CONNECT_GREY_30,
    "cg20": CONNECT_GREY_20,
    "cg10": CONNECT_GREY_10,
    "cg05": CONNECT_GREY_05,
    "red30": ACCENT_RED_30,
    "red20": ACCENT_RED_20,
    "red10": ACCENT_RED_10,
    "white": WHITE,
    "black": BLACK,
}

# Version — bumped when constants change
__version__ = "1.0.0"
