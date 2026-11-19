#!/usr/bin/env python3
"""The World in One Page - Wednesday 18 November 2026.

Draws a one-page newspaper front page summing up the day's world news
as a 1024x1024 PNG. Python standard library only: no network, no clock,
no randomness, no third-party packages. Running it twice produces
byte-identical output.

Layout (top to bottom):
  masthead band, lead story (Shenzhen summit), two rows of two stories
  (Gulf strikes / Kerch bridge; Alaska Senate / Nvidia), a full-width
  health strip (measles), a briefs strip, and a sources footer.

Every letter is drawn from GLYPHS, a hand-made 5x7 bitmap font below.
Every picture is drawn from circles, lines and rectangles.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (27, 42, 74)
RED = (169, 30, 34)
GOLD = (201, 162, 39)
GOLD_DARK = (150, 116, 28)
GREY = (96, 96, 92)
TINT = (233, 227, 211)
BLUE = (38, 84, 124)
GREEN = (46, 125, 87)
TEAL = (24, 110, 110)
WHITE = (255, 255, 255)
NAVY_BG = (24, 36, 64)

# ------------------------------------------------------------------- font
# Each glyph is 7 rows of 5 cells. "#" is ink, "." is empty.
GLYPHS = {
    "A": ("..#..", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", "..#.."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    ";": (".....", "..#..", ".....", ".....", ".....", "..#..", "..#.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
}

BLANK = (".....",) * 7


def text_width(text, scale):
    """Pixel width of text at the given scale (6 units per char)."""
    return len(text) * 6 * scale


def wrap(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.buf = bytearray(colour * (width * height))

    def px(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = colour[0]
            self.buf[i + 1] = colour[1]
            self.buf[i + 2] = colour[2]

    def block(self, x, y, s, colour):
        for dy in range(s):
            for dx in range(s):
                self.px(x + dx, y + dy, colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            base = (yy * self.w + x) * 3
            for xx in range(w):
                i = base + xx * 3
                if 0 <= x + xx < self.w and 0 <= yy < self.h:
                    self.buf[i] = colour[0]
                    self.buf[i + 1] = colour[1]
                    self.buf[i + 2] = colour[2]

    def hline(self, x, y, length, colour, thick=1):
        self.rect(x, y, length, thick, colour)

    def vline(self, x, y, length, colour, thick=1):
        self.rect(x, y, thick, length, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        """Bresenham line, with square brush of side `thick`."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.block(x - thick // 2, y - thick // 2, thick, colour)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - half, cy + dy, 2 * half + 1, 1, colour)

    def ring(self, cx, cy, r, colour, thick=3):
        # Parametric outline: plot points around the circle.
        import math

        steps = max(48, r * 4)
        for k in range(steps):
            a = 2 * math.pi * k / steps
            self.block(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)),
                       thick, colour)

    def arc(self, cx, cy, r, a0, a1, colour, thick=3):
        import math

        steps = max(24, int(r * abs(a1 - a0)))
        for k in range(steps + 1):
            a = a0 + (a1 - a0) * k / steps
            self.block(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)),
                       thick, colour)

    # ------------------------------------------------------------- text
    def glyph(self, x, y, char, scale, colour):
        rows = GLYPHS.get(char.upper(), BLANK)
        for ry, row in enumerate(rows):
            for rx, cell in enumerate(row):
                if cell == "#":
                    self.block(x + rx * scale, y + ry * scale, scale, colour)

    def text(self, x, y, s, scale, colour):
        for ch in s:
            self.glyph(x, y, ch, scale, colour)
            x += 6 * scale
        return x

    def centred(self, y, s, scale, colour, cx=512):
        x = cx - text_width(s, scale) // 2
        self.text(x, y, s, scale, colour)

    def paragraph(self, x, y, s, scale, colour, max_width, leading=None):
        if leading is None:
            leading = 7 * scale + 6
        for line in wrap(s, max_width, scale):
            self.text(x, y, line, scale, colour)
            y += leading
        return y

    # ---------------------------------------------------------- png out
    def to_png(self):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)  # filter: none
            raw += self.buf[y * stride:(y + 1) * stride]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", comp)
                + chunk(b"IEND", b""))

# --------------------------------------------------------------- pictograms
# Small geometric pictures, one per story, drawn with the canvas tools.

