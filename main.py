#!/usr/bin/env python3
"""Sum up 19 November 2026 world news in one image.

make.fun bounty news-image-20261119, round-2 revision.
Python 3.13, standard library only, no network, deterministic.
Draws a 1024x1024 PNG newspaper front page and writes it to
/output/entry.png (or output/entry.png when /output does not exist).

News facts, researched 19 Nov 2026 from reputable reports:
- Donald Trump, Xi Jinping and Vladimir Putin held the first
  trilateral summit of the three leaders in Shenzhen, on the
  sidelines of APEC. Ukraine dominated the Trump-Putin talks.
- The International Court of Justice rules on the genocide case
  Gambia brought against Myanmar over the 2017 crackdown that
  drove 730,000+ Rohingya into Bangladesh. No state has ever
  been found guilty of genocide by an international court.
- Ukraine struck the Crimean Bridge for the third time in a
  week; traffic was suspended.
- Kuwait repelled an Iranian attack, the first in two months,
  and Bahrain was targeted too, after US jets struck a missile
  site on Iran's Qeshm Island. The IEA called the Hormuz crisis
  the greatest threat ever to energy security.
- Bangladesh: Muhammad Yunus's ancestral home was set on fire;
  violence spread to 28 districts, with dozens of bomb blasts
  and burned vehicles in ten days.
- COP31: ministers met in Antalya to unblock climate talks.
- Van Gogh's "Chestnut Trees in Flower" sold at Sotheby's for
  USD 190.4M, a record for the artist.
- IAEA: North Korea expanded uranium enrichment at Yongbyon.
- EU proposed a EUR 45BN loan to fund Ukraine in 2027.
- Anthropic priced its IPO at USD 83 a share, set to raise
  USD 81.3BN, a record debut.
- Fiji declared a national state of disaster over El Nino drought.
- Markets at the 19 Nov close: SP 500 7,323.63 -0.23%, Nasdaq
  24,429.88 +0.42%, gold USD 3,739.60, Brent USD 89.59 -2.57%,
  VIX 24.56.

Rendering is a small rasteriser written for this program. The
5x7 bitmap font is stored as seven 5-character strings per
glyph ('#' = ink, ' ' = blank) and compiled to row masks at
import, so the program needs no external files, fonts or
packages.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# --- palette ---
PAPER = (252, 250, 244)
INK = (18, 18, 18)
GREY = (96, 96, 96)
FAINT = (228, 226, 218)
RED = (178, 34, 34)
NAVY = (22, 48, 88)
GOLD = (201, 162, 39)
SKY = (168, 203, 232)
SEA = (44, 92, 128)
GREEN = (46, 110, 70)
DUSK = (28, 38, 58)
STONE = (210, 205, 190)
WOOD = (139, 90, 43)

# --- 5x7 bitmap font: seven 5-char rows per glyph ---
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ### ", "#   #", "#    ", "#  ##", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": (" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "a": ("     ", "     ", " ### ", "    #", " ####", "#   #", " ####"),
    "b": ("#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#### "),
    "c": ("     ", "     ", " ### ", "#    ", "#    ", "#   #", " ### "),
    "d": ("    #", "    #", " ####", "#   #", "#   #", "#   #", " ####"),
    "e": ("     ", "     ", " ### ", "#   #", "#####", "#    ", " ### "),
    "f": ("  ## ", " #  #", " #   ", "#### ", " #   ", " #   ", " #   "),
    "g": ("     ", " ####", "#   #", "#   #", " ####", "    #", " ### "),
    "h": ("#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#   #"),
    "i": ("  #  ", "     ", " ##  ", "  #  ", "  #  ", "  #  ", " ### "),
    "j": ("   # ", "     ", "  ## ", "   # ", "   # ", "#  # ", " ##  "),
    "k": ("#    ", "#    ", "#  # ", "# #  ", "##   ", "# #  ", "#  # "),
    "l": (" ##  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "m": ("     ", "     ", "## # ", "# # #", "# # #", "# # #", "# # #"),
    "n": ("     ", "     ", "#### ", "#   #", "#   #", "#   #", "#   #"),
    "o": ("     ", "     ", " ### ", "#   #", "#   #", "#   #", " ### "),
    "p": ("     ", "     ", "#### ", "#   #", "#   #", "#### ", "#    "),
    "q": ("     ", "     ", " ####", "#   #", "#   #", " ####", "    #"),
    "r": ("     ", "     ", "# ## ", "##  #", "#    ", "#    ", "#    "),
    "s": ("     ", "     ", " ####", "#    ", " ### ", "    #", "#### "),
    "t": (" #   ", " #   ", "###  ", " #   ", " #   ", " #  #", "  ## "),
    "u": ("     ", "     ", "#   #", "#   #", "#   #", "#  ##", " ## #"),
    "v": ("     ", "     ", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "w": ("     ", "     ", "#   #", "# # #", "# # #", "# # #", " # # "),
    "x": ("     ", "     ", "#   #", " # # ", "  #  ", " # # ", "#   #"),
    "y": ("     ", "     ", "#   #", "#   #", " ####", "    #", " ### "),
    "z": ("     ", "     ", "#####", "   # ", "  #  ", " #   ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "  ## ", " #   ", "#    ", "#####"),
    "3": ("#####", "   # ", "  #  ", "   # ", "    #", "#   #", " ### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": ("  ## ", " #   ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "   # ", " ##  "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", "  #  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", "  #  ", " #   "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    '"': (" # # ", " # # ", "     ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "?": (" ### ", "#   #", "    #", "  ## ", "  #  ", "     ", "  #  "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "/": ("    #", "   # ", "   # ", "  #  ", " #   ", " #   ", "#    "),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ## ", "#  ##"),
    "|": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
}
_BLANK = ("     ", "     ", "     ", "     ", "     ", "     ", "     ")

# Compile the string patterns into 5-bit row masks once, at import.
_MASKS = {}
for _ch, _rows in FONT.items():
    _MASKS[_ch] = tuple(
        sum((1 << (4 - _i)) for _i, _p in enumerate(_row) if _p == "#")
        for _row in _rows
    )


# --- canvas: a small rasteriser held in one class ---
class Page:
    def __init__(self, w, h, paper):
        self.w, self.h = w, h
        self.pix = bytearray(paper * w * h)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = (y * self.w + x) * 3
            self.pix[o], self.pix[o + 1], self.pix[o + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, c)

    def hline(self, x, y, w, c=INK):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c=INK):
        self.rect(x, y, 1, h, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.px(xx, yy, c)

    def ring(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if abs(d - r * r) <= r:
                    self.px(xx, yy, c)

    def line(self, x0, y0, x1, y1, c):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.px(round(x0 + (x1 - x0) * i / n),
                    round(y0 + (y1 - y0) * i / n), c)

    def text(self, x, y, s, size, c):
        """Draw text left-aligned; return pixel width used."""
        cx = x
        for ch in s:
            rows = _MASKS.get(ch)
            if rows is None:
                rows = _MASKS.get(" ", (0, 0, 0, 0, 0, 0, 0))
            for r, mask in enumerate(rows):
                for col in range(5):
                    if mask >> (4 - col) & 1:
                        self.rect(cx + col * size, y + r * size,
                                  size, size, c)
            cx += 6 * size
        return cx - x

    @staticmethod
    def text_w(s, size):
        return len(s) * 6 * size

    def wrap(self, s, max_w, size):
        out, cur = [], ""
        for word in s.split(" "):
            trial = (cur + " " + word).strip()
            if self.text_w(trial, size) <= max_w:
                cur = trial
            else:
                if cur:
                    out.append(cur)
                cur = word
        if cur:
            out.append(cur)
        return out

    def para(self, x, y, s, max_w, size, c, leading=None):
        leading = leading if leading is not None else 9 * size
        for ln in self.wrap(s, max_w, size):
            self.text(x, y, ln, size, c)
            y += leading
        return y

    def head(self, x, y, s, max_w, size=3):
        yy = y
        for ln in self.wrap(s, max_w, size):
            self.text(x, yy, ln, size, INK)
            yy += 10 * size
        return yy

    def kicker(self, x, y, s, c=RED):
        return self.text(x, y, s, 2, c)


# --- illustrations, all drawn, no photos ---
def ill_summit(pg, x, y, w, h):
    pg.rect(x, y, w, h, SKY)
    pg.circle(x + w - 56, y + 28, 16, GOLD)
    pg.ring(x + w - 56, y + 28, 22, (240, 220, 160))
    # stepped skyline, windows lit
    towers = ((30, 52), (74, 88), (118, 64), (162, 96), (206, 70),
              (250, 84), (294, 58), (338, 92), (382, 66), (426, 80))
    for bx, bh in towers:
        pg.rect(x + bx, y + h - 30 - bh, 34, bh + 30, NAVY)
        for wy in range(y + h - 24 - bh, y + h - 36, 12):
            for wx in range(x + bx + 5, x + bx + 29, 10):
                pg.rect(wx, wy, 4, 5, GOLD)
    # summit table with three chairs in front
    pg.rect(x, y + h - 30, w, 30, (58, 58, 58))
    pg.rect(x + 40, y + h - 52, w - 80, 22, (96, 60, 36))
    for cx in (x + 70, x + w // 2, x + w - 70):
        pg.rect(cx - 16, y + h - 44, 32, 12, (30, 30, 30))
        pg.rect(cx - 16, y + h - 30, 4, 30, (30, 30, 30))
        pg.rect(cx + 12, y + h - 30, 4, 30, (30, 30, 30))


def ill_scales(pg, x, y, w, h):
    pg.rect(x, y, w, h, NAVY)
    # courthouse pediment
    pg.line(x + 12, y + 34, x + w // 2, y + 8, STONE)
    pg.line(x + w // 2, y + 8, x + w - 12, y + 34, STONE)
    pg.line(x + 12, y + 34, x + w - 12, y + 34, STONE)
    pg.circle(x + w // 2, y + 22, 5, GOLD)
    # scales of justice: post, beam, two pans
    cx = x + w // 2
    pg.vline(cx, y + 34, h - 44, STONE)
    pg.hline(cx - 52, y + 40, 104, STONE)
    pg.line(cx - 52, y + 40, cx - 66, y + 58, STONE)
    pg.line(cx + 52, y + 40, cx + 66, y + 58, STONE)
    pg.line(cx - 52, y + 40, cx - 38, y + 58, STONE)
    pg.line(cx + 52, y + 40, cx + 38, y + 58, STONE)
    pg.rect(cx - 74, y + 58, 28, 4, GOLD)
    pg.rect(cx + 46, y + 58, 28, 4, GOLD)
    pg.rect(cx - 40, y + h - 12, 80, 5, STONE)


def ill_bridge(pg, x, y, w, h):
    pg.rect(x, y, w, h, SKY)
    pg.circle(x + 34, y + 14, 11, GOLD)
    sea_y = y + h - 16
    pg.rect(x, sea_y, w, 16, SEA)
    for wx in range(x + 6, x + w - 6, 26):
        pg.line(wx, sea_y + 5, wx + 12, sea_y + 9, (130, 175, 215))
        pg.line(wx + 12, sea_y + 9, wx + 24, sea_y + 5, (130, 175, 215))
    # two towers with a broken middle span
    deck_y = y + h - 28
    for tx in (x + 52, x + w - 62):
        pg.rect(tx, y + 8, 10, deck_y - y - 8, (70, 70, 70))
        pg.rect(tx - 4, y + 4, 18, 6, (70, 70, 70))
    pg.rect(x, deck_y, w // 2 - 30, 6, (88, 88, 88))
    pg.rect(x + w // 2 + 30, deck_y, w // 2 - 30, 6, (88, 88, 88))
    # fallen span, tilted into the water
    pg.line(x + w // 2 - 28, deck_y + 3, x + w // 2 + 14, y + h - 4,
            (66, 66, 66))
    pg.line(x + w // 2 + 28, deck_y + 3, x + w // 2 - 10, y + h - 2,
            (66, 66, 66))
    # suspension cables from each tower to its span
    pg.line(x + 57, y + 8, x + 10, deck_y, (110, 110, 110))
    pg.line(x + 57, y + 8, x + w // 2 - 32, deck_y, (110, 110, 110))
    pg.line(x + w - 57, y + 8, x + w // 2 + 32, deck_y, (110, 110, 110))
    pg.line(x + w - 57, y + 8, x + w - 10, deck_y, (110, 110, 110))


def ill_gulf(pg, x, y, w, h):
    pg.rect(x, y, w, h, DUSK)
    pg.circle(x + w - 46, y + 14, 11, (228, 228, 216))
    sea_y = y + h // 2 + 4
    pg.rect(x, sea_y, w, h - sea_y, SEA)
    for wx in range(x + 8, x + w - 8, 34):
        pg.hline(wx, sea_y + 8 + (wx % 3) * 4, 18, (120, 170, 210))
    # missile trail arcing over the water
    for t in range(0, 61):
        ax = x + 20 + t * 3
        ay = y + 26 - int(14 * (t / 60.0) * (1 - t / 60.0) * 4)
        pg.px(ax, ay, (240, 180, 60))
        pg.px(ax, ay + 1, (220, 120, 40))
    pg.circle(x + w - 60, y + 12, 5, (240, 180, 60))
    # tanker silhouette with a flare on the horizon
    pg.rect(x + 24, y + h - 16, 120, 10, INK)
    pg.rect(x + 44, y + h - 30, 34, 14, INK)
    pg.rect(x + 96, y + h - 26, 10, 10, INK)
    pg.circle(x + 2 * w // 3, y + h - 14, 12, (220, 120, 40))
    pg.circle(x + 2 * w // 3, y + h - 20, 7, (240, 180, 60))


def ill_fire(pg, x, y, w, h):
    pg.rect(x, y, w, h, (240, 224, 200))
    # smoke curls above the roof
    pg.circle(x + w // 2 - 14, y + 8, 5, (150, 145, 135))
    pg.circle(x + w // 2 + 6, y + 5, 6, (170, 165, 155))
    pg.circle(x + w // 2 + 22, y + 9, 4, (150, 145, 135))
    # house body and pitched roof, drawn with double lines
    pg.rect(x + 24, y + h - 22, w - 48, 22, (120, 90, 70))
    pg.line(x + 24, y + h - 22, x + w // 2, y + 12, (90, 60, 44))
    pg.line(x + 24, y + h - 20, x + w // 2, y + 14, (90, 60, 44))
    pg.line(x + w // 2, y + 12, x + w - 24, y + h - 22, (90, 60, 44))
    pg.line(x + w // 2, y + 14, x + w - 24, y + h - 20, (90, 60, 44))
    pg.rect(x + w // 2 - 8, y + h - 16, 16, 16, (60, 40, 28))
    pg.rect(x + 34, y + h - 16, 12, 16, (60, 40, 28))
    pg.rect(x + w - 46, y + h - 16, 12, 16, (60, 40, 28))
    # flame licking out of the roof
    pg.circle(x + w // 2, y + h - 30, 15, (230, 120, 30))
    pg.circle(x + w // 2, y + h - 23, 9, (245, 190, 60))
    pg.circle(x + w // 2, y + h - 17, 5, (250, 230, 120))


# --- page layout ---
pg = Page(W, H, PAPER)
pg.hline(24, 14, W - 48)
pg.hline(24, 18, W - 48)

# masthead
_title = "THE WORLD TODAY"
pg.text((W - Page.text_w(_title, 5)) // 2, 30, _title, 5, INK)
pg.hline(24, 82, W - 48, RED)
pg.hline(24, 86, W - 48, RED)
_dateline = "THURSDAY, 19 NOVEMBER 2026  |  NO. 19  |  PAGE 1"
pg.text((W - Page.text_w(_dateline, 2)) // 2, 98, _dateline, 2, INK)
pg.hline(24, 118, W - 48)

# LEAD, left column (x 24, 600 wide): Shenzhen summit
lx, lw = 24, 600
pg.kicker(lx, 130, "SUMMIT  -  SHENZHEN, APEC")
y = pg.head(lx, 148, "TRUMP, XI AND PUTIN HOLD FIRST THREE-WAY SUMMIT", lw, 3)
ill_summit(pg, lx, y + 8, lw, 110)
y = y + 8 + 110 + 12
y = pg.para(lx, y,
    "Donald Trump, Xi Jinping and Vladimir Putin met in Shenzhen at the "
    "APEC summit, the first time the three leaders have sat down "
    "together. Ukraine dominated the Trump-Putin talks.",
    lw, 2, INK)
y = pg.para(lx, y + 4,
    "The three were also expected to discuss nuclear arms control after "
    "the expiry of New START, and the future of world trade.",
    lw, 2, GREY)
lead_end = y

# RIGHT column (x 648, 352 wide): ICJ, then Bangladesh
rx, rw = 648, 352
pg.kicker(rx, 130, "THE HAGUE  -  ICJ RULING")
y2 = pg.head(rx, 148, "ICJ RULES ON ROHINGYA GENOCIDE CASE", rw, 2)
ill_scales(pg, rx, y2 + 8, rw, 56)
y2 = y2 + 8 + 56 + 10
y2 = pg.para(rx, y2,
    "The International Court of Justice rules on Gambia's case against "
    "Myanmar over the 2017 crackdown that drove 730,000 Rohingya into "
    "Bangladesh. No state has ever been found guilty of genocide.",
    rw, 2, INK, leading=17)
pg.hline(rx, y2 + 10, rw)
pg.kicker(rx, y2 + 22, "BANGLADESH  -  UNREST SPREADS")
y2 = pg.head(rx, y2 + 40, "YUNUS HOME TORCHED AS UNREST SPREADS", rw, 2)
ill_fire(pg, rx, y2 + 8, rw, 40)
y2 = y2 + 8 + 40 + 8
y2 = pg.para(rx, y2,
    "Muhammad Yunus's ancestral home was set on fire as protests spread "
    "to 28 districts. Paramilitary forces deployed after dozens of bomb "
    "blasts.",
    rw, 2, INK, leading=17)
right_end = y2

# MIDDLE ROW: Crimea bridge (left) and the Gulf (right)
my = max(lead_end, right_end) + 16
pg.hline(24, my, W - 48)
pg.kicker(lx, my + 12, "UKRAINE  -  KERCH BRIDGE")
y3 = pg.head(lx, my + 32, "KERCH BRIDGE HIT FOR THIRD TIME IN A WEEK", 480, 2)
ill_bridge(pg, lx, y3 + 6, 480, 40)
y3 = pg.para(lx, y3 + 6 + 40 + 8,
    "Ukraine struck the Crimean Bridge for the third time in a week. "
    "The head of Crimea said traffic was suspended after the attack on "
    "the strategic link to the annexed peninsula.",
    480, 2, INK, leading=15)
bx, bw = 528, 472
pg.kicker(bx, my + 12, "MIDDLE EAST  -  GULF WIDENS")
y4 = pg.head(bx, my + 32, "KUWAIT REPELS IRANIAN ATTACK", bw, 2)
ill_gulf(pg, bx, y4 + 6, bw, 40)
y4 = pg.para(bx, y4 + 6 + 40 + 8,
    "Kuwait said it repelled an Iranian attack, the first in two months, "
    "and Bahrain said it was targeted too, after US jets struck a "
    "missile site on Iran's Qeshm Island. The IEA called the Hormuz "
    "crisis the greatest threat ever to energy security.",
    bw, 2, INK, leading=15)
mid_end = max(y3, y4)

# BOTTOM STRIP: in brief, two columns
by = mid_end + 14
pg.hline(24, by, W - 48)
pg.kicker(24, by + 10, "IN BRIEF")
_briefs_left = [
    "COP31: Ministers meet in Antalya to unblock the climate talks.",
    "VAN GOGH: 'Chestnut Trees in Flower' sells for USD 190.4M, a record.",
    "EU: Brussels proposes a EUR 45BN loan to fund Ukraine in 2027.",
]
_briefs_right = [
    "NORTH KOREA: IAEA says uranium enrichment at Yongbyon expanded.",
    "ANTHROPIC: IPO priced at USD 83, set to raise USD 81.3BN, a record.",
    "FIJI: State of disaster declared as El Nino drought drains water.",
]
yy = by + 32
for _lb, _rb in zip(_briefs_left, _briefs_right):
    pg.para(24, yy, _lb, 470, 1, INK, leading=15)
    pg.para(528, yy, _rb, 472, 1, INK, leading=15)
    yy += 28
# markets line
pg.hline(24, yy + 6, W - 48, FAINT)
pg.text(24, yy + 18,
    "MARKETS: SP 500 7,323.63 -0.23%  NASDAQ 24,429.88 +0.42%  GOLD USD 3,739.60  "
    "BRENT USD 89.59 -2.57%  VIX 24.56",
    1, GREY)


# --- PNG writer (stdlib zlib) ---
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(page, path):
    raw = b"".join(b"\x00" + bytes(page.pix[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + _chunk(b"IDAT", zlib.compress(raw, 9))
           + _chunk(b"IEND", b""))
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out = "/output/entry.png" if os.path.isdir("/output") else "output/entry.png"
    if "MAKEFUN_OUTPUT_DIR" in os.environ:
        out = os.path.join(os.environ["MAKEFUN_OUTPUT_DIR"], "entry.png")
    if "OUTPUT_PATH" in os.environ:
        out = os.environ["OUTPUT_PATH"]
    n = write_png(pg, out)
    print(f"wrote {out} {W}x{H} {n} bytes")


if __name__ == "__main__":
    main()
