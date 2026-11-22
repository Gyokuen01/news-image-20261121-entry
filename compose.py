#!/usr/bin/env python3
"""THE WORLD TODAY - front page for Saturday 21 November 2026.

Renders a 1024x1024 newspaper front page with Pillow (stdlib + PIL only).
Every headline below was transcribed by eye from the reference front page;
the layout is rebuilt from scratch in this file: masthead, date bar, news
ticker, lead story with three leader portraits, three feature boxes, and 36
numbered stories in three columns.

Usage:
    python3 compose.py [output-path]

With no path, the image goes to $MAKEFUN_OUTPUT_DIR/entry.png, falling
back to ./entry.png. Rendering is deterministic: same bytes every run.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 28
CONTENT_W = PAGE_W - 2 * MARGIN

PAPER = (243, 238, 226)
CARD = (255, 255, 255)
INK = (26, 26, 26)
NAVY = (17, 23, 56)
CRIMSON = (168, 30, 34)
GOLD = (214, 158, 58)
GREY = (112, 109, 100)
FAINT = (152, 149, 140)
HAIRLINE = (96, 94, 86)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

_font_cache = {}


def face(path, size):
    """Cached truetype font; size is an int."""
    key = (path, int(size))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, int(size))
    return _font_cache[key]


def text_w(f, s):
    return f.getlength(s)


def wrap_text(f, s, width):
    """Greedy word wrap; each returned line fits `width` where possible."""
    words = s.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(f, trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_size(path, s, start, width, floor):
    """Largest size from `start` down to `floor` whose text fits `width`."""
    size = start
    while size > floor and text_w(face(path, size), s) > width:
        size -= 1
    return size


def draw_centered(d, cx, y, s, f, fill):
    d.text((cx, y), s, font=f, fill=fill, anchor="ma")


# ---------------------------------------------------------------- data

TICKER = [
    ("IRAN STRIKES", "2 US bases", CRIMSON),
    ("KRYVYI RIH", "Boy, 7, killed", CRIMSON),
    ("S&P 500", "-3.7%", CRIMSON),
    ("NIKKEI", "-5.06%", CRIMSON),
    ("BITCOIN", "$62K", NAVY),
    ("COP31", "No deal", NAVY),
]

LEAD_KICKER = "THE LEAD STORY \u2014 STRIKES ON TWO FRONTS"
LEAD_HEAD = ["IRAN STRIKES US BASES \u2014", "A BOY, 7, DIES IN UKRAINE"]
LEAD_DECK = (
    "Tehran says it hit two American bases in Bahrain; a fire burns at an "
    "industrial site. In Kryvyi Rih, Russia's triple-tap kills a child and "
    "a paramedic."
)
LEAD_FOOT = (
    "POLAND: MISSILES DOWN ON NATO SOIL  \u2022  "
    "APEC: THREE LEADERS, NO BREAKTHROUGH"
)

# (name, role, hair colour, skin colour, tie colour)
LEADERS = [
    ("TRUMP", "US President", (238, 198, 92), (248, 212, 168), CRIMSON),
    ("XI", "China's leader", (22, 22, 22), (232, 190, 150), CRIMSON),
    ("PUTIN", "Russia's leader", (198, 198, 198), (238, 205, 175), (32, 72, 150)),
]

MARKET_BARS = [
    ("-3.7%", "S&P"),
    ("-5.06%", "NIKKEI"),
    ("$62K", "BITCOIN"),
]

APEC_BODY = (
    "Xi hosts Trump and Putin. Trump calls Putin 'my friend'; "
    "Zelensky calls him a killer."
)

HAGUE_BODY = (
    "The world court rules Myanmar responsible for genocide; "
    "reparations ordered."
)

# (section heading, [(headline, deck), ...]) per column, in reading order.
COLUMNS = [
    ("EUROPE", [
        ("Kryvyi Rih triple-tap kills boy, 7",
         "Paramedic, 20, also killed; 60 hurt"),
        ("Kyiv hit: fires, water cut",
         "Debris falls in 5 districts; 1 hurt"),
        ("Missiles land in Poland",
         "NATO soil hit; Warsaw calls it provocation"),
        ("Biggest Nov barrage: 404 drones",
         "111 missiles fired; 8 killed in Kyiv"),
        ("Zelensky: Putin is a \u201ckiller\u201d",
         "After Trump calls Putin 'my friend'"),
        ("Ukraine \u201cBear Trap\u201d frees land",
         "200 sq km, 14 settlements in Kharkiv"),
        ("Kerch Bridge: Kyiv defends strikes",
         "Zelensky: justified reply to bridge attacks"),
    ]),
    ("MIDDLE EAST", [
        ("Iran strikes US bases in Bahrain",
         "2 bases hit; fire at industrial site"),
        ("Iran downs US drone near Qeshm",
         "Tehran claims kill; US denies F-16 hit"),
        ("Houthis hit Saudi power plant",
         "Al-Shuqaiq station attacked in Jazan"),
        ("Houthis hit Jazan port",
         "Second strike on Saudi Red Sea coast"),
        ("Israel plans West Bank city",
         "New city for 200,000 advances"),
    ]),
    ("APEC & ASIA", [
        ("Xi hosts Trump, Putin at APEC",
         "Three leaders meet in Shenzhen"),
        ("Summit ends, no breakthrough",
         "Trump: Putin 'my friend'; no deal"),
        ("Nvidia halts H200 chip exports",
         "China sales blocked amid US debate"),
        ("Chinese AI stocks shed $1.7T",
         "Tech sell-off deepens since June"),
    ]),
    ("MARKETS", [
        ("S&P 500 falls 3.7%",
         "Wall Street slides into correction"),
        ("Nasdaq erases 2026 gains",
         "Tech rout wipes out year's rise"),
        ("Nikkei plunges 5.06%",
         "Tokyo follows US markets lower"),
        ("AI stocks lead the rout",
         "Chip shares drag indexes down"),
        ("Bitcoin falls toward $62K",
         "Crypto liquidations top $2bn"),
    ]),
    ("GLOBAL", [
        ("COP31 runs past deadline",
         "Antalya summit overruns in stalemate"),
        ("Fossil fuels block a deal",
         "Draft drops phase-out language"),
        ("UN food agency seeks $12bn",
         "Aid for 91 million people in 2027"),
    ]),
    ("NORTH AMERICA", [
        ("\u201cEl Chapo Isidro\u201d captured",
         "FBI most-wanted kingpin seized in Sinaloa"),
        ("Violence follows the arrest",
         "Gunmen hit back; at least 11 dead"),
        ("FBI probes database hack",
         "Apparent breach of criminal records"),
        ("Trump: ban overseas AI centres",
         "US firms barred from building abroad"),
    ]),
    ("AFRICA & ASIA", [
        ("ICJ: Myanmar guilty of genocide",
         "Court rules on Rohingya case"),
        ("Mongolia president resigns",
         "Snap elections within 4 months"),
        ("Denmark: Russia plotted killing",
         "Target was US-Ukrainian rapper"),
        ("Drones hit Russia-bound ship",
         "Cargo vessel burns near Finland"),
        ("S. Korea tops e-government",
         "No. 1 in UN digital index"),
    ]),
    ("SOUTH AMERICA", [
        ("Peru quake shakes the Andes",
         "Strong tremor; no casualties yet"),
        ("Brazil dengue cases down 69%",
         "Wolbachia mosquitoes cut infections"),
        ("Ebola vaccine trials begin",
         "Trials launch in DR Congo"),
    ]),
]

# Column 1 holds sections 0-1, column 2 holds 2-4, column 3 holds 5-7.
COLUMN_LAYOUT = [(0, 2), (2, 5), (5, 8)]

FOOTER = (
    "THE WORLD TODAY \u2022 SATURDAY 21 NOVEMBER 2026 \u2022 "
    "Sources: AP, CNN, UN, ICJ, ISW"
)


# ---------------------------------------------------------------- sections

def draw_top_meta(d):
    f = face(SANS, 11)
    d.text((MARGIN, 8), "VOL. 2026 \u2014 No. 325", font=f, fill=GREY)
    tag = "PRICE: ONE DAY'S NEWS"
    d.text((PAGE_W - MARGIN, 8), tag, font=f, fill=GREY, anchor="ra")
    d.line([(MARGIN, 27), (PAGE_W - MARGIN, 27)], fill=INK, width=1)


def draw_masthead(d):
    size = fit_size(SERIF_B, "THE WORLD TODAY", 88, CONTENT_W - 10, 60)
    f = face(SERIF_B, size)
    draw_centered(d, PAGE_W // 2, 32, "THE WORLD TODAY", f, INK)
    d.line([(MARGIN, 112), (PAGE_W - MARGIN, 112)], fill=INK, width=3)
    d.line([(MARGIN, 117), (PAGE_W - MARGIN, 117)], fill=INK, width=1)


def draw_date_bar(d):
    y0, y1 = 121, 149
    d.rectangle([MARGIN, y0, PAGE_W - MARGIN, y1], fill=NAVY)
    left = face(SANS_B, 19)
    d.text((MARGIN + 14, (y0 + y1) // 2), "SATURDAY \u2022 21 NOVEMBER 2026",
           font=left, fill=CARD, anchor="lm")
    right = face(SANS_B, 17)
    d.text((PAGE_W - MARGIN - 14, (y0 + y1) // 2), "40 STORIES \u2022 8 REGIONS",
           font=right, fill=GOLD, anchor="rm")


def draw_ticker(d):
    y0, y1 = 155, 191
    gap = 6
    box_w = (CONTENT_W - gap * (len(TICKER) - 1)) // len(TICKER)
    x = MARGIN
    for label, value, colour in TICKER:
        d.rectangle([x, y0, x + box_w, y1], fill=CARD, outline=FAINT, width=1)
        lf = face(SANS, 10)
        draw_centered(d, x + box_w // 2, y0 + 5, label, lf, GREY)
        size = fit_size(SANS_B, value, 19, box_w - 12, 14)
        vf = face(SANS_B, size)
        draw_centered(d, x + box_w // 2, y0 + 17, value, vf, colour)
        x += box_w + gap
    d.line([(MARGIN, 196), (PAGE_W - MARGIN, 196)], fill=CRIMSON, width=2)


def draw_portrait(d, cx, top, hair, skin, tie):
    """Flat front-facing leader: hair, face, suit shoulders, tie."""
    # shoulders / suit
    d.polygon([(cx - 44, top + 90), (cx - 38, top + 52), (cx - 18, top + 44),
               (cx + 18, top + 44), (cx + 38, top + 52), (cx + 44, top + 90)],
              fill=(24, 24, 28))
    # shirt V
    d.polygon([(cx - 12, top + 46), (cx + 12, top + 46), (cx, top + 66)],
              fill=CARD)
    # tie
    d.polygon([(cx - 6, top + 50), (cx + 6, top + 50), (cx + 8, top + 78),
               (cx, top + 90), (cx - 8, top + 78)], fill=tie)
    # head
    d.ellipse([cx - 24, top, cx + 24, top + 48], fill=skin)
    # hair cap
    d.pieslice([cx - 25, top - 4, cx + 25, top + 26], 180, 360, fill=hair)
    # eyes
    d.ellipse([cx - 13, top + 20, cx - 9, top + 24], fill=INK)
    d.ellipse([cx + 9, top + 20, cx + 13, top + 24], fill=INK)
    # mouth
    d.line([(cx - 6, top + 36), (cx + 6, top + 36)], fill=(120, 70, 60),
           width=2)


def draw_lead(d):
    y0, y1 = 201, 361
    d.rectangle([MARGIN, y0, PAGE_W - MARGIN, y1], fill=NAVY)
    tx = MARGIN + 16
    text_wid = 580
    kf = face(SANS_B, 14)
    d.text((tx, y0 + 8), LEAD_KICKER, font=kf, fill=GOLD)
    size = fit_size(SERIF_B, LEAD_HEAD[0], 34, text_wid, 28)
    hf = face(SERIF_B, size)
    d.text((tx, y0 + 26), LEAD_HEAD[0], font=hf, fill=CARD)
    d.text((tx, y0 + 26 + size + 6), LEAD_HEAD[1], font=hf, fill=CARD)
    deck_top = y0 + 26 + 2 * (size + 6) + 8
    df = face(SANS, 13)
    for i, line in enumerate(wrap_text(df, LEAD_DECK, text_wid)):
        d.text((tx, deck_top + i * 17), line, font=df, fill=(232, 232, 238))
    ff = face(SANS_B, 12)
    d.text((tx, y1 - 13), LEAD_FOOT, font=ff, fill=(224, 92, 88))
    # three portraits on the right
    for i, (name, role, hair, skin, tie) in enumerate(LEADERS):
        cx = 724 + i * 96
        draw_portrait(d, cx, y0 + 10, hair, skin, tie)
        nf = face(SANS_B, 14)
        draw_centered(d, cx, y0 + 104, name, nf, CARD)
        rf = face(SANS, 11)
        draw_centered(d, cx, y0 + 120, role, rf, (170, 172, 190))


def draw_scales(d, cx, top):
    """Small balance scales: post, beam, gold knob, two hanging pans."""
    d.line([(cx, top + 6), (cx, top + 38)], fill=INK, width=3)
    d.line([(cx - 34, top + 10), (cx + 34, top + 10)], fill=INK, width=3)
    d.ellipse([cx - 4, top, cx + 4, top + 8], fill=GOLD)
    for side in (-1, 1):
        px = cx + side * 31
        d.line([(px, top + 10), (px - 11, top + 26)], fill=INK, width=2)
        d.line([(px, top + 10), (px + 11, top + 26)], fill=INK, width=2)
        d.arc([px - 12, top + 22, px + 12, top + 36], 0, 180, fill=INK,
              width=2)
        d.line([(px - 12, top + 29), (px + 12, top + 29)], fill=INK, width=2)


def draw_feature_box(d, x, y, w, h, kicker, headline, body_fn):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=FAINT, width=1)
    kf = face(SANS_B, 13)
    d.text((x + 12, y + 10), kicker, font=kf, fill=CRIMSON)
    hf = face(SERIF_B, 23)
    lines = wrap_text(hf, headline, w - 24)
    for i, line in enumerate(lines[:2]):
        d.text((x + 12, y + 32 + i * 27), line, font=hf, fill=INK)
    body_fn(d, x, y, w, h)


def draw_market_chart(d, x, y, w, h):
    base = y + 132
    d.line([(x + 14, base), (x + w - 14, base)], fill=HAIRLINE, width=1)
    slot = (w - 28) // 3
    for i, (val, label) in enumerate(MARKET_BARS):
        bx = x + 14 + i * slot
        d.rectangle([bx + 8, base - 22, bx + slot - 8, base], fill=CRIMSON)
        vf = face(SANS_B, 13)
        draw_centered(d, bx + slot // 2, base - 20, val, vf, CARD)
        lf = face(SANS_B, 11)
        draw_centered(d, bx + slot // 2, base + 5, label, lf, INK)


def draw_apec_body(d, x, y, w, h):
    bf = face(SANS, 13)
    top = y + 88
    for i, line in enumerate(wrap_text(bf, APEC_BODY, w - 24)):
        d.text((x + 12, top + i * 17), line, font=bf, fill=INK)
    box_y = y + h - 29
    d.rectangle([x + 12, box_y, x + w - 12, box_y + 18], outline=CRIMSON,
                width=2)
    sf = face(SANS_B, 14)
    draw_centered(d, x + w // 2, box_y + 1, "NO DEAL IN SHENZHEN", sf,
                  CRIMSON)


def draw_hague_body(d, x, y, w, h):
    draw_scales(d, x + w // 2, y + 88)
    bf = face(SANS, 12)
    top = y + h - 30
    for i, line in enumerate(wrap_text(bf, HAGUE_BODY, w - 24)):
        d.text((x + 12, top + i * 14), line, font=bf, fill=(70, 70, 70))


def draw_features(d):
    y0, h = 369, 165
    w = (CONTENT_W - 14) // 3
    x = MARGIN
    draw_feature_box(d, x, y0, w, h, "MARKETS IN TURMOIL",
                     "Stocks slide into correction", draw_market_chart)
    x += w + 7
    draw_feature_box(d, x, y0, w, h, "APEC \u2022 SHENZHEN",
                     "Three leaders, no breakthrough", draw_apec_body)
    x += w + 7
    draw_feature_box(d, x, y0, w, h, "THE HAGUE \u2022 JUSTICE",
                     "Myanmar guilty of genocide", draw_hague_body)


def draw_section_head(d):
    f = face(SERIF_B, 27)
    d.text((MARGIN, 546), "ALSO ON SATURDAY \u2014 36 MORE STORIES",
           font=f, fill=INK)
    d.line([(MARGIN, 580), (PAGE_W - MARGIN, 580)], fill=INK, width=2)


# ---------------------------------------------------------------- columns

def story_block(f_head, f_sub, headline, deck, width, start=15):
    """Measure one story: (headline lines, deck lines, fitted head size)."""
    size = start
    while size > 12 and text_w(face(SANS_B, size), headline) > width:
        size -= 1
    lines = wrap_text(face(SANS_B, size), headline, width)
    subs = wrap_text(f_sub, deck, width)
    return lines, subs, size


def column_total(head_size, sub_size, gap, sections, width):
    """Total pixel height of a column's sections at the given sizes."""
    total = 0
    for _, stories in sections:
        total += 22  # section heading
        for headline, deck in stories:
            lines, subs, fitted = story_block(face(SANS_B, head_size),
                                              face(SANS, sub_size),
                                              headline, deck, width,
                                              start=head_size)
            total += len(lines) * (fitted + 2) + len(subs) * (sub_size + 1)
            total += gap
    return total


