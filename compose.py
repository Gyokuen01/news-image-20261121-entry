#!/usr/bin/env python3
"""Render THE WORLD TODAY front page, v4, for Saturday 21 November 2026.

A 1024x1024 newspaper front page: masthead, date band, a six-box stats
strip, a lead-story hero (Iran strikes US bases in Bahrain; Russia's
triple-tap kills a boy of 7 in Kryvyi Rih; missiles down in Poland),
three feature boxes (markets sell-off chart, APEC three-way summit,
ICJ Myanmar genocide ruling), and a numbered list of 36 dated stories
across 8 regions (40 stories in all, hero and features included).

Stories were checked against reporting of 21 November 2026 (AP, CNN,
Majik Morning Brief, One Turn, Standard Topic, IQMIA). The hero drops
v3's overstated "peace declaration" framing: the Shenzhen summit ended
with no breakthrough.

Built with Pillow only. Fully deterministic: no timestamps, no random
numbers, no network. Running this file twice produces a byte-identical
entry.png.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas
PAGE_W, PAGE_H = 1024, 1024
PAPER = (246, 242, 233)
INK = (18, 18, 18)
NAVY = (14, 26, 60)
GOLD = (212, 175, 55)
CRIMSON = (172, 30, 30)
CRIMSON_LT = (205, 92, 92)
FOREST = (30, 130, 30)
MUTED = (112, 112, 106)
DARK_GRAY = (72, 72, 70)
RULE_GRAY = (182, 177, 166)
SKIN_TONE = (240, 200, 160)
EDGE = 28
COL_WIDTH = 309
COL_STEP = 329
COL_LEFT = [EDGE, EDGE + COL_STEP, EDGE + 2 * COL_STEP]

# ----------------------------------------------------------------- fonts
FONT_FOLDERS = [
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/dejavu",
]


def font_for(filename, size):
    """Find a TTF by filename in the known font folders."""
    for folder in FONT_FOLDERS:
        candidate = os.path.join(folder, filename)
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size)


def serif(size):
    return font_for("LiberationSerif-Bold.ttf", size)


def sans_b(size):
    return font_for("LiberationSans-Bold.ttf", size)


def sans_r(size):
    return font_for("LiberationSans-Regular.ttf", size)


# ----------------------------------------------------------------- text
def wrap_text(d, text, fnt, max_w):
    """Split text into lines that fit max_w pixels."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_c(d, cx, y, text, fnt, fill):
    """Draw text centred on cx."""
    w = d.textlength(text, font=fnt)
    d.text((cx - w / 2, y), text, font=fnt, fill=fill)


