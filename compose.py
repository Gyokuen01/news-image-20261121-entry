#!/usr/bin/env python3
"""Render THE WORLD TODAY front page for Saturday 21 November 2026.

A 1024x1024 newspaper front page: masthead, date band, a six-box stats
strip, a lead-story hero with three leader portraits, three feature
boxes, and a numbered list of 36 dated stories across 7 regions.

Built with Pillow only. Fully deterministic: no timestamps, no random
numbers, no network. Running this file twice produces a byte-identical
entry.png.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ canvas
W, H = 1024, 1024
CREAM = (246, 242, 233)
INK = (20, 20, 20)
NAVY = (16, 28, 64)
GOLD = (212, 175, 55)
RED = (178, 34, 34)
RED_SOFT = (205, 92, 92)
GREEN = (34, 139, 34)
GRAY = (110, 110, 105)
GRAY_DARK = (70, 70, 68)
GRAY_LINE = (180, 175, 165)
SKIN = (240, 200, 160)
MARGIN = 28
COL_W = 309
COL_GAP = 20
COL_X = [MARGIN, MARGIN + COL_W + COL_GAP, MARGIN + 2 * (COL_W + COL_GAP)]

# ------------------------------------------------------------------ fonts
FONT_DIRS = [
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/dejavu",
]


def load_font(basename, size):
    """Load a TTF by basename from the known font directories."""
    for folder in FONT_DIRS:
        path = os.path.join(folder, basename)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def serif_bold(size):
    return load_font("LiberationSerif-Bold.ttf", size)


def sans_bold(size):
    return load_font("LiberationSans-Bold.ttf", size)


def sans(size):
    return load_font("LiberationSans-Regular.ttf", size)


# ------------------------------------------------------------------ text
def wrap(draw, text, font, max_w):
    """Word-wrap text to fit max_w pixels; return a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def centered(draw, cx, y, text, font, fill):
    """Draw text horizontally centered on cx at y."""
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, y), text, font=font, fill=fill)


def right_aligned(draw, x, y, text, font, fill):
    """Draw text right-aligned so it ends at x."""
    w = draw.textlength(text, font=font)
    draw.text((x - w, y), text, font=font, fill=fill)


# ------------------------------------------------------------------ stories
# (number, headline, detail), grouped by column and region.
COLUMNS = [
    [
        ("EUROPE", [
            (5, "Kyiv hit overnight: 3 killed",
             "9 injured; bridges damaged, power cut — AP"),
            (6, "Kyiv bridges hit, power cut",
             "Strikes damage crossings; outages across city"),
            (7, "Kryvyi Rih missile strike",
             "2 killed, 60 wounded in Zelenskyy's hometown"),
            (8, "Trump: Europe must defund Kyiv",
             "US president's message to allies — Telegraph"),
            (9, "Russia rules out energy truce",
             "No ceasefire on energy, Moscow says"),
            (10, "No Black Sea truce either",
             "Moscow rejects a sea ceasefire too"),
            (11, "Kerch Bridge: revenge vowed",
             "Russia promises retaliation after bridge damage"),
            (12, "UK–EU landmark deal",
             "London and Brussels rebuild ties post-Brexit"),
            (13, "Rutte flies to Warsaw",
             "NATO chief visits Poland as Ukraine talks continue"),
            (14, "Zelenskyy rejects land swap",
             "Kyiv rules out ceding land in US peace plan"),
        ]),
    ],
    [
        ("MARKETS", [
            (15, "S&P 500 falls 3.7% on Friday",
             "Wall Street's worst day in the AI sell-off"),
            (16, "Nikkei plunges 5.06%",
             "Tokyo follows US markets sharply lower"),
            (17, "AI stocks lead the rout",
             "Chip and software shares drag indexes down"),
            (18, "Anthropic debuts near $2T",
             "AI lab lists on Wall Street Thursday"),
            (19, "Bitcoin slides with stocks",
             "Crypto joins the AI sell-off, down sharply"),
        ]),
        ("NORTH AMERICA", [
            (20, "'El Chapo Isidro' captured",
             "FBI most-wanted kingpin seized in Sinaloa"),
            (21, "Violence follows the arrest",
             "Gunmen hit back after forces move in"),
            (22, "US envoy meets Putin",
             "Witkoff in Moscow to discuss the peace plan"),
        ]),
        ("GLOBAL", [
            (23, "COP31 talks run past deadline",
             "Antalya summit overruns Friday in stalemate"),
            (24, "Fossil fuels block a deal",
             "Nations split over phase-out language"),
            (25, "UN food agency seeks $12bn",
             "Aid for 91 million people in 2027"),
        ]),
    ],
    [
        ("MIDDLE EAST", [
            (26, "Gaza: 7 killed in strikes",
             "Palestinians killed despite the ceasefire"),
            (27, "Houthis hit Saudi power plant",
             "Al-Shuqaiq station attacked in Jazan region"),
            (28, "Houthis hit Jazan port",
             "Second strike on Saudi Red Sea coast"),
            (29, "US weighs new Iran strikes",
             "Trump considers action as Israel presses"),
            (30, "Iran claims drone downed",
             "Tehran says it shot down a drone near its border"),
            (31, "Riyadh: oil output steady",
             "Saudi says output unaffected by Houthi strikes"),
        ]),
        ("AFRICA & ASIA", [
            (32, "ICJ: Myanmar guilty of genocide",
             "Court rules on Rohingya case at The Hague"),
            (33, "Ebola vaccine trials begin",
             "Trials launch in DR Congo"),
            (34, "S. Korea tops e-government",
             "No. 1 in UN digital government index"),
        ]),
        ("SOUTH AMERICA", [
            (35, "Peru quake: magnitude 6.7",
             "Andes tremor; no casualties reported yet"),
            (36, "Brazil dengue cases down 69%",
             "Wolbachia mosquitoes cut infections sharply"),
        ]),
    ],
]

