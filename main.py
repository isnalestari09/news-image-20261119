#!/usr/bin/env python3
"""Sum up 19 November 2026 world news in one image.

make.fun bounty news-image-20261119.
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

Rendering is a small rasteriser written for this program, with a
5x7 bitmap font stored as 5-bit row masks, so it needs no
external files, fonts or packages.
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

# --- 5x7 bitmap font: each glyph is 7 row masks, bit 4 = leftmost dot ---
def _rows(*rs):
    return rs

GLYPHS = {}
_caps = {
    "A": _rows(0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": _rows(0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": _rows(0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": _rows(0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": _rows(0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": _rows(0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": _rows(0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": _rows(0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": _rows(0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": _rows(0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": _rows(0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": _rows(0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": _rows(0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": _rows(0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": _rows(0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": _rows(0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": _rows(0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": _rows(0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": _rows(0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": _rows(0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": _rows(0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": _rows(0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": _rows(0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": _rows(0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": _rows(0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": _rows(0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
}
_small = {
    "a": _rows(0b00000, 0b00000, 0b01110, 0b00001, 0b01111, 0b10001, 0b01111),
    "b": _rows(0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b11110),
    "c": _rows(0b00000, 0b00000, 0b01110, 0b10000, 0b10000, 0b10001, 0b01110),
    "d": _rows(0b00001, 0b00001, 0b01111, 0b10001, 0b10001, 0b10001, 0b01111),
    "e": _rows(0b00000, 0b00000, 0b01110, 0b10001, 0b11111, 0b10000, 0b01110),
    "f": _rows(0b00110, 0b01001, 0b01000, 0b11110, 0b01000, 0b01000, 0b01000),
    "g": _rows(0b00000, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "h": _rows(0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001),
    "i": _rows(0b00100, 0b00000, 0b01100, 0b00100, 0b00100, 0b00100, 0b01110),
    "j": _rows(0b00010, 0b00000, 0b00110, 0b00010, 0b00010, 0b10010, 0b01100),
    "k": _rows(0b10000, 0b10000, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010),
    "l": _rows(0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "m": _rows(0b00000, 0b00000, 0b11010, 0b10101, 0b10101, 0b10101, 0b10101),
    "n": _rows(0b00000, 0b00000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001),
    "o": _rows(0b00000, 0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110),
    "p": _rows(0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000),
    "q": _rows(0b00000, 0b00000, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001),
    "r": _rows(0b00000, 0b00000, 0b10110, 0b11001, 0b10000, 0b10000, 0b10000),
    "s": _rows(0b00000, 0b00000, 0b01111, 0b10000, 0b01110, 0b00001, 0b11110),
    "t": _rows(0b01000, 0b01000, 0b11100, 0b01000, 0b01000, 0b01001, 0b00110),
    "u": _rows(0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b10011, 0b01101),
    "v": _rows(0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "w": _rows(0b00000, 0b00000, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "x": _rows(0b00000, 0b00000, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001),
    "y": _rows(0b00000, 0b00000, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "z": _rows(0b00000, 0b00000, 0b11111, 0b00010, 0b00100, 0b01000, 0b11111),
}
for _table in (_caps, _small):
    GLYPHS.update(_table)

_digits = {
    "0": _rows(0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": _rows(0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": _rows(0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": _rows(0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": _rows(0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": _rows(0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": _rows(0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": _rows(0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": _rows(0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": _rows(0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
}
_marks = {
    " ": _rows(0, 0, 0, 0, 0, 0, 0),
    ".": _rows(0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": _rows(0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    ":": _rows(0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": _rows(0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "'": _rows(0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    '"': _rows(0b01010, 0b01010, 0, 0, 0, 0, 0),
    "-": _rows(0, 0, 0, 0b01110, 0, 0, 0),
    "(": _rows(0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": _rows(0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "?": _rows(0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    "!": _rows(0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "/": _rows(0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "+": _rows(0, 0b00100, 0b00100, 0b01110, 0b00100, 0b00100, 0),
    "=": _rows(0, 0, 0b11111, 0, 0b11111, 0, 0),
    "$": _rows(0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "%": _rows(0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
}
GLYPHS.update(_digits)
GLYPHS.update(_marks)
BLANK = (0, 0, 0, 0, 0, 0, 0)

# --- canvas: flat RGB buffer ---
buf = bytearray(PAPER * W * H)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        buf[o], buf[o + 1], buf[o + 2] = c


def fill(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(xx, yy, c)


def rule_h(x, y, w, c=INK):
    fill(x, y, w, 1, c)


def rule_v(x, y, h, c=INK):
    fill(x, y, 1, h, c)


def disc(cx, cy, r, c, solid=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if solid and d <= r * r:
                set_px(xx, yy, c)
            elif not solid and abs(d - r * r) <= r:
                set_px(xx, yy, c)


def seg(x0, y0, x1, y1, c):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        set_px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)


def draw_text(x, y, s, size, c):
    """Draw text left-aligned; return pixel width used."""
    cx = x
    for ch in s:
        glyph = GLYPHS.get(ch, BLANK)
        for r, mask in enumerate(glyph):
            for col in range(5):
                if mask >> (4 - col) & 1:
                    fill(cx + col * size, y + r * size, size, size, c)
        cx += 6 * size
    return cx - x


def text_width(s, size):
    return len(s) * 6 * size


def split_lines(s, max_w, size):
    out, cur = [], ""
    for word in s.split(" "):
        trial = (cur + " " + word).strip()
        if text_width(trial, size) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def draw_para(x, y, s, max_w, size, c, leading=None):
    leading = leading if leading is not None else 9 * size
    for ln in split_lines(s, max_w, size):
        draw_text(x, y, ln, size, c)
        y += leading
    return y


def draw_head(x, y, s, max_w, size=3):
    yy = y
    for ln in split_lines(s, max_w, size):
        draw_text(x, yy, ln, size, INK)
        yy += 10 * size
    return yy


def draw_kicker(x, y, s, c=RED):
    return draw_text(x, y, s, 2, c)


# --- illustrations, all drawn, no photos ---
def ill_summit(x, y, w, h):
    fill(x, y, w, h, SKY)
    disc(x + w - 64, y + 32, 20, GOLD)
    # skyline towers with lit windows
    for i, bh in enumerate((46, 78, 60, 92, 66, 82, 52)):
        bx = x + 12 + i * 52
        fill(bx, y + h - 36 - bh, 38, bh + 36, NAVY)
        for wy in range(y + h - 30 - bh, y + h - 40, 13):
            for wx in range(bx + 6, bx + 32, 11):
                fill(wx, wy, 5, 6, GOLD)
    fill(x, y + h - 36, w, 36, (58, 58, 58))
    # three flag poles in front
    for i, fc in enumerate((RED, (255, 255, 255), NAVY)):
        fx = x + 26 + i * 64
        rule_v(fx, y + 6, h - 42, INK)
        fill(fx, y + 6, 42, 24, fc)
        if fc == (255, 255, 255):
            fill(fx, y + 6, 42, 8, RED)
            fill(fx, y + 22, 42, 8, NAVY)


def ill_gavel(x, y, w, h):
    fill(x, y, w, h, NAVY)
    # court columns
    for cx in (x + 26, x + w - 34):
        fill(cx, y + 18, 8, h - 36, (210, 205, 190))
        fill(cx - 4, y + 14, 16, 6, (210, 205, 190))
        fill(cx - 4, y + h - 24, 16, 6, (210, 205, 190))
    # gavel: head and handle, diagonal
    fill(x + w // 2 - 46, y + 30, 92, 22, (139, 90, 43))
    fill(x + w // 2 - 52, y + 26, 10, 30, (120, 76, 34))
    fill(x + w // 2 + 42, y + 26, 10, 30, (120, 76, 34))
    seg(x + w // 2 + 8, y + 52, x + w // 2 + 26, y + h - 26, (160, 110, 60))
    seg(x + w // 2 + 2, y + 52, x + w // 2 + 20, y + h - 26, (160, 110, 60))
    # sound block
    fill(x + w // 2 - 34, y + h - 24, 68, 12, (120, 76, 34))
    disc(x + w // 2 - 40, y + 20, 5, GOLD)
    disc(x + w // 2 + 40, y + 20, 5, GOLD)


def ill_bridge(x, y, w, h):
    fill(x, y, w, h, SKY)
    disc(x + 36, y + 12, 12, GOLD)
    sea_y = y + h - 18
    fill(x, sea_y, w, 18, SEA)
    for wx in range(x + 8, x + w - 8, 30):
        rule_h(wx, sea_y + 6 + (wx % 3) * 3, 18, (130, 175, 215))
    # deck, left and right spans; middle span gone
    deck_y = y + h - 30
    fill(x, deck_y, w // 2 - 26, 7, (88, 88, 88))
    fill(x + w // 2 + 26, deck_y, w // 2 - 26, 7, (88, 88, 88))
    # fallen span tilted into the water
    seg(x + w // 2 - 24, deck_y + 4, x + w // 2 + 12, y + h - 6, (66, 66, 66))
    seg(x + w // 2 + 24, deck_y + 4, x + w // 2 - 8, y + h - 4, (66, 66, 66))
    # suspension cables
    for px_ in range(x + 10, x + w - 10, 24):
        rule_v(px_, y + 6, deck_y - y - 6, (110, 110, 110))


def ill_gulf(x, y, w, h):
    fill(x, y, w, h, DUSK)
    disc(x + w - 52, y + 14, 14, (228, 228, 216))
    sea_y = y + h // 2
    fill(x, sea_y, w, h - h // 2, SEA)
    for wx in range(x + 8, x + w - 8, 34):
        rule_h(wx, sea_y + 8 + (wx % 3) * 4, 18, (120, 170, 210))
    # drone silhouette
    cx, cy = x + w // 3, y + 22
    fill(cx - 24, cy - 4, 48, 7, INK)
    fill(cx - 7, cy - 13, 14, 9, INK)
    disc(cx - 26, cy, 6, INK)
    disc(cx + 26, cy, 6, INK)
    # explosion flare over the water
    disc(x + 2 * w // 3, y + h - 16, 16, (220, 120, 40))
    disc(x + 2 * w // 3, y + h - 24, 10, (240, 180, 60))
    # patrol ship silhouette
    sx = x + 24
    fill(sx, y + h - 14, 90, 8, INK)
    fill(sx + 30, y + h - 24, 22, 10, INK)


def ill_fire(x, y, w, h):
    fill(x, y, w, h, (240, 224, 200))
    # house outline with flame
    fill(x + 22, y + h - 40, w - 44, 40, (120, 90, 70))
    seg(x + 22, y + h - 40, x + w // 2, y + 12, (90, 60, 44))
    seg(x + w // 2, y + 12, x + w - 22, y + h - 40, (90, 60, 44))
    disc(x + w // 2, y + h - 58, 22, (230, 120, 30))
    disc(x + w // 2, y + h - 46, 13, (245, 190, 60))
    disc(x + w // 2, y + h - 38, 6, (250, 230, 120))


# --- page layout ---
fill(0, 0, W, H, PAPER)
rule_h(24, 16, W - 48)
rule_h(24, 20, W - 48)

# masthead
_title = "THE WORLD TODAY"
draw_text((W - text_width(_title, 5)) // 2, 34, _title, 5, INK)
rule_h(24, 88, W - 48, RED)
rule_h(24, 92, W - 48, RED)
_dateline = "THURSDAY, 19 NOVEMBER 2026  |  NO. 19  |  PAGE 1"
draw_text((W - text_width(_dateline, 2)) // 2, 104, _dateline, 2, INK)
rule_h(24, 126, W - 48)

# LEAD, left column (x 24, 600 wide): Shenzhen summit
lx, lw = 24, 600
draw_kicker(lx, 140, "SUMMIT  -  SHENZHEN, APEC")
y = draw_head(lx, 160, "TRUMP, XI AND PUTIN MEET IN SHENZHEN", lw, 3)
ill_summit(lx, y + 8, lw, 110)
y = y + 8 + 110 + 12
y = draw_para(lx, y,
    "Donald Trump, Xi Jinping and Vladimir Putin met in Shenzhen on the "
    "sidelines of the APEC summit, the first time the leaders of the three "
    "largest powers have sat down together. Ukraine dominated the talks "
    "with Putin.",
    lw, 2, INK)
y = draw_para(lx, y + 4,
    "The trilateral meeting was also expected to take up nuclear arms "
    "control after the expiry of the New START treaty, and the future "
    "of world trade.",
    lw, 2, GREY)
lead_end = y

# RIGHT column (x 648, 352 wide): ICJ, then Bangladesh
rx, rw = 648, 352
draw_kicker(rx, 140, "THE HAGUE  -  ICJ RULING")
y2 = draw_head(rx, 160, "COURT RULES ON ROHINGYA GENOCIDE", rw, 2)
ill_gavel(rx, y2 + 8, rw, 72)
y2 = y2 + 8 + 72 + 10
y2 = draw_para(rx, y2,
    "The International Court of Justice rules on Gambia's genocide case "
    "against Myanmar over the 2017 crackdown that drove 730,000 Rohingya "
    "into Bangladesh. No state has ever been found guilty of genocide.",
    rw, 2, INK, leading=17)
rule_h(rx, y2 + 10, rw)
draw_kicker(rx, y2 + 22, "BANGLADESH  -  UNREST SPREADS")
y2 = draw_head(rx, y2 + 40, "YUNUS HOME TORCHED IN 28-DISTRICT UNREST", rw, 2)
y2 = draw_para(rx, y2 + 2,
    "Muhammad Yunus's ancestral home was set on fire as protests by "
    "Sheikh Hasina's party spread to 28 districts. Paramilitary forces "
    "deployed after dozens of bomb blasts.",
    rw, 2, INK, leading=17)
right_end = y2

# MIDDLE ROW: Crimea bridge (left) and the Gulf (right)
my = max(lead_end, right_end) + 16
rule_h(24, my, W - 48)
draw_kicker(lx, my + 12, "UKRAINE  -  KERCH BRIDGE")
y3 = draw_head(lx, my + 32, "BRIDGE HIT AGAIN AS TRAFFIC IS SUSPENDED", 480, 2)
ill_bridge(lx, y3 + 6, 480, 44)
y3 = draw_para(lx, y3 + 6 + 44 + 8,
    "Ukraine struck the Crimean Bridge for the third time in a week. "
    "The head of Crimea said traffic was suspended after the attack on "
    "the strategic link to the annexed peninsula.",
    480, 2, INK, leading=16)
bx, bw = 528, 472
draw_kicker(bx, my + 12, "MIDDLE EAST  -  GULF WIDENS")
y4 = draw_head(bx, my + 32, "KUWAIT REPELS IRANIAN ATTACK", bw, 2)
ill_gulf(bx, y4 + 6, bw, 44)
y4 = draw_para(bx, y4 + 6 + 44 + 8,
    "Kuwait said it repelled an Iranian attack, the first in two months, "
    "and Bahrain said it was targeted too, after US jets struck a "
    "missile site on Iran's Qeshm Island. The IEA called the Hormuz "
    "crisis the greatest threat ever to energy security.",
    bw, 2, INK, leading=16)
mid_end = max(y3, y4)

# BOTTOM STRIP: in brief, two columns
by = mid_end + 14
rule_h(24, by, W - 48)
draw_kicker(24, by + 10, "IN BRIEF")
_briefs_left = [
    "COP31: Ministers meet in Antalya to unblock climate talks and agree a final text.",
    "VAN GOGH: 'Chestnut Trees in Flower' sells at Sotheby's for USD 190.4M, a record.",
    "EU: Brussels proposes a EUR 45BN loan to fund Ukraine in 2027.",
]
_briefs_right = [
    "NORTH KOREA: IAEA says uranium enrichment at Yongbyon has expanded.",
    "ANTHROPIC: IPO priced at USD 83 a share, set to raise USD 81.3BN, a record.",
    "FIJI: National state of disaster declared as El Nino drought drains water.",
]
yy = by + 32
for _lb, _rb in zip(_briefs_left, _briefs_right):
    draw_para(24, yy, _lb, 470, 1, INK, leading=15)
    draw_para(528, yy, _rb, 472, 1, INK, leading=15)
    yy += 30
# markets line
rule_h(24, yy + 6, W - 48, FAINT)
draw_text(24, yy + 18,
    "MARKETS: SP 500 7,323.63 -0.23%  NASDAQ 24,429.88 +0.42%  GOLD USD 3,739.60  "
    "BRENT USD 89.59 -2.57%  VIX 24.56",
    1, GREY)


# --- PNG writer (stdlib zlib) ---
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path):
    raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3])
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
    n = write_png(out)
    print(f"wrote {out} {W}x{H} {n} bytes")


if __name__ == "__main__":
    main()
