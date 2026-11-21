#!/usr/bin/env python3
"""Render THE WORLD TODAY — Saturday 21 November 2026.

A one-page digital front page summing up the day's world news:
36 stories across 7 regions, drawn with Pillow only. Deterministic:
same input bytes in, same PNG bytes out (no timestamps, no randomness).
Run:  python3 compose.py   -> writes entry.png beside this file.
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (250, 247, 240)
INK = (17, 17, 17)
NAVY = (24, 38, 66)
NAVY_LT = (38, 58, 96)
RED = (178, 34, 34)
RED_LT = (198, 52, 40)
GOLD = (201, 162, 39)
GREY = (110, 110, 108)
LINE = (200, 196, 188)
WHITE = (255, 255, 255)
GREEN = (27, 120, 70)

F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, f, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def centre(draw, s, cx, y, f, fill):
    draw.text((cx - text_w(draw, s, f) / 2, y), s, font=f, fill=fill)


# ---------------------------------------------------------------- stories
# (head, detail) pairs, grouped by region. All facts as reported 21 Nov 2026.
STORIES = [
    ("EUROPE", [
        ("Kyiv hit overnight: 3 killed", "9 injured; bridges damaged, power cut — AP"),
        ("Kyiv bridges hit, power cut", "Strikes damage crossings; outages across city"),
        ("Kryvyi Rih missile strike", "2 killed, 60 wounded in Zelenskyy's hometown"),
        ("Trump: Europe must defund Kyiv", "US president's message to allies — Telegraph"),
        ("Russia rules out energy truce", "No ceasefire on energy, Moscow says"),
        ("No Black Sea truce either", "Moscow rejects a sea ceasefire too"),
        ("Kerch Bridge: revenge vowed", "Russia promises retaliation after bridge damage"),
        ("UK–EU landmark deal", "London and Brussels rebuild ties post-Brexit"),
        ("Rutte flies to Warsaw", "NATO chief visits Poland as Ukraine talks continue"),
        ("Zelenskyy rejects land swap", "Kyiv rules out ceding land in US peace plan"),
    ]),
    ("MARKETS", [
        ("S&P 500 falls 3.7% on Friday", "Wall Street's worst day in the AI sell-off"),
        ("Nikkei plunges 5.06%", "Tokyo follows US markets sharply lower"),
        ("AI stocks lead the rout", "Chip and software shares drag indexes down"),
        ("Anthropic debuts near $2T", "AI lab lists on Wall Street on Thursday"),
        ("Bitcoin slides with stocks", "Crypto joins the AI sell-off, down sharply"),
    ]),
    ("NORTH AMERICA", [
        ("'El Chapo Isidro' captured", "FBI most-wanted kingpin seized in Sinaloa"),
        ("Violence follows the arrest", "Gunmen hit back after forces move in"),
        ("US envoy meets Putin", "Witkoff in Moscow to discuss the peace plan"),
    ]),
    ("SOUTH AMERICA", [
        ("Peru quake: magnitude 6.7", "Andes tremor; no casualties reported yet"),
        ("Brazil dengue cases down 69%", "Wolbachia mosquitoes cut infections sharply"),
    ]),
    ("MIDDLE EAST", [
        ("Gaza: 7 killed in strikes", "Palestinians killed despite the ceasefire"),
        ("Houthis hit Saudi power plant", "Al-Shuqaiq station attacked in Jazan region"),
        ("Houthis hit Jazan port", "Second strike on Saudi Red Sea coast"),
        ("US weighs new Iran strikes", "Trump considers action as Israel presses"),
        ("Iran claims drone downed", "Tehran says it shot down a drone near its border"),
        ("Riyadh: oil output steady", "Saudi says output unaffected by Houthi strikes"),
    ]),
    ("AFRICA & ASIA", [
        ("ICJ: Myanmar guilty of genocide", "Court rules on Rohingya case at The Hague"),
        ("Ebola vaccine trials begin", "Trials launch in DR Congo"),
        ("S. Korea tops e-government", "No. 1 in the UN digital government index"),
    ]),
    ("GLOBAL", [
        ("COP31 talks run past deadline", "Antalya summit overruns Friday in stalemate"),
        ("Fossil fuels block a deal", "Nations split over phase-out language"),
        ("UN food agency seeks $12bn", "Aid for 91 million people in 2027"),
    ]),
]

STATS = [
    ("S&P 500", "-3.7%", RED),
    ("NIKKEI", "-5.06%", RED),
    ("PERU QUAKE", "M6.7", NAVY),
    ("KRYVYI RIH", "60 hurt", RED),
    ("ANTHROPIC", "≈$2T", GREEN),
    ("DENGUE", "-69%", GREEN),
]

LEADERS = [
    # (name, role, skin, hair, hair_style, suit, tie)
    ("TRUMP", "US President", (242, 200, 155), (245, 215, 110), "swept", (30, 32, 40), (178, 34, 34)),
    ("XI", "China's leader", (239, 195, 154), (25, 25, 25), "flat", (30, 32, 40), (178, 34, 34)),
    ("PUTIN", "Russia's leader", (239, 201, 160), (201, 194, 180), "short", (30, 32, 40), (38, 68, 140)),
]


def draw_portrait(draw, cx, top, w, h, person):
    """Stylised bust: suit, shirt, tie, head, hair, simple face."""
    name, role, skin, hair, style, suit, tie = person
    # shoulders / suit
    draw.rounded_rectangle([cx - w // 2, top + h - 46, cx + w // 2, top + h], radius=10, fill=suit)
    # shirt V + tie
    draw.polygon([(cx - 16, top + h - 46), (cx + 16, top + h - 46), (cx, top + h - 18)], fill=WHITE)
    draw.polygon([(cx - 6, top + h - 44), (cx + 6, top + h - 44), (cx + 9, top + h - 16),
                  (cx, top + h - 8), (cx - 9, top + h - 16)], fill=tie)
    # lapels
    draw.polygon([(cx - 16, top + h - 46), (cx, top + h - 18), (cx - 24, top + h - 46)], fill=(48, 50, 62))
    draw.polygon([(cx + 16, top + h - 46), (cx, top + h - 18), (cx + 24, top + h - 46)], fill=(48, 50, 62))
    # neck + head
    draw.rectangle([cx - 11, top + 34, cx + 11, top + 52], fill=(224, 178, 138))
    draw.ellipse([cx - 24, top, cx + 24, top + 52], fill=skin)
    # ears
    draw.ellipse([cx - 28, top + 20, cx - 21, top + 34], fill=skin)
    draw.ellipse([cx + 21, top + 20, cx + 28, top + 34], fill=skin)
    # hair
    if style == "swept":  # blond, swept to the side
        draw.pieslice([cx - 25, top - 6, cx + 25, top + 24], 180, 360, fill=hair)
        draw.polygon([(cx - 25, top + 8), (cx + 8, top - 6), (cx + 25, top + 10),
                      (cx + 18, top + 4), (cx - 8, top + 2)], fill=hair)
    elif style == "flat":  # neat black side part
        draw.pieslice([cx - 25, top - 4, cx + 25, top + 20], 180, 360, fill=hair)
        draw.rectangle([cx - 25, top + 6, cx + 25, top + 12], fill=hair)
    else:  # short grey-blond
        draw.pieslice([cx - 25, top - 2, cx + 25, top + 16], 180, 360, fill=hair)
    # brows, eyes, nose, mouth
    draw.line([cx - 15, top + 24, cx - 5, top + 23], fill=(60, 45, 30), width=2)
    draw.line([cx + 5, top + 23, cx + 15, top + 24], fill=(60, 45, 30), width=2)
    draw.ellipse([cx - 13, top + 27, cx - 8, top + 31], fill=INK)
    draw.ellipse([cx + 8, top + 27, cx + 13, top + 31], fill=INK)
    draw.line([cx, top + 31, cx - 2, top + 39], fill=(190, 140, 100), width=2)
    draw.arc([cx - 8, top + 40, cx + 8, top + 48], 20, 160, fill=(140, 70, 60), width=2)
    # name + role
    centre(draw, name, cx, top + h + 4, font(F_SANS_B, 13), WHITE)
    centre(draw, role, cx, top + h + 21, font(F_SANS, 10), (190, 200, 220))


def draw_chart(draw, x, y, w, h):
    """Friday's market moves: zero line in the middle, red falls hang
    below it, the green debut rises above it; values inside the bars."""
    draw.rectangle([x, y, x + w, y + h], outline=LINE, width=1)
    zero = y + 36
    draw.line([x + 8, zero, x + w - 8, zero], fill=GREY, width=1)
    bars = [("S&P", "-3.7%", 22, RED, 1), ("NIKKEI", "-5.06%", 30, RED, 1),
            ("ANTHROPIC", "≈$2T", 28, GREEN, -1)]
    bw, gap = 56, 24
    bx = x + 20
    for label, val, bh, col, direction in bars:
        if direction > 0:  # fall: bar hangs below the zero line
            draw.rectangle([bx, zero, bx + bw, zero + bh], fill=col)
            draw.text((bx + bw // 2 - text_w(draw, val, font(F_SANS_B, 11)) / 2, zero + bh - 16),
                      val, font=font(F_SANS_B, 11), fill=WHITE)
        else:  # debut: bar rises above the zero line
            draw.rectangle([bx, zero - bh, bx + bw, zero], fill=col)
            draw.text((bx + bw // 2 - text_w(draw, val, font(F_SANS_B, 11)) / 2, zero - bh + 4),
                      val, font=font(F_SANS_B, 11), fill=WHITE)
        centre(draw, label, bx + bw // 2, y + h - 14, font(F_SANS_B, 10), INK)
        bx += bw + gap


def draw_scales(draw, cx, y, s):
    """Simple scales of justice for the ICJ feature (48 px tall)."""
    draw.line([cx, y, cx, y + 48], fill=NAVY, width=3)
    draw.line([cx - 34, y + 6, cx + 34, y + 6], fill=NAVY, width=3)
    draw.ellipse([cx - 5, y - 6, cx + 5, y + 4], fill=GOLD)
    for sx in (cx - 34, cx + 34):
        draw.line([sx, y + 6, sx - 13, y + 24], fill=NAVY, width=2)
        draw.line([sx, y + 6, sx + 13, y + 24], fill=NAVY, width=2)
        draw.arc([sx - 14, y + 20, sx + 14, y + 36], 0, 180, fill=NAVY, width=2)
    draw.line([cx - 22, y + 48, cx + 22, y + 48], fill=NAVY, width=3)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 28  # side margin

    # ---- top folio line
    d.text((MX, 12), "VOL. 2026 — No. 325", font=font(F_SANS, 11), fill=GREY)
    right = "PRICE: ONE DAY'S NEWS"
    d.text((W - MX - text_w(d, right, font(F_SANS, 11)), 12), right, font=font(F_SANS, 11), fill=GREY)
    d.line([MX, 32, W - MX, 32], fill=INK, width=2)

    # ---- masthead
    centre(d, "THE WORLD TODAY", W // 2, 40, font(F_SERIF_B, 64), INK)
    d.line([MX, 116, W - MX, 116], fill=INK, width=1)

    # ---- date band
    d.rectangle([MX, 124, W - MX, 158], fill=NAVY)
    centre(d, "SATURDAY  •  21 NOVEMBER 2026", W // 2 - 120, 133, font(F_SERIF_B, 22), WHITE)
    d.text((W - MX - 190, 136), "36 STORIES • 7 REGIONS", font=font(F_SANS_B, 13), fill=GOLD)

    # ---- stats strip
    y0, y1 = 166, 208
    bw = (W - 2 * MX - 5 * 8) / 6
    for i, (label, val, col) in enumerate(STATS):
        x0 = MX + i * (bw + 8)
        d.rectangle([x0, y0, x0 + bw, y1], outline=LINE, width=1, fill=WHITE)
        centre(d, label, x0 + bw / 2, y0 + 6, font(F_SANS_B, 10), GREY)
        centre(d, val, x0 + bw / 2, y0 + 21, font(F_SANS_B, 19), col)

    # ---- hero panel: summit aftermath
    hy0, hy1 = 216, 428
    d.rectangle([MX, hy0, W - MX, hy1], fill=NAVY)
    d.rectangle([MX, hy0, W - MX, hy0 + 4], fill=RED)
    tx = MX + 22
    d.text((tx, hy0 + 16), "SUMMIT AFTERMATH  —  THE LEAD STORY", font=font(F_SANS_B, 12), fill=GOLD)
    head = ["PEACE PLAN PUBLISHED —", "THEN THE BOMBS FELL"]
    yy = draw_lines(d, head, tx, hy0 + 38, font(F_SERIF_B, 34), WHITE, 40)
    deck = ("Trump, Putin and Xi closed their summit with a peace "
            "declaration — then Russia launched its heaviest strikes "
            "on Kyiv and Kryvyi Rih in weeks.")
    draw_lines(d, wrap(d, deck, font(F_SANS, 15), 560), tx, yy + 10, font(F_SANS, 15), (215, 222, 235), 20)
    sub = "KYIV: 3 KILLED, 9 INJURED  •  KRYVYI RIH: 2 KILLED, 60 WOUNDED"
    d.text((tx, hy1 - 30), sub, font=font(F_SANS_B, 12), fill=(255, 200, 190))
    # portraits, right side
    px = W - MX - 300
    for i, person in enumerate(LEADERS):
        draw_portrait(d, px + 50 + i * 100, hy0 + 44, 92, 118, person)

    # ---- three features
    fy0, fy1 = 438, 612
    cw = (W - 2 * MX - 2 * 12) / 3
    cols = []
    for i in range(3):
        x0 = MX + i * (cw + 12)
        cols.append(x0)
        d.rectangle([x0, fy0, x0 + cw, fy1], outline=LINE, width=1, fill=WHITE)
    # 1: markets
    x0 = cols[0]
    d.text((x0 + 12, fy0 + 10), "MARKETS IN TURMOIL", font=font(F_SANS_B, 12), fill=RED)
    draw_lines(d, wrap(d, "Wall Street's AI sell-off goes global", font(F_SERIF_B, 19), cw - 24),
               x0 + 12, fy0 + 30, font(F_SERIF_B, 19), INK, 22)
    draw_chart(d, x0 + 12, fy0 + 80, cw - 24, 84)
    # 2: ICJ
    x0 = cols[1]
    d.text((x0 + 12, fy0 + 10), "THE HAGUE  •  JUSTICE", font=font(F_SANS_B, 12), fill=RED)
    draw_lines(d, wrap(d, "Myanmar guilty of genocide", font(F_SERIF_B, 19), cw - 24),
               x0 + 12, fy0 + 30, font(F_SERIF_B, 19), INK, 22)
    draw_scales(d, x0 + cw / 2, fy0 + 80, 1)
    draw_lines(d, wrap(d, "The world court rules Myanmar responsible for "
                          "genocide against the Rohingya.",
                       font(F_SANS, 13), cw - 24),
               x0 + 12, fy0 + 138, font(F_SANS, 13), INK, 17)
    # 3: Mexico
    x0 = cols[2]
    d.text((x0 + 12, fy0 + 10), "MEXICO  •  CAPTURE", font=font(F_SANS_B, 12), fill=RED)
    draw_lines(d, wrap(d, "'El Chapo Isidro' seized in Sinaloa", font(F_SERIF_B, 19), cw - 24),
               x0 + 12, fy0 + 30, font(F_SERIF_B, 19), INK, 22)
    draw_lines(d, wrap(d, "Forces capture the FBI's most-wanted cartel "
                          "kingpin, Fausto Isidro Meza Flores — "
                          "then gunmen hit back across the state.",
                       font(F_SANS, 13), cw - 24),
               x0 + 12, fy0 + 78, font(F_SANS, 13), INK, 17)
    d.rectangle([x0 + 12, fy1 - 30, x0 + cw - 12, fy1 - 12], outline=RED, width=2)
    centre(d, "FBI MOST WANTED  •  CAPTURED", x0 + cw / 2, fy1 - 27, font(F_SANS_B, 11), RED)

    # ---- numbered list: 32 more stories, 7 regions
    ly = 624
    d.text((MX, ly), "ALSO ON SATURDAY — 32 MORE STORIES", font=font(F_SERIF_B, 20), fill=INK)
    d.line([MX, ly + 28, W - MX, ly + 28], fill=INK, width=2)
    # distribute region groups over 3 columns, balanced by item count
    # (36 stories: col1 EUROPE 10, col2 MARKETS+NA+GLOBAL 11,
    #  col3 MIDDLE EAST+AFRICA&ASIA+S.AMERICA 11; 24px/item, 18px/header)
    groups = STORIES
    col_groups = [[groups[0]], [groups[1], groups[2], groups[6]], [groups[4], groups[5], groups[3]]]
    col_w = (W - 2 * MX - 2 * 16) / 3
    n = 4  # hero is story 01, the three features are 02-04
    for ci, cgroups in enumerate(col_groups):
        cx = MX + ci * (col_w + 16)
        cy = ly + 40
        for region, items in cgroups:
            d.text((cx, cy), region, font=font(F_SANS_B, 11), fill=RED)
            cy += 13
            d.line([cx, cy, cx + col_w, cy], fill=LINE, width=1)
            cy += 5
            for head, detail in items:
                n += 1
                d.text((cx, cy), "%02d" % n, font=font(F_MONO_B, 12), fill=NAVY)
                d.text((cx + 30, cy), head, font=font(F_SANS_B, 12), fill=INK)
                cy += 12
                d.text((cx + 30, cy), detail, font=font(F_SANS, 11), fill=(70, 70, 70))
                cy += 12

    # ---- footer
    d.line([MX, 990, W - MX, 990], fill=INK, width=1)
    centre(d, "THE WORLD TODAY  •  SATURDAY 21 NOVEMBER 2026  •  Sources: AP, NYT, The Telegraph, UN, ICJ",
           W // 2, 996, font(F_SANS, 10), GREY)

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