def text_r(d, x, y, text, fnt, fill):
    """Draw text right-aligned to end at x."""
    w = d.textlength(text, font=fnt)
    d.text((x - w, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- stories
# (number, headline, detail) grouped by column and region.
# All 36 verified against 21 November 2026 reporting. Column heights
# are balanced (12 stories each) so no column runs into the footer.
STORY_COLS = [
    [
        ("EUROPE", [
            (1, "Kryvyi Rih triple-tap kills boy, 7",
             "Paramedic, 20, also killed; 60 hurt"),
            (2, "Kyiv hit: fires, water cut",
             "Debris falls in 5 districts; 1 hurt"),
            (3, "Missiles land in Poland",
             "NATO soil hit; Warsaw calls it provocation"),
            (4, "Biggest Nov barrage: 404 drones",
             "111 missiles fired; 8 killed in Kyiv"),
            (5, 'Zelensky: Putin is a "killer"',
             "After Trump calls Putin 'my friend'"),
            (6, 'Ukraine "Bear Trap" frees land',
             "200 sq km, 14 settlements in Kharkiv"),
            (7, "Kerch Bridge: Kyiv defends strikes",
             "Zelensky: justified reply to bridge attacks"),
        ]),
        ("MIDDLE EAST", [
            (8, "Iran strikes US bases in Bahrain",
             "2 bases hit; fire at industrial site"),
            (9, "Iran downs US drone near Qeshm",
             "Tehran claims kill; US denies F-16 hit"),
            (10, "Houthis hit Saudi power plant",
             "Al-Shuqaiq station attacked in Jazan"),
            (11, "Houthis hit Jazan port",
             "Second strike on Saudi Red Sea coast"),
            (12, "Israel plans West Bank city",
             "New city for 200,000 advances"),
        ]),
    ],
    [
        ("APEC & ASIA", [
            (13, "Xi hosts Trump, Putin at APEC",
             "Three leaders meet in Shenzhen"),
            (14, "Summit ends, no breakthrough",
             "Trump: Putin 'my friend'; no deal"),
            (15, "Nvidia halts H200 chip exports",
             "China sales blocked amid US debate"),
            (16, "Chinese AI stocks shed $1.7T",
             "Tech sell-off deepens since June"),
        ]),
        ("MARKETS", [
            (17, "S&P 500 falls 3.7%",
             "Wall Street slides into correction"),
            (18, "Nasdaq erases 2026 gains",
             "Tech rout wipes out year's rise"),
            (19, "Nikkei plunges 5.06%",
             "Tokyo follows US markets lower"),
            (20, "AI stocks lead the rout",
             "Chip shares drag indexes down"),
            (21, "Bitcoin falls toward $62K",
             "Crypto liquidations top $2bn"),
        ]),
        ("GLOBAL", [
            (22, "COP31 runs past deadline",
             "Antalya summit overruns in stalemate"),
            (23, "Fossil fuels block a deal",
             "Draft drops phase-out language"),
            (24, "UN food agency seeks $12bn",
             "Aid for 91 million people in 2027"),
        ]),
    ],
    [
        ("NORTH AMERICA", [
            (25, '"El Chapo Isidro" captured',
             "FBI most-wanted kingpin seized in Sinaloa"),
            (26, "Violence follows the arrest",
             "Gunmen hit back; at least 11 dead"),
            (27, "FBI probes database hack",
             "Apparent breach of criminal records"),
            (28, "Trump: ban overseas AI centres",
             "US firms barred from building abroad"),
        ]),
        ("AFRICA & ASIA", [
            (29, "ICJ: Myanmar guilty of genocide",
             "Court rules on Rohingya case"),
            (30, "Mongolia president resigns",
             "Snap elections within 4 months"),
            (31, "Denmark: Russia plotted killing",
             "Target was US-Ukrainian rapper"),
            (32, "Drones hit Russia-bound ship",
             "Cargo vessel burns near Finland"),
            (33, "S. Korea tops e-government",
             "No. 1 in UN digital index"),
        ]),
        ("SOUTH AMERICA", [
            (34, "Peru quake shakes the Andes",
             "Strong tremor; no casualties yet"),
            (35, "Brazil dengue cases down 69%",
             "Wolbachia mosquitoes cut infections"),
            (36, "Ebola vaccine trials begin",
             "Trials launch in DR Congo"),
        ]),
    ],
]

STAT_BOXES = [
    ("IRAN STRIKES", "2 US bases", CRIMSON),
    ("KRYVYI RIH", "Boy, 7, killed", CRIMSON),
    ("S&P 500", "-3.7%", CRIMSON),
    ("NIKKEI", "-5.06%", CRIMSON),
    ("BITCOIN", "$62K", NAVY),
    ("COP31", "No deal", NAVY),
]


# -------------------------------------------------------------- pictures
def draw_leader(d, cx, top, hair, tie, name, role):
    """Cartoon leader portrait: suit, shirt, tie, head, hair, eyes."""
    d.polygon(
        [(cx - 38, top + 110), (cx + 38, top + 110),
         (cx + 30, top + 60), (cx - 30, top + 60)],
        fill=(24, 24, 30),
    )
    d.polygon(
        [(cx - 10, top + 60), (cx + 10, top + 60), (cx, top + 80)],
        fill=(245, 245, 245),
    )
    d.polygon(
        [(cx - 5, top + 64), (cx + 5, top + 64),
         (cx + 4, top + 90), (cx, top + 96), (cx - 4, top + 90)],
        fill=tie,
    )
    d.ellipse(
        [cx - 27, top, cx + 27, top + 54],
        fill=SKIN_TONE, outline=(200, 160, 120),
    )
    d.pieslice([cx - 27, top - 4, cx + 27, top + 26], 180, 360, fill=hair)
    d.ellipse([cx - 14, top + 24, cx - 8, top + 28], fill=INK)
    d.ellipse([cx + 8, top + 24, cx + 14, top + 28], fill=INK)
    text_c(d, cx, top + 116, name, sans_b(14), (255, 255, 255))
    text_c(d, cx, top + 134, role, sans_r(10), (180, 180, 180))


def draw_justice(d, cx, top):
    """Scales-of-justice icon."""
    d.ellipse([cx - 4, top - 6, cx + 4, top + 2], fill=GOLD)
    d.line([(cx, top), (cx, top + 52)], fill=INK, width=2)
    d.line([(cx - 42, top + 12), (cx + 42, top + 12)], fill=INK, width=2)
    for sx in (cx - 42, cx + 42):
        d.line([(sx, top + 12), (sx - 14, top + 34)], fill=INK, width=1)
        d.line([(sx, top + 12), (sx + 14, top + 34)], fill=INK, width=1)
        d.line([(sx, top + 12), (sx, top + 34)], fill=INK, width=1)
        d.arc([sx - 14, top + 30, sx + 14, top + 44], 0, 180, fill=INK, width=2)
    d.line([(cx - 16, top + 52), (cx + 16, top + 52)], fill=INK, width=2)


def draw_bars(d, x, y, w):
    """Bar chart: three markets down on the day. Down-bars hang below
    the baseline, so their value labels sit inside the bar and the name
    labels sit below the bar bottom."""
    base = y + 50
    bw, gap = 56, 20
    start = x + (w - (3 * bw + 2 * gap)) // 2
    bars = [
        ("S&P", "-3.7%", CRIMSON, 16),
        ("NIKKEI", "-5.06%", CRIMSON, 20),
        ("BITCOIN", "$62K", CRIMSON, 24),
    ]
    d.line([(x, base), (x + w, base)], fill=MUTED, width=1)
    for i, (label, value, color, depth) in enumerate(bars):
        bx = start + i * (bw + gap)
        d.rectangle([bx, base, bx + bw, base + depth], fill=color)
        text_c(d, bx + bw // 2, base + depth // 2 - 6, value,
               sans_b(11), (255, 255, 255))
        text_c(d, bx + bw // 2, base + depth + 6, label, sans_b(10), INK)


# ---------------------------------------------------------------- render
def render_page():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(img)

    # Top meta line and rule.
    d.text((EDGE, 8), "VOL. 2026 — No. 325", font=sans_r(11), fill=MUTED)
    text_r(d, PAGE_W - EDGE, 8, "PRICE: ONE DAY'S NEWS", sans_r(11), MUTED)
    d.line([(EDGE, 28), (PAGE_W - EDGE, 28)], fill=INK, width=1)

    # Masthead.
    text_c(d, PAGE_W // 2, 34, "THE WORLD TODAY", serif(72), INK)
    d.line([(EDGE, 108), (PAGE_W - EDGE, 108)], fill=INK, width=2)

    # Date band (navy).
    d.rectangle([EDGE, 114, PAGE_W - EDGE, 154], fill=NAVY)
    d.text((EDGE + 20, 124), "SATURDAY • 21 NOVEMBER 2026",
           font=sans_b(20), fill=(255, 255, 255))
    text_r(d, PAGE_W - EDGE - 20, 128, "40 STORIES • 8 REGIONS",
           sans_b(16), GOLD)

    # Stats strip: six boxes.
    box_w, box_gap = 155, 7
    for i, (label, value, color) in enumerate(STAT_BOXES):
        bx = EDGE + i * (box_w + box_gap)
        d.rectangle([bx, 160, bx + box_w, 206],
                    fill=(255, 255, 255), outline=RULE_GRAY)
        text_c(d, bx + box_w // 2, 165, label, sans_r(11), MUTED)
        text_c(d, bx + box_w // 2, 182, value, sans_b(20), color)
    d.line([(EDGE, 212), (PAGE_W - EDGE, 212)], fill=CRIMSON, width=3)

    # Hero (navy): the strikes.
    d.rectangle([EDGE, 218, PAGE_W - EDGE, 414], fill=NAVY)
    d.text((EDGE + 20, 230), "THE LEAD STORY — STRIKES ON TWO FRONTS",
           font=sans_b(13), fill=GOLD)
    d.text((EDGE + 20, 250), "IRAN STRIKES US BASES —",
           font=serif(38), fill=(255, 255, 255))
    d.text((EDGE + 20, 292), "A BOY, 7, DIES IN UKRAINE",
           font=serif(38), fill=(255, 255, 255))
    d.text((EDGE + 20, 340),
           "Tehran says it hit two American bases in Bahrain; a fire burns at an",
           font=sans_r(15), fill=(255, 255, 255))
    d.text((EDGE + 20, 360),
           "industrial site. In Kryvyi Rih, Russia's triple-tap kills a child and a paramedic.",
           font=sans_r(15), fill=(255, 255, 255))
    tick = "POLAND: MISSILES DOWN ON NATO SOIL  •  APEC: THREE LEADERS, NO BREAKTHROUGH"
    d.text((EDGE + 20, 388), tick, font=sans_b(12), fill=CRIMSON_LT)

    # Three leader portraits on the right of the hero (APEC summit).
    draw_leader(d, 735, 238, (245, 215, 110), CRIMSON, "TRUMP", "US President")
    draw_leader(d, 835, 238, (20, 20, 20), CRIMSON, "XI", "China's leader")
    draw_leader(d, 935, 238, (205, 205, 205), (40, 80, 160),
                "PUTIN", "Russia's leader")

    # Three feature boxes.
    feat_y, feat_h = 420, 172
    for fx in COL_LEFT:
        d.rectangle([fx, feat_y, fx + COL_WIDTH, feat_y + feat_h],
                    fill=(255, 255, 255), outline=RULE_GRAY)

    # Feature 1: markets.
    fx = COL_LEFT[0]
    d.text((fx + 14, 430), "MARKETS IN TURMOIL", font=sans_b(12), fill=CRIMSON)
    for j, line in enumerate(wrap_text(d, "Stocks slide into correction",
                                       serif(19), COL_WIDTH - 28)):
        d.text((fx + 14, 448 + j * 22), line, font=serif(19), fill=INK)
    draw_bars(d, fx + 14, 500, COL_WIDTH - 28)

    # Feature 2: APEC summit.
    fx = COL_LEFT[1]
    d.text((fx + 14, 430), "APEC • SHENZHEN", font=sans_b(12), fill=CRIMSON)
    for j, line in enumerate(wrap_text(d, "Three leaders, no breakthrough",
                                       serif(19), COL_WIDTH - 28)):
        d.text((fx + 14, 448 + j * 22), line, font=serif(19), fill=INK)
    for j, line in enumerate(wrap_text(
            d, "Xi hosts Trump and Putin. Trump calls Putin 'my friend'; "
               "Zelensky calls him a killer.",
            sans_r(13), COL_WIDTH - 28)):
        d.text((fx + 14, 502 + j * 16), line, font=sans_r(13), fill=INK)
    d.rectangle([fx + 14, 566, fx + COL_WIDTH - 14, 586], outline=CRIMSON, width=2)
    text_c(d, fx + COL_WIDTH // 2, 571, "NO DEAL IN SHENZHEN",
           sans_b(12), CRIMSON)

    # Feature 3: The Hague.
    fx = COL_LEFT[2]
    d.text((fx + 14, 430), "THE HAGUE • JUSTICE", font=sans_b(12), fill=CRIMSON)
    for j, line in enumerate(wrap_text(d, "Myanmar guilty of genocide",
                                       serif(19), COL_WIDTH - 28)):
        d.text((fx + 14, 448 + j * 22), line, font=serif(19), fill=INK)
    draw_justice(d, fx + COL_WIDTH // 2, 512)
    for j, line in enumerate(wrap_text(
            d, "The world court rules Myanmar responsible for genocide "
               "against the Rohingya; reparations ordered.",
            sans_r(12), COL_WIDTH - 28)):
        d.text((fx + 14, 566 + j * 15), line, font=sans_r(12), fill=DARK_GRAY)

    # "Also on Saturday" heading and rule.
    d.text((EDGE, 600), "ALSO ON SATURDAY — 36 MORE STORIES",
           font=serif(22), fill=INK)
    d.line([(EDGE, 630), (PAGE_W - EDGE, 630)], fill=INK, width=2)

    # Numbered story columns.
    for col_i, groups in enumerate(STORY_COLS):
        x = COL_LEFT[col_i]
        y = 640
        for region, stories in groups:
            d.text((x, y), region, font=sans_b(13), fill=CRIMSON)
            y += 18
            for number, headline, detail in stories:
                d.text((x, y), "%02d" % number, font=sans_b(12), fill=INK)
                for j, line in enumerate(
                        wrap_text(d, headline, sans_b(12), COL_WIDTH - 22)):
                    d.text((x + 22, y + j * 13), line, font=sans_b(12), fill=INK)
                for j, line in enumerate(
                        wrap_text(d, detail, sans_r(10), COL_WIDTH - 22)):
                    d.text((x + 22, y + 12 + j * 12), line, font=sans_r(10),
                           fill=DARK_GRAY)
                y += 24

    # Footer.
    text_c(d, PAGE_W // 2, 1000,
           "THE WORLD TODAY • SATURDAY 21 NOVEMBER 2026 • Sources: AP, CNN, UN, ICJ, ISW",
           sans_r(11), MUTED)
    return img


def main():
    img = render_page()
    img.save("entry.png")
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