def pick_column_sizes(available, width):
    """Largest headline/deck sizes whose tallest column fits `available`."""
    for head_size, sub_size in ((14, 11), (13, 11), (13, 10),
                                (12, 10)):
        worst = 0
        for lo, hi in COLUMN_LAYOUT:
            total = column_total(head_size, sub_size, 1,
                                 COLUMNS[lo:hi], width - 30)
            worst = max(worst, total)
        if worst <= available:
            return head_size, sub_size
    return 12, 10


def draw_columns(d):
    top, bottom = 588, 988
    col_w = (CONTENT_W - 32) // 3
    head_size, sub_size = pick_column_sizes(bottom - top, col_w)
    gap = 1
    num = 0
    for ci, (lo, hi) in enumerate(COLUMN_LAYOUT):
        x = MARGIN + ci * (col_w + 16)
        y = top
        for heading, stories in COLUMNS[lo:hi]:
            hf = face(SANS_B, 19)
            d.text((x, y), heading, font=hf, fill=CRIMSON)
            y += 22
            for headline, deck in stories:
                num += 1
                lines, subs, fitted = story_block(
                    face(SANS_B, head_size), face(SANS, sub_size),
                    headline, deck, col_w - 30, start=head_size)
                nf = face(SANS_B, head_size)
                d.text((x, y), "%02d" % num, font=nf, fill=INK)
                hfont = face(SANS_B, fitted)
                for i, line in enumerate(lines):
                    d.text((x + 30, y + i * (fitted + 2)), line, font=hfont,
                           fill=INK)
                y += len(lines) * (fitted + 2)
                sf = face(SANS, sub_size)
                for i, line in enumerate(subs):
                    d.text((x + 30, y + i * (sub_size + 1)), line, font=sf,
                           fill=GREY)
                y += len(subs) * (sub_size + 1) + gap


def draw_footer(d):
    f = face(SANS, 12)
    draw_centered(d, PAGE_W // 2, 998, FOOTER, f, GREY)


def build_page():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(img)
    draw_top_meta(d)
    draw_masthead(d)
    draw_date_bar(d)
    draw_ticker(d)
    draw_lead(d)
    draw_features(d)
    draw_section_head(d)
    draw_columns(d)
    draw_footer(d)
    return img


def main():
    if len(sys.argv) > 1:
        out_path = sys.argv[1]
    else:
        out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
        out_path = os.path.join(out_dir, "entry.png")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    build_page().save(out_path, format="PNG")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