def pic_globe(c, cx, cy, r):
    """Three leaders, one table: a globe with meridians."""
    c.ring(cx, cy, r, BLUE, 4)
    c.ring(cx, cy, r - 14, BLUE, 2)
    c.vline(cx, cy - r, 2 * r, BLUE, 2)
    c.hline(cx - r, cy, 2 * r, BLUE, 2)
    c.arc(cx, cy, r - 26, -1.2, 1.2, BLUE, 2)
    c.arc(cx, cy, r - 26, 1.94, 4.34, BLUE, 2)
    c.disc(cx - r // 2, cy - r // 3, 5, RED)
    c.disc(cx + r // 2, cy - r // 4, 5, GOLD_DARK)
    c.disc(cx, cy + r // 2, 5, TEAL)


def pic_burst(c, cx, cy, r):
    """Strikes in the Gulf: a burst over water."""
    for k in range(8):
        import math
        a = math.pi * k / 4
        c.line(cx, cy, int(cx + r * math.cos(a)), int(cy + r * math.sin(a)),
               RED, 3)
    c.disc(cx, cy, r // 3, GOLD)
    c.disc(cx, cy, r // 6, RED)
    c.hline(cx - r, cy + r, 2 * r, BLUE, 3)
    c.hline(cx - r + 8, cy + r + 10, 2 * r - 16, BLUE, 2)


def pic_bridge(c, cx, cy, w):
    """Kerch bridge: deck broken, one span down in the strait."""
    c.hline(cx - w // 2, cy - 10, w // 2 - 14, INK, 5)  # left deck
    c.hline(cx + 14, cy - 10, w // 2 - 14, INK, 5)      # right deck
    c.rect(cx - w // 2 + 8, cy - 5, 8, 40, INK)         # left pier
    c.rect(cx + w // 2 - 16, cy - 5, 8, 40, INK)        # right pier
    c.line(cx - 14, cy - 10, cx + 10, cy + 24, INK, 5)  # fallen span
    c.hline(cx - w // 2, cy + 38, w, BLUE, 3)           # strait
    c.hline(cx - w // 2 + 10, cy + 46, w - 20, BLUE, 2)


def pic_ballot(c, cx, cy, s):
    """Alaska vote: a ballot box with a ticked slip."""
    c.rect(cx - s // 2, cy - 6, s, s - 6, BLUE)
    c.hline(cx - s // 2 + 8, cy - 6, s - 16, PAPER, 4)
    c.rect(cx - 12, cy - 34, 24, 26, WHITE)
    c.rect(cx - 12, cy - 34, 24, 26, INK)
    c.line(cx - 8, cy - 22, cx - 2, cy - 14, RED, 3)
    c.line(cx - 2, cy - 14, cx + 10, cy - 30, RED, 3)


def pic_chip(c, cx, cy, s):
    """Nvidia: a chip with rising bars."""
    c.rect(cx - s // 2, cy - s // 2, s, s, INK)
    c.rect(cx - s // 2 + 8, cy - s // 2 + 8, s - 16, s - 16, PAPER)
    for k in range(3):
        c.rect(cx - s // 2 + 14 + k * 14, cy + s // 2 - 16 - (k + 1) * 9,
               8, (k + 1) * 9, GREEN)
    for k in range(4):
        c.hline(cx - s // 2 + 6 + k * 16, cy - s // 2 - 8, 8, INK, 3)
        c.hline(cx - s // 2 + 6 + k * 16, cy + s // 2 + 5, 8, INK, 3)


def pic_virus(c, cx, cy, r):
    """Measles: a spiked round virus."""
    import math
    for k in range(10):
        a = 2 * math.pi * k / 10
        x2 = int(cx + (r + 8) * math.cos(a))
        y2 = int(cy + (r + 8) * math.sin(a))
        c.line(cx, cy, x2, y2, RED, 3)
        c.disc(x2, y2, 4, RED)
    c.disc(cx, cy, r, TEAL)
    c.disc(cx - r // 3, cy - r // 3, r // 4, WHITE)
    c.disc(cx + r // 3, cy + r // 4, r // 5, WHITE)


def pic_cyclone(c, cx, cy, r):
    """Cyclone Akvan: three tightening arcs."""
    c.arc(cx, cy, r, 0.3, 4.6, BLUE, 3)
    c.arc(cx + 4, cy + 4, r - 10, 1.0, 5.2, BLUE, 3)
    c.arc(cx + 8, cy + 8, r - 20, 1.8, 5.9, BLUE, 3)
    c.disc(cx + 8, cy + 8, 4, RED)


# ------------------------------------------------------------------ stories
# Headlines spot-checked 2026-11-19 against Reuters (1, 2, 3), AP (4),
# multiple outlets (5), PAHO/CDC (6). GPT-6.2 claim left out: uncorroborated.
LEAD = {
    "kicker": "THE LEAD  -  SHENZHEN",
    "headline": ["XI, PUTIN AND TRUMP", "MEET IN SHENZHEN"],
    "body": ("Xi and Putin hold talks in Shenzhen on Wednesday, a day "
             "before the first trilateral summit with Trump at APEC. "
             "Xi greets Trump on the tarmac."),
    "pic": pic_globe,
}

GRID = [
    {
        "kicker": "THE GULF",
        "headline": "GULF STRIKES WIDEN",
        "body": ("US jets hit a Revolutionary Guard missile site on "
                 "Qeshm Island. Iran fires at US bases in Kuwait and "
                 "Bahrain. No casualties reported."),
        "pic": pic_burst,
    },
    {
        "kicker": "UKRAINE",
        "headline": "KERCH BRIDGE HIT AGAIN",
        "body": ("Ukraine strikes the bridge to Crimea a second day "
                 "running. A road span falls into the strait; traffic "
                 "halts. Rail traffic partly resumes."),
        "pic": pic_bridge,
    },
    {
        "kicker": "WASHINGTON",
        "headline": "PELTOLA WINS ALASKA",
        "body": ("Democrat Mary Peltola beats Republican Dan Sullivan "
                 "in the last Senate race to be called. Democrats take "
                 "a 56-44 majority, their ninth flip."),
        "pic": pic_ballot,
    },
    {
        "kicker": "TECH",
        "headline": "NVIDIA'S RECORD QUARTER",
        "body": ("Revenue $115.8B, up 103% on the year. The board "
                 "rejects former CEO Jensen Huang's offer to return. "
                 "He testifies to Congress in December."),
        "pic": pic_chip,
    },
]

STRIP = {
    "kicker": "HEALTH",
    "headline": "US LOSES MEASLES-ELIMINATION STATUS",
    "body": ("PAHO says one measles transmission chain ran for more "
             "than 12 months, ending a status held since 2000. "
             "Mexico and Bolivia lose it too."),
    "pic": pic_virus,
}

BRIEFS = [
    ("CYCLONE AKVAN", "strengthens in the Bay of Bengal; landfall in "
     "India on Friday."),
    ("EBOLA", "in DR Congo passes 11,000 cases and 5,400 deaths, "
     "the UN says."),
    ("ANTHROPIC", "prices its IPO at $83 a share, above the expected "
     "range."),
]

MARGIN = 24
CONTENT_W = W - 2 * MARGIN


# ------------------------------------------------------------------ layout
def draw_masthead(c):
    c.rect(0, 0, W, 120, NAVY_BG)
    c.centred(26, "THE WORLD IN ONE PAGE", 5, WHITE)
    c.centred(76, "WEDNESDAY - 18 NOVEMBER 2026", 2, GOLD)
    c.hline(0, 120, W, RED, 5)


def draw_lead(c, y):
    # Lead story: kicker + two-line headline left, globe right, body below.
    c.text(MARGIN, y, LEAD["kicker"], 2, RED)
    hy = y + 26
    for line in LEAD["headline"]:
        c.text(MARGIN, hy, line, 4, INK)
        hy += 7 * 4 + 8
    LEAD["pic"](c, 884, y + 88, 74)
    c.paragraph(MARGIN, hy + 6, LEAD["body"], 2, INK, 620)
    return y + 180


def draw_cell(c, story, x, y, w, h):
    # Text lives in a left column; the pictogram owns a 116px column
    # on the right, so pictures can never cover words.
    c.rect(x, y, w, 2, INK)
    text_w = w - 120
    c.text(x, y + 12, story["kicker"], 2, RED)
    hy = y + 38
    for line in wrap(story["headline"], text_w, 3):
        c.text(x, hy, line, 3, INK)
        hy += 7 * 3 + 6
    px = x + w - 58
    py = y + 100
    if story["pic"] is pic_bridge:
        story["pic"](c, px, py, 92)
    elif story["pic"] is pic_burst:
        story["pic"](c, px, py, 32)
    elif story["pic"] is pic_ballot:
        story["pic"](c, px, py, 56)
    else:
        story["pic"](c, px, py, 56)
    c.paragraph(x, hy + 12, story["body"], 2, INK, text_w)
    return y + h


def draw_strip(c, y):
    c.rect(MARGIN, y, CONTENT_W, 116, TINT)
    c.rect(MARGIN, y, 6, 116, RED)
    STRIP["pic"](c, MARGIN + 56, y + 58, 30)
    c.text(MARGIN + 108, y + 14, STRIP["kicker"], 2, RED)
    c.text(MARGIN + 108, y + 40, STRIP["headline"], 3, INK)
    c.paragraph(MARGIN + 108, y + 72, STRIP["body"], 2, INK,
                CONTENT_W - 132)
    return y + 116


def draw_briefs(c, y):
    c.text(MARGIN, y, "IN BRIEF", 2, RED)
    y += 26
    for tag, rest in BRIEFS:
        c.disc(MARGIN + 5, y + 6, 4, RED)
        c.text(MARGIN + 18, y, tag, 2, INK)
        tx = MARGIN + 18 + text_width(tag + " ", 2)
        y = c.paragraph(tx, y, rest, 2, GREY, CONTENT_W - (tx - MARGIN) - 8,
                        leading=20)
        y += 4
    return y


def draw_page():
    c = Canvas(W, H, PAPER)
    draw_masthead(c)
    y = draw_lead(c, 138)
    c.hline(MARGIN, y + 8, CONTENT_W, INK, 2)
    y += 20
    # Two rows of two stories.
    cell_w = (CONTENT_W - 24) // 2
    row_h = 200
    draw_cell(c, GRID[0], MARGIN, y, cell_w, row_h)
    draw_cell(c, GRID[1], MARGIN + cell_w + 24, y, cell_w, row_h)
    y += row_h + 12
    draw_cell(c, GRID[2], MARGIN, y, cell_w, row_h)
    draw_cell(c, GRID[3], MARGIN + cell_w + 24, y, cell_w, row_h)
    y += row_h + 12
    y = draw_strip(c, y)
    y += 12
    y = draw_briefs(c, y)
    c.centred(1002, "DRAWN IN CODE - SOURCES: REUTERS, AP, BBC, PAHO",
              1, GREY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    png = draw_page().to_png()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