STATS = [
    ("S&P 500", "-3.7%", RED),
    ("NIKKEI", "-5.06%", RED),
    ("PERU QUAKE", "M6.7", NAVY),
    ("KRYVYI RIH", "60 hurt", RED),
    ("ANTHROPIC", "≈$2T", GREEN),
    ("DENGUE", "-69%", GREEN),
]


# ------------------------------------------------------------------ pictures
def draw_portrait(draw, cx, top, hair, tie, name, title):
    """Draw a simple cartoon leader portrait: head, hair, suit, tie."""
    # Shoulders (trapezoid suit).
    draw.polygon(
        [(cx - 38, top + 110), (cx + 38, top + 110),
         (cx + 30, top + 60), (cx - 30, top + 60)],
        fill=(24, 24, 30),
    )
    # Shirt triangle and tie.
    draw.polygon(
        [(cx - 10, top + 60), (cx + 10, top + 60), (cx, top + 80)],
        fill=(245, 245, 245),
    )
    draw.polygon(
        [(cx - 5, top + 64), (cx + 5, top + 64),
         (cx + 4, top + 90), (cx, top + 96), (cx - 4, top + 90)],
        fill=tie,
    )
    # Head.
    draw.ellipse(
        [cx - 27, top, cx + 27, top + 54],
        fill=SKIN, outline=(200, 160, 120),
    )
    # Hair cap (top half of the head).
    draw.pieslice([cx - 27, top - 4, cx + 27, top + 26], 180, 360, fill=hair)
    # Eyes.
    draw.ellipse([cx - 14, top + 24, cx - 8, top + 28], fill=INK)
    draw.ellipse([cx + 8, top + 24, cx + 14, top + 28], fill=INK)
    # Name and title below the portrait.
    centered(draw, cx, top + 116, name, sans_bold(14), (255, 255, 255))
    centered(draw, cx, top + 134, title, sans(10), (180, 180, 180))


def draw_scales(draw, cx, top):
    """Draw a simple scales-of-justice icon."""
    draw.ellipse([cx - 4, top - 6, cx + 4, top + 2], fill=GOLD)
    draw.line([(cx, top), (cx, top + 52)], fill=INK, width=2)
    draw.line([(cx - 42, top + 12), (cx + 42, top + 12)], fill=INK, width=2)
    for sx in (cx - 42, cx + 42):
        draw.line([(sx, top + 12), (sx - 14, top + 34)], fill=INK, width=1)
        draw.line([(sx, top + 12), (sx + 14, top + 34)], fill=INK, width=1)
        draw.line([(sx, top + 12), (sx, top + 34)], fill=INK, width=1)
        draw.arc([sx - 14, top + 30, sx + 14, top + 44], 0, 180, fill=INK, width=2)
    draw.line([(cx - 16, top + 52), (cx + 16, top + 52)], fill=INK, width=2)


def draw_chart(draw, x, y, w):
    """Draw a small bar chart: S&P and Nikkei down, Anthropic up.

    Down-bars hang below the baseline, so their labels sit below the
    bar bottom (not at the baseline, where they would overlap the bar).
    Up-bars rise above the baseline and their labels sit below it.
    """
    base = y + 50
    bw, gap = 56, 20
    start = x + (w - (3 * bw + 2 * gap)) // 2
    bars = [
        ("S&P", "-3.7%", RED, -16),
        ("NIKKEI", "-5.06%", RED, -20),
        ("ANTHROPIC", "≈$2T", GREEN, 24),
    ]
    draw.line([(x, base), (x + w, base)], fill=GRAY, width=1)
    for i, (label, value, color, dh) in enumerate(bars):
        bx = start + i * (bw + gap)
        if dh < 0:
            # Bar hangs below the baseline; label goes under the bar.
            draw.rectangle([bx, base, bx + bw, base - dh], fill=color)
            centered(draw, bx + bw // 2, base - dh // 2 - 6, value,
                     sans_bold(11), (255, 255, 255))
            centered(draw, bx + bw // 2, base - dh + 6, label, sans_bold(10), INK)
        else:
            # Bar rises above the baseline; label goes under the baseline.
            draw.rectangle([bx, base - dh, bx + bw, base], fill=color)
            centered(draw, bx + bw // 2, base - dh // 2 - 6, value,
                     sans_bold(11), (255, 255, 255))
            centered(draw, bx + bw // 2, base + 6, label, sans_bold(10), INK)


# ------------------------------------------------------------------ render
def render():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # Top meta line and rule.
    draw.text((MARGIN, 8), "VOL. 2026 — No. 325", font=sans(11), fill=GRAY)
    right_aligned(draw, W - MARGIN, 8, "PRICE: ONE DAY'S NEWS", sans(11), GRAY)
    draw.line([(MARGIN, 28), (W - MARGIN, 28)], fill=INK, width=1)

    # Masthead.
    centered(draw, W // 2, 34, "THE WORLD TODAY", serif_bold(72), INK)
    draw.line([(MARGIN, 108), (W - MARGIN, 108)], fill=INK, width=2)

    # Date band (navy).
    draw.rectangle([MARGIN, 114, W - MARGIN, 154], fill=NAVY)
    draw.text((MARGIN + 20, 124), "SATURDAY • 21 NOVEMBER 2026",
              font=sans_bold(20), fill=(255, 255, 255))
    right_aligned(draw, W - MARGIN - 20, 128, "36 STORIES • 7 REGIONS",
                  sans_bold(16), GOLD)

    # Stats strip: six boxes.
    box_w, box_gap = 155, 7
    for i, (label, value, color) in enumerate(STATS):
        bx = MARGIN + i * (box_w + box_gap)
        draw.rectangle([bx, 160, bx + box_w, 206],
                       fill=(255, 255, 255), outline=GRAY_LINE)
        centered(draw, bx + box_w // 2, 165, label, sans(11), GRAY)
        centered(draw, bx + box_w // 2, 182, value, sans_bold(20), color)
    draw.line([(MARGIN, 212), (W - MARGIN, 212)], fill=RED, width=3)

    # Hero (navy).
    draw.rectangle([MARGIN, 218, W - MARGIN, 414], fill=NAVY)
    draw.text((MARGIN + 20, 230), "SUMMIT AFTERMATH — THE LEAD STORY",
              font=sans_bold(13), fill=GOLD)
    draw.text((MARGIN + 20, 250), "PEACE PLAN PUBLISHED —",
              font=serif_bold(38), fill=(255, 255, 255))
    draw.text((MARGIN + 20, 292), "THEN THE BOMBS FELL",
              font=serif_bold(38), fill=(255, 255, 255))
    draw.text((MARGIN + 20, 340),
              "Trump, Putin and Xi closed their summit with a peace declaration — then Russia",
              font=sans(15), fill=(255, 255, 255))
    draw.text((MARGIN + 20, 360),
              "launched its heaviest strikes on Kyiv and Kryvyi Rih in weeks.",
              font=sans(15), fill=(255, 255, 255))
    w1 = draw.textlength("KYIV: 3 KILLED, 9 INJURED  •  ", font=sans_bold(12))
    draw.text((MARGIN + 20, 388), "KYIV: 3 KILLED, 9 INJURED  •  ",
              font=sans_bold(12), fill=RED_SOFT)
    draw.text((MARGIN + 20 + w1, 388), "KRYVYI RIH: 2 KILLED, 60 WOUNDED",
              font=sans_bold(12), fill=GOLD)

    # Three leader portraits on the right of the hero.
    draw_portrait(draw, 735, 238, (245, 215, 110), RED, "TRUMP", "US President")
    draw_portrait(draw, 835, 238, (20, 20, 20), RED, "XI", "China's leader")
    draw_portrait(draw, 935, 238, (205, 205, 205), (40, 80, 160),
                  "PUTIN", "Russia's leader")

    # Three feature boxes.
    feat_y, feat_h = 420, 172
    for i, fx in enumerate(COL_X):
        draw.rectangle([fx, feat_y, fx + COL_W, feat_y + feat_h],
                       fill=(255, 255, 255), outline=GRAY_LINE)

    # Feature 1: markets.
    fx = COL_X[0]
    draw.text((fx + 14, 430), "MARKETS IN TURMOIL", font=sans_bold(12), fill=RED)
    for j, line in enumerate(wrap(draw, "Wall Street's AI sell-off goes global",
                                  serif_bold(19), COL_W - 28)):
        draw.text((fx + 14, 448 + j * 22), line, font=serif_bold(19), fill=INK)
    draw_chart(draw, fx + 14, 500, COL_W - 28)

    # Feature 2: The Hague.
    fx = COL_X[1]
    draw.text((fx + 14, 430), "THE HAGUE • JUSTICE", font=sans_bold(12), fill=RED)
    for j, line in enumerate(wrap(draw, "Myanmar guilty of genocide",
                                  serif_bold(19), COL_W - 28)):
        draw.text((fx + 14, 448 + j * 22), line, font=serif_bold(19), fill=INK)
    draw_scales(draw, fx + COL_W // 2, 512)
    for j, line in enumerate(wrap(
            draw, "The world court rules Myanmar responsible for genocide against the Rohingya.",
            sans(12), COL_W - 28)):
        draw.text((fx + 14, 566 + j * 15), line, font=sans(12), fill=GRAY_DARK)

    # Feature 3: Mexico.
    fx = COL_X[2]
    draw.text((fx + 14, 430), "MEXICO • CAPTURE", font=sans_bold(12), fill=RED)
    for j, line in enumerate(wrap(draw, "'El Chapo Isidro' seized in Sinaloa",
                                  serif_bold(19), COL_W - 28)):
        draw.text((fx + 14, 448 + j * 22), line, font=serif_bold(19), fill=INK)
    for j, line in enumerate(wrap(
            draw, "Forces capture the FBI's most-wanted cartel kingpin, Fausto Isidro Meza Flores — then gunmen hit back across the state.",
            sans(13), COL_W - 28)):
        draw.text((fx + 14, 502 + j * 16), line, font=sans(13), fill=INK)
    draw.rectangle([fx + 14, 566, fx + COL_W - 14, 586], outline=RED, width=2)
    centered(draw, fx + COL_W // 2, 571, "FBI MOST WANTED • CAPTURED",
             sans_bold(12), RED)

    # "Also on Saturday" heading and rule.
    draw.text((MARGIN, 600), "ALSO ON SATURDAY — 32 MORE STORIES",
              font=serif_bold(22), fill=INK)
    draw.line([(MARGIN, 630), (W - MARGIN, 630)], fill=INK, width=2)

    # Numbered story columns.
    num_font = sans_bold(12)
    head_font = sans_bold(12)
    det_font = sans(10)
    for col_i, groups in enumerate(COLUMNS):
        x = COL_X[col_i]
        y = 640
        for region, stories in groups:
            draw.text((x, y), region, font=sans_bold(13), fill=RED)
            y += 18
            for number, headline, detail in stories:
                draw.text((x, y), "%02d" % number, font=num_font, fill=INK)
                for j, line in enumerate(wrap(draw, headline, head_font, COL_W - 22)):
                    draw.text((x + 22, y + j * 13), line, font=head_font, fill=INK)
                for j, line in enumerate(wrap(draw, detail, det_font, COL_W - 22)):
                    draw.text((x + 22, y + 12 + j * 12), line, font=det_font, fill=GRAY_DARK)
                y += 24

    # Footer.
    centered(draw, W // 2, 1000,
             "THE WORLD TODAY • SATURDAY 21 NOVEMBER 2026 • Sources: AP, NYT, The Telegraph, UN, ICJ",
             sans(11), GRAY)
    return img


def main():
    img = render()
    img.save("entry.png")
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
