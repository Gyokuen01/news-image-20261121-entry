#!/usr/bin/env python3
"""SATURDAY 21 NOVEMBER 2026 - one day's world news in one image (v5).

Renders a 1024x1024 front page with Pillow (stdlib + PIL only).
Structure follows what the day's winning pages do, rebuilt from scratch
here: the date itself is the masthead; a UTC strip shows the day unfolding;
a colour-coded region bar counts the breadth; three large pictured stories,
ten more pictured cards, a world map with pins, a 24-story list, a DATE
CHECK box naming the stories left out because they belong to another day,
and a HOW SURE legend. Every story is dated Saturday 21 November 2026
(UTC); every story carries its sources and a status (CONFIRMED / OFFICIAL /
REPORTED / CLAIM).

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
MARGIN = 24
CONTENT_W = PAGE_W - 2 * MARGIN
RIGHT = PAGE_W - MARGIN

PAPER = (243, 238, 226)
CARD = (255, 255, 255)
INK = (26, 26, 26)
NAVY = (17, 23, 56)
CRIMSON = (168, 30, 34)
GOLD = (214, 158, 58)
GREY = (112, 109, 100)
FAINT = (152, 149, 140)
HAIRLINE = (96, 94, 86)
SKY = (205, 225, 235)
LAND = (232, 222, 196)
LAND_LINE = (150, 140, 115)
TEAL = (0, 122, 122)

# Region colours: used for the region bar, card top borders and map pins.
REGION_COLORS = {
    "EUROPE": (32, 74, 140),
    "MIDDLE EAST": (168, 30, 34),
    "AMERICAS": (34, 122, 72),
    "AFRICA": (176, 102, 28),
    "SOUTH ASIA": (112, 62, 142),
    "EAST ASIA": (0, 128, 128),
    "SE ASIA": (122, 122, 32),
    "OCEANIA": (178, 138, 20),
    "GLOBAL": (92, 92, 102),
}
REGION_SHORT = {
    "EUROPE": "EUROPE",
    "MIDDLE EAST": "MID EAST",
    "AMERICAS": "AMERICAS",
    "AFRICA": "AFRICA",
    "SOUTH ASIA": "S. ASIA",
    "EAST ASIA": "E. ASIA",
    "SE ASIA": "SE ASIA",
    "OCEANIA": "OCEANIA",
    "GLOBAL": "GLOBAL",
}
# Order for the region bar: most stories first.
REGION_ORDER = ["EUROPE", "MIDDLE EAST", "AMERICAS", "GLOBAL", "AFRICA",
                "SOUTH ASIA", "EAST ASIA", "SE ASIA", "OCEANIA"]

STATUS_COLORS = {
    "CONFIRMED": (34, 122, 72),
    "OFFICIAL": (32, 74, 140),
    "REPORTED": (176, 102, 28),
    "CLAIM": (168, 30, 34),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
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

# (num, region, kicker, status, headline, deck, sources, picture, lon, lat)
# lon/lat is None for stories with no place on Earth (space, crypto).
HERO = [
    (1, "MIDDLE EAST", "BAHRAIN \u2022 HORMUZ \u2014 CONFLICT", "CLAIM",
     "Bahrain says Iran struck it; tanker hit off Oman",
     "Site ablaze, no one hurt, Bahrain says. IRGC claims US radar hits; "
     "UKMTO: tanker struck off Khasab.",
     "BAHRAIN \u2022 UKMTO \u2022 FRANCE 24", "gulf", (54.0, 26.0)),
    (2, "GLOBAL", "ANTALYA, T\u00dcRKIYE \u2014 CLIMATE", "CONFIRMED",
     "COP31 deadlocked over fossil fuels in overtime",
     "Talks pause overnight. EU and Pacific states reject a draft that "
     "omits fossil fuels.",
     "REUTERS \u2022 AFP \u2022 AP", "cop31", (30.7, 36.9)),
    (3, "AMERICAS", "SINALOA, MEXICO \u2014 CRIME", "CONFIRMED",
     "Mexico captures cartel boss \u2018El Chapo Isidro\u2019",
     "Fausto Isidro Meza Flores seized in a Guasave raid; 4 soldiers and "
     "7 gunmen killed.",
     "AP \u2022 GUARDIAN \u2022 FBI", "mexico", (-108.5, 25.6)),
]

# (num, region, kicker, status, headline, deck, sources, picture, lon, lat)
CARDS = [
    (4, "AMERICAS", "PERU \u2014 QUAKE", "OFFICIAL",
     "Deep M6.7 quake shakes central Peru",
     "00:09 UTC, 108 km deep; felt in Lima. No deaths.",
     "USGS \u2022 AP", "quake67", (-75.2, -11.0)),
    (5, "GLOBAL", "MERCURY \u2014 SPACE", "OFFICIAL",
     "BepiColombo enters Mercury orbit",
     "37-min burn at 18:24 UTC ends 8-year voyage.",
     "ESA \u2022 JAXA", "mercury", None),
    (6, "EUROPE", "BRUSSELS \u2014 TRADE", "OFFICIAL",
     "EU and Indonesia sign trade pact",
     "Cuts 98.5% of EU tariff lines after a decade.",
     "EU \u2022 ANTARA", "eu-id", (4.4, 50.8)),
    (7, "GLOBAL", "GENEVA \u2014 AI ARMS", "CONFIRMED",
     "128 states set 2-year killer-robot path",
     "No binding ban yet; US, Russia oppose limits.",
     "AFP \u2022 REUTERS", "robot", (6.1, 46.2)),
    (8, "EUROPE", "GULF OF FINLAND", "CONFIRMED",
     "Drones set Russian cargo ship ablaze",
     "Sparta II hit 06:50 UTC; 16 crew rescued.",
     "REUTERS \u2022 BBC", "ship", (25.0, 59.8)),
    (9, "OCEANIA", "BANDA SEA", "OFFICIAL",
     "Deep M6.8 quake felt in Darwin",
     "09:42 UTC, 100 km deep; no tsunami, no injuries.",
     "USGS \u2022 ABC AUSTRALIA", "quake68", (129.0, -6.5)),
    (10, "GLOBAL", "CRYPTO", "CONFIRMED",
     "Bitcoin dives to $55,100, then rebounds",
     "Lowest since Sep 2024; 8% recovery near $60,190.",
     "COINGECKO \u2022 REUTERS", "bitcoin", None),
    (11, "EUROPE", "FRANCE \u2014 PROTEST", "OFFICIAL",
     "Sixth Saturday of cost-of-living marches",
     "Ministry counts 82,500; organisers say 150,000.",
     "AFP \u2022 FRANCE 24 \u2022 LE MONDE", "crowd", (2.35, 48.85)),
    (12, "EUROPE", "TWICKENHAM", "CONFIRMED",
     "England beat All Blacks by record margin",
     "37\u201312, biggest win over New Zealand.",
     "BBC \u2022 REUTERS \u2022 STUFF", "rugby", (-0.3, 51.5)),
    (13, "EAST ASIA", "OSAKA \u2014 MUSIC", "CONFIRMED",
     "BTS take five MAMA awards, two grand prizes",
     "Album of the Year for \u2018Arirang\u2019; Cortis win Song.",
     "YONHAP \u2022 FINANCIAL EXPRESS", "trophy", (135.5, 34.7)),
]

# (num, region, headline, sources) - one line each.
ALSO = [
    (14, "EUROPE", "Paris: 144 held at cost marches", "FRENCH POLICE"),
    (15, "EUROPE", "Kyiv: UK deal to build drones", "BBC"),
    (16, "EUROPE", "Dublin: Ireland beat South Africa 20\u201317", "SKY \u2022 GUARDIAN"),
    (17, "EUROPE", "Turin: Alcaraz beats Shelton, faces Zverev", "BBC \u2022 ATP"),
    (18, "MIDDLE EAST", "Jerusalem: Eisenkot invites Likud to talks", "TOI"),
    (19, "MIDDLE EAST", "Gaza City: strike on food vehicle kills 3", "REUTERS \u2022 AJ"),
    (20, "MIDDLE EAST", "Riyadh: coalition says it downed 3 missiles", "AJ \u2022 REUTERS"),
    (21, "MIDDLE EAST", "Beirut: Aoun demands Israeli pull-out", "AJ \u2022 TOI"),
    (22, "AMERICAS", "Bras\u00edlia: Bolsonaro moved to intensive care", "REUTERS \u2022 AP"),
    (23, "AMERICAS", "Washington: FBI probes crime-database breach", "BBC \u2022 CBC"),
    (24, "AMERICAS", "Washington: Trump backs 10% card-cap bill", "PBS"),
    (25, "SE ASIA", "Serang, Java: factory fire, 3 dead, 36 missing", "BBC \u2022 GUARDIAN"),
    (26, "SE ASIA", "Hanoi: law to speed land expropriation", "REUTERS"),
    (27, "SE ASIA", "Bangkok: 6-point plan on arsenic in 3 rivers", "THAI GOVT"),
    (28, "SOUTH ASIA", "Savar: 80 garment factories shut in protests", "TBS \u2022 D. STAR"),
    (29, "SOUTH ASIA", "Mastung: Pakistan forces kill 15 militants", "DAWN \u2022 TRIBUNE"),
    (30, "SOUTH ASIA", "Manipur: tainted alcohol kills 11, 600 in care", "REUTERS \u2022 SCMP"),
    (31, "EAST ASIA", "Beijing: Singapore\u2019s Wong meets Li Qiang", "ST \u2022 BT"),
    (32, "EAST ASIA", "Qinghai: M5.9 quake in remote west China", "USGS"),
    (33, "AFRICA", "Bayelsa: Nigeria funeral boat toll reaches 24", "DW \u2022 AP \u2022 SKY"),
    (34, "AFRICA", "Abuja: CAF makes Kiswahi 5th official language", "CAF \u2022 NATION"),
    (35, "AFRICA", "Niger State: gunmen kill village head in raid", "PUNCH"),
    (36, "OCEANIA", "Australia: hosts beat England by 3 wickets", "BBC \u2022 AP"),
    (37, "OCEANIA", "Wellington: India 486-4, lead NZ by 118", "AFP \u2022 REUTERS"),
]

# (utc minutes, label) for the day strip.
UTC_EVENTS = [
    (9, "00:09 Peru quake"),
    (120, "02:00 Sinaloa raid"),
    (300, "05:00 Tanker hit"),
    (582, "09:42 Banda Sea"),
    (732, "12:12 EU\u2013Indonesia"),
    (1104, "18:24 Mercury burn"),
    (1320, "22:00 COP31 pause"),
]

TICKER_LINE = (
    "Iran strikes Bahrain as tankers hit in Hormuz  \u25c6  "
    "Mexico captures \u2018El Chapo Isidro\u2019  \u25c6  "
    "COP31 deadlocked over fossil fuels in overtime"
)

DATE_CHECK = (
    "DATE CHECK \u2014 Left out on purpose: they belong to another day.  "
    "Fri 20 Nov: Wall Street tech sell-off \u2022 Russian missiles land in Poland "
    "\u2022 Kryvyi Rih double-tap \u2022 Denmark expels Russian attach\u00e9.  "
    "Thu 19 Nov: ICJ Myanmar ruling \u2022 APEC summit in Shenzhen.  "
    "Not yet: COP31 closing session (Sun 22 Nov)."
)

FOOTER = (
    "Every story here happened or was first reported on Saturday 21 November 2026 "
    "(UTC), told as the named outlets reported it. All maps and drawings are "
    "original vector work."
)

HOW_SURE = (
    "HOW SURE:  CONFIRMED 2+ outlets   \u2022   OFFICIAL on the record   "
    "\u2022   REPORTED one outlet   \u2022   CLAIM one side says"
)


def region_counts():
    """Count stories per region across hero + cards + also-list."""
    counts = {r: 0 for r in REGION_ORDER}
    for s in HERO + CARDS + ALSO:
        counts[s[1]] += 1
    return counts


# ---------------------------------------------------------------- world map
# Coarse continent outlines in (lon, lat). Stylised, not survey-grade.

NORTH_AMERICA = [
    (-168, 65), (-150, 70), (-125, 71), (-105, 70), (-90, 69), (-80, 72),
    (-70, 68), (-64, 61), (-56, 53), (-60, 46), (-65, 43), (-70, 41),
    (-75, 37), (-80, 31), (-81, 25), (-85, 30), (-90, 29), (-95, 29),
    (-97, 25), (-101, 22), (-105, 20), (-100, 16), (-94, 16), (-90, 13),
    (-85, 11), (-81, 8), (-78, 8), (-82, 11), (-87, 13), (-90, 14),
    (-94, 16), (-97, 17), (-101, 18), (-105, 20), (-108, 24), (-111, 28),
    (-114, 31), (-118, 34), (-122, 38), (-124, 44), (-124, 48), (-128, 51),
    (-132, 55), (-137, 58), (-143, 60), (-149, 61), (-155, 58), (-161, 59),
    (-166, 61), (-168, 65),
]
GREENLAND = [
    (-55, 60), (-42, 60), (-38, 65), (-32, 68), (-25, 70), (-20, 70),
    (-28, 74), (-40, 76), (-52, 75), (-58, 70), (-57, 64), (-55, 60),
]
SOUTH_AMERICA = [
    (-80, 9), (-72, 12), (-64, 11), (-60, 8), (-54, 6), (-50, 4),
    (-48, 0), (-44, -4), (-38, -6), (-36, -10), (-39, -16), (-41, -22),
    (-48, -26), (-52, -32), (-57, -38), (-63, -41), (-66, -46), (-68, -51),
    (-71, -54), (-74, -50), (-74, -42), (-72, -34), (-71, -28), (-70, -20),
    (-75, -15), (-79, -9), (-81, -4), (-80, 2), (-80, 9),
]
AFRICA = [
    (-17, 15), (-15, 21), (-10, 28), (-5, 35), (0, 36), (10, 37),
    (15, 32), (22, 33), (28, 31), (33, 30), (36, 27), (39, 21),
    (42, 16), (44, 12), (48, 11), (51, 11), (49, 6), (43, 0),
    (40, -5), (37, -10), (34, -14), (32, -19), (30, -24), (27, -30),
    (23, -34), (19, -35), (16, -30), (14, -24), (12, -18), (13, -12),
    (11, -6), (9, -1), (9, 4), (4, 6), (-2, 5), (-8, 5), (-13, 8),
    (-16, 12), (-17, 15),
]
EURASIA = [
    (-10, 36), (-9, 42), (-2, 44), (-2, 48), (-5, 50), (0, 51),
    (4, 53), (8, 56), (10, 58), (6, 60), (10, 63), (18, 69),
    (25, 71), (30, 70), (40, 68), (50, 69), (60, 69), (70, 70),
    (80, 73), (90, 75), (100, 77), (110, 76), (120, 73), (130, 72),
    (140, 72), (150, 70), (160, 69), (170, 67), (178, 65), (170, 66),
    (162, 62), (158, 59), (150, 60), (142, 58), (138, 55), (132, 52),
    (128, 50), (124, 48), (121, 44), (118, 40), (113, 38), (108, 34),
    (104, 36), (100, 38), (95, 40), (90, 42), (85, 44), (80, 45),
    (75, 48), (70, 50), (66, 52), (62, 55), (58, 55), (54, 56),
    (50, 55), (46, 56), (42, 58), (38, 60), (34, 62), (30, 62),
    (26, 62), (22, 60), (18, 58), (14, 56), (10, 55), (8, 54),
    (5, 53), (0, 51), (-4, 50), (-8, 47), (-10, 43), (-10, 37),
    (-10, 36),
]
BRITAIN = [
    (-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
    (-1, 51), (-3, 50), (-5, 50),
]
JAPAN = [
    (130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
    (141, 40), (142, 42), (144, 44), (142, 45), (140, 43), (138, 40),
    (136, 37), (134, 35), (132, 33), (130, 31),
]
SUMATRA = [(95, 5), (100, 0), (105, -5), (106, -6), (104, -3), (100, 0), (95, 5)]
JAVA = [(105, -6), (110, -7), (114, -7), (114, -8), (108, -8), (105, -7)]
BORNEO = [(109, 1), (113, 3), (117, 4), (119, 1), (117, -2), (113, -3), (110, 0), (109, 1)]
NEW_GUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (147, -8), (142, -8), (137, -6), (132, -3), (131, -1)]
AUSTRALIA = [
    (113, -22), (114, -30), (115, -34), (118, -35), (124, -33), (129, -32),
    (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
    (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
    (140, -12), (136, -12), (135, -15), (132, -12), (130, -13), (126, -14),
    (122, -17), (118, -20), (114, -21), (113, -22),
]
NEW_ZEALAND = [
    (167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
    (175, -41), (173, -42), (170, -44), (167, -46), (167, -45),
]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (49, -20), (45, -25), (43, -22), (44, -16)]

WORLD_LAND = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
              BRITAIN, JAPAN, SUMATRA, JAVA, BORNEO, NEW_GUINEA, AUSTRALIA,
              NEW_ZEALAND, MADAGASCAR]

# ---------------------------------------------------------------- sections

def draw_top_meta(d):
    f = face(SANS_B, 11)
    d.text((MARGIN, 8), "THE WORLD TODAY", font=f, fill=INK)
    draw_centered(d, PAGE_W // 2, 8, "DAY 325 OF 2026", f, CRIMSON)
    d.text((RIGHT, 8), "ALL TIMES UTC \u2022 RANKED BY CONSEQUENCE",
           font=f, fill=GREY, anchor="ra")
    d.line([(MARGIN, 24), (RIGHT, 24)], fill=INK, width=1)


def draw_masthead(d):
    size = fit_size(SERIF_B, "Saturday 21 November 2026", 68, CONTENT_W, 48)
    f = face(SERIF_B, size)
    draw_centered(d, PAGE_W // 2, 28, "Saturday 21 November 2026", f, INK)
    d.line([(MARGIN, 96), (RIGHT, 96)], fill=INK, width=2)


def draw_subbar(d):
    counts = region_counts()
    total = sum(counts.values())
    nreg = sum(1 for v in counts.values() if v)
    s = ("%d STORIES \u2022 %d REGIONS \u2022 EVERY ONE DATED "
         "SATURDAY 21 NOVEMBER 2026" % (total, nreg))
    f = face(SANS_B, 15)
    draw_centered(d, PAGE_W // 2, 101, s, f, CRIMSON)
    d.line([(MARGIN, 118), (RIGHT, 118)], fill=INK, width=1)


def draw_ticker(d):
    size = fit_size(SERIF, TICKER_LINE, 15, CONTENT_W, 11)
    f = face(SERIF, size)
    draw_centered(d, PAGE_W // 2, 122, TICKER_LINE, f, INK)
    d.line([(MARGIN, 140), (RIGHT, 140)], fill=INK, width=1)


def draw_utc_strip(d):
    y0, y1 = 144, 180
    # label box
    d.rectangle([MARGIN, y0, MARGIN + 92, y1], fill=NAVY)
    lf = face(SANS_B, 11)
    draw_centered(d, MARGIN + 46, y0 + 5, "THE DAY", lf, CARD)
    draw_centered(d, MARGIN + 46, y0 + 19, "IN UTC", lf, GOLD)
    x0 = MARGIN + 100
    x1 = RIGHT
    mid = (y0 + y1) // 2 + 2
    d.line([(x0, mid), (x1, mid)], fill=HAIRLINE, width=2)
    # hour ticks (no numbers: the event times already carry the clock)
    for hh in range(0, 25, 4):
        tx = x0 + (hh / 24.0) * (x1 - x0)
        d.line([(tx, mid - 3), (tx, mid + 3)], fill=INK, width=1)
    # events, labels alternating above / below the line
    ef = face(SANS_B, 9)
    for i, (mins, label) in enumerate(UTC_EVENTS):
        ex = x0 + (mins / 1440.0) * (x1 - x0)
        d.ellipse([ex - 4, mid - 4, ex + 4, mid + 4], fill=CRIMSON,
                  outline=CARD, width=1)
        text = label
        tw = text_w(ef, text)
        lx = min(max(ex - tw / 2, x0), x1 - tw)
        if i % 2 == 0:
            d.text((lx, y0 + 2), text, font=ef, fill=INK)
        else:
            d.text((lx, mid + 5), text, font=ef, fill=INK)


def draw_region_bar(d):
    y0, y1 = 184, 200
    counts = region_counts()
    total = sum(counts.values())
    x = MARGIN
    f = face(SANS_B, 10)
    for r in REGION_ORDER:
        n = counts[r]
        if not n:
            continue
        w = int(round(CONTENT_W * n / float(total)))
        d.rectangle([x, y0, x + w, y1], fill=REGION_COLORS[r])
        label = "%s %d" % (REGION_SHORT[r], n)
        draw_centered(d, x + w // 2, y0 + 3, label, f, CARD)
        x += w


# ---------------------------------------------------------------- pictures

def _pic_frame(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)


def draw_gulf_map(d, x, y, w, h):
    """Strait of Hormuz: Iran above, Arabia below, tankers in the Gulf."""
    _pic_frame(d, x, y, w, h)
    # local projection: lon 47..60 -> x, lat 23..31 -> y
    def px(lon, lat):
        return (x + (lon - 47.0) / 13.0 * w,
                y + (31.0 - lat) / 8.0 * h)
    # Iran (north land)
    iran = [(47, 31), (60, 31), (60, 28.6), (58.5, 27.8), (57, 27.2),
            (55.5, 27.4), (54, 27.8), (52.5, 28.2), (51, 28.6), (49.5, 29.0),
            (48, 29.6), (47, 30.2)]
    d.polygon([px(lo, la) for lo, la in iran], fill=LAND, outline=LAND_LINE)
    # Arabia (south land) with Qatar bump
    arabia = [(47, 23), (60, 23), (60, 25.2), (58.5, 25.6), (57.5, 25.9),
              (56.5, 26.2), (55.5, 26.0), (54.5, 25.4), (53.5, 25.2),
              (52.5, 25.0), (51.5, 25.2), (51.8, 26.2), (51.2, 26.0),
              (50.5, 25.6), (49.5, 25.4), (48.5, 25.0), (47, 24.6)]
    d.polygon([px(lo, la) for lo, la in arabia], fill=LAND, outline=LAND_LINE)
    # Bahrain island
    bx, by = px(50.6, 26.2)
    d.ellipse([bx - 4, by - 3, bx + 4, by + 3], fill=LAND,
              outline=LAND_LINE)
    # fire star at Bahrain industrial site
    sx, sy = px(50.9, 26.0)
    d.ellipse([sx - 6, sy - 6, sx + 6, sy + 6], fill=CRIMSON)
    d.text((sx, sy - 5), "*", font=face(SANS_B, 14), fill=CARD, anchor="mm")
    # dashed tanker route: Gulf -> Hormuz -> Arabian Sea
    route = [(48.5, 28.3), (51, 27.6), (53.5, 27.0), (55.5, 26.6),
             (56.8, 26.2), (58.5, 25.4), (59.5, 24.8)]
    pts = [px(lo, la) for lo, la in route]
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx2, by2 = pts[i + 1]
        steps = 8
        for s in range(0, steps, 2):
            t0 = s / float(steps)
            t1 = (s + 1) / float(steps)
            d.line([(ax + (bx2 - ax) * t0, ay + (by2 - ay) * t0),
                    (ax + (bx2 - ax) * t1, ay + (by2 - ay) * t1)],
                   fill=CRIMSON, width=2)
    # two tanker icons on the route
    for lon, lat in ((52.0, 27.3), (57.6, 25.9)):
        tx, ty = px(lon, lat)
        d.rectangle([tx - 9, ty - 3, tx + 9, ty + 3], fill=INK)
        d.rectangle([tx + 2, ty - 7, tx + 6, ty - 3], fill=INK)
    # labels
    lf = face(SANS_B, 11)
    sf = face(SANS, 9)
    d.text(px(53.5, 30.2), "IRAN", font=lf, fill=INK, anchor="ma")
    d.text(px(50.6, 24.9), "BAHRAIN", font=face(SANS_B, 9), fill=CRIMSON,
           anchor="ma")
    d.text(px(56.8, 24.6), "STRAIT OF HORMUZ", font=sf, fill=INK,
           anchor="ma")
    d.text(px(49.0, 24.2), "SAUDI ARABIA", font=sf, fill=GREY, anchor="ma")
    d.text(px(54.6, 24.2), "QATAR", font=sf, fill=GREY, anchor="ma")
    d.text(px(58.8, 24.0), "OMAN", font=sf, fill=GREY, anchor="ma")


def draw_cop31(d, x, y, w, h):
    """COP31: teal summit block, draft text, overtime clock."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 240, 238))
    # teal block
    bw = 132
    d.rectangle([x, y, x + bw, y + h], fill=TEAL)
    tf = face(SANS_B, 26)
    d.text((x + 10, y + 10), "COP31", font=tf, fill=CARD)
    sf = face(SANS_B, 9)
    d.text((x + 10, y + 42), "ANTALYA", font=sf, fill=CARD)
    d.text((x + 10, y + 54), "UN CLIMATE", font=sf, fill=CARD)
    d.text((x + 10, y + 66), "SUMMIT", font=sf, fill=CARD)
    # delegate dots
    for i in range(7):
        cx = x + 16 + i * 16
        d.ellipse([cx - 5, y + 96, cx + 5, y + 106], fill=CARD)
        d.rectangle([cx - 7, y + 107, cx + 7, y + 118], fill=CARD)
    d.text((x + 10, y + 122), "200 NATIONS", font=sf, fill=CARD)
    # draft text box
    bx = x + bw + 10
    bw2 = w - bw - 20
    d.rectangle([bx, y + 10, bx + bw2, y + 62], fill=CARD,
                outline=FAINT, width=1)
    kf = face(SANS_B, 9)
    d.text((bx + 8, y + 14), "DRAFT TEXT", font=kf, fill=GREY)
    df = face(SANS_B, 15)
    d.text((bx + 8, y + 28), "fossil fuels", font=df, fill=CRIMSON)
    d.line([(bx + 8, y + 46), (bx + 8 + text_w(df, "fossil fuels"), y + 46)],
           fill=CRIMSON, width=2)
    d.text((bx + 8, y + 50), "no mention in the draft", font=face(SANS, 10),
           fill=GREY)
    # clock + overtime
    cx, cy = bx + 34, y + 100
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=CARD,
              outline=INK, width=2)
    d.line([(cx, cy), (cx, cy - 16)], fill=INK, width=2)
    d.line([(cx, cy), (cx + 12, cy + 6)], fill=INK, width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=INK)
    of = face(SANS_B, 16)
    d.text((bx + 68, y + 78), "OVERTIME", font=of, fill=CRIMSON)
    d.text((bx + 68, y + 100), "a day past Friday's", font=face(SANS, 10),
           fill=GREY)
    d.text((bx + 68, y + 113), "deadline", font=face(SANS, 10), fill=GREY)


def draw_mexico_map(d, x, y, w, h):
    """Sinaloa: Mexico with the Gulf of California, capture marker."""
    _pic_frame(d, x, y, w, h)
    # local projection: lon -117..-86 -> x, lat 14..33 -> y
    def px(lon, lat):
        return (x + (lon + 117.0) / 31.0 * w,
                y + (33.0 - lat) / 19.0 * h)
    # Baja peninsula
    baja = [(-117, 33), (-115, 31), (-113, 29), (-111, 27), (-110, 25),
            (-111, 23), (-112, 25), (-114, 28), (-116, 31), (-117, 33)]
    d.polygon([px(lo, la) for lo, la in baja], fill=LAND, outline=LAND_LINE)
    # mainland Mexico
    mex = [(-110, 31), (-105, 29), (-100, 27), (-97, 26), (-94, 22),
           (-92, 19), (-90, 18), (-87, 16), (-86, 14), (-88, 14),
           (-90, 15), (-92, 15), (-94, 16), (-96, 16), (-97, 19),
           (-100, 20), (-103, 19), (-105, 20), (-107, 23), (-109, 25),
           (-111, 28), (-112, 30), (-110, 31)]
    d.polygon([px(lo, la) for lo, la in mex], fill=LAND, outline=LAND_LINE)
    # capture marker at Guasave
    gx, gy = px(-108.5, 25.6)
    d.ellipse([gx - 8, gy - 8, gx + 8, gy + 8], fill=CRIMSON,
              outline=CARD, width=2)
    d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=CARD)
    # CAPTURED stamp
    sf = face(SANS_B, 13)
    label = "CAPTURED"
    tw = text_w(sf, label)
    sx = x + w - tw - 18
    sy = y + 12
    d.rectangle([sx - 6, sy - 4, sx + tw + 6, sy + 18], fill=CRIMSON)
    d.text((sx, sy), label, font=sf, fill=CARD)
    # labels
    d.text(px(-101, 28.5), "MEXICO", font=face(SANS_B, 11), fill=INK,
           anchor="ma")
    d.text(px(-108.5, 22.6), "GUASAVE", font=face(SANS_B, 9), fill=CRIMSON,
           anchor="ma")
    d.text(px(-113.5, 29.5), "GULF OF", font=face(SANS, 8), fill=GREY,
           anchor="ma")
    d.text(px(-113.5, 28.2), "CALIFORNIA", font=face(SANS, 8), fill=GREY,
           anchor="ma")
    d.text((x + 10, y + h - 18), "11 DEAD IN CLASHES", font=face(SANS_B, 10),
           fill=CRIMSON)


def draw_quake_pic(d, x, y, w, h, mag, depth):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    # seismograph zigzag
    pts = []
    n = 24
    for i in range(n + 1):
        px = x + 8 + (w - 16) * i / float(n)
        amp = ((i * 7) % 13 - 6) / 6.0
        py = y + h // 2 + amp * (h // 2 - 8)
        pts.append((px, py))
    d.line(pts, fill=CRIMSON, width=2)
    d.line([(x + 8, y + h // 2), (x + w - 8, y + h // 2)], fill=HAIRLINE,
           width=1)
    mf = face(SANS_B, 20)
    d.text((x + 8, y + 4), mag, font=mf, fill=INK)
    d.text((x + 8, y + h - 16), depth, font=face(SANS_B, 9), fill=GREY)


def draw_mercury_pic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 20, 44))
    cx, cy = x + 44, y + h // 2
    d.ellipse([x + 14, y + 8, x + w - 14, y + h - 8], outline=(90, 95, 130),
              width=1)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(168, 164, 150))
    d.ellipse([cx - 8, cy - 10, cx - 2, cy - 4], fill=(120, 116, 104))
    d.ellipse([cx + 4, cy + 4, cx + 10, cy + 10], fill=(120, 116, 104))
    # spacecraft on the orbit
    sx, sy = x + w - 34, y + 14
    d.rectangle([sx - 4, sy - 3, sx + 4, sy + 3], fill=GOLD)
    d.line([(sx - 10, sy), (sx - 4, sy)], fill=GOLD, width=2)
    d.line([(sx + 4, sy), (sx + 10, sy)], fill=GOLD, width=2)
    d.text((x + w - 8, y + h - 16), "18:24 UTC", font=face(SANS_B, 9),
           fill=CARD, anchor="ra")


def draw_eu_id_pic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD)
    # EU flag
    d.rectangle([x + 8, y + 8, x + w // 2 - 4, y + h - 8],
                fill=(0, 51, 153))
    cx = x + w // 4
    cy = y + h // 2
    for i in range(12):
        import math
        a = math.pi * 2 * i / 12.0 - math.pi / 2
        sx = cx + 13 * math.cos(a)
        sy = cy + 13 * math.sin(a)
        d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=GOLD)
    # Indonesia flag
    fx0 = x + w // 2 + 4
    d.rectangle([fx0, y + 8, x + w - 8, y + h // 2], fill=(206, 17, 38))
    d.rectangle([fx0, y + h // 2, x + w - 8, y + h - 8], fill=CARD,
                outline=FAINT, width=1)
    d.text((x + w // 2, y + h - 15), "SIGNED", font=face(SANS_B, 9),
           fill=(34, 122, 72), anchor="ma")


def draw_robot_pic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 232, 236))
    cx, cy = x + 34, y + h // 2 + 2
    d.line([(cx, y + 6), (cx, y + 14)], fill=INK, width=2)
    d.ellipse([cx - 3, y + 2, cx + 3, y + 8], fill=CRIMSON)
    d.rounded_rectangle([cx - 18, y + 14, cx + 18, y + h - 10], radius=8,
                        fill=(70, 74, 90))
    d.ellipse([cx - 10, y + 24, cx - 4, y + 30], fill=CARD)
    d.ellipse([cx + 4, y + 24, cx + 10, y + 30], fill=CARD)
    d.line([(cx - 8, y + h - 18), (cx + 8, y + h - 18)], fill=CARD, width=2)
    d.text((x + 62, y + 6), "128", font=face(SANS_B, 22), fill=INK)
    d.text((x + 62, y + 30), "STATES", font=face(SANS_B, 10), fill=GREY)


def draw_ship_pic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 38, 56))
    # sea
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(14, 26, 40))
    # hull + containers
    d.polygon([(x + 20, y + h - 22), (x + w - 20, y + h - 22),
               (x + w - 34, y + h - 12), (x + 34, y + h - 12)],
              fill=(20, 20, 24))
    for i in range(4):
        cx = x + 44 + i * 30
        d.rectangle([cx, y + h - 34, cx + 24, y + h - 22],
                    fill=(150, 60, 50) if i % 2 else (90, 110, 140))
    # flames
    for fx, fh in ((x + 60, 14), (x + 96, 20), (x + 132, 12)):
        d.polygon([(fx - 8, y + h - 34), (fx, y + h - 34 - fh),
                   (fx + 8, y + h - 34)], fill=(230, 120, 30))
    # smoke
    for sx, sy, r in ((x + 70, y + 12, 7), (x + 92, y + 8, 9),
                      (x + 116, y + 12, 6)):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(120, 120, 125))
    d.text((x + 8, y + 4), "16 CREW SAFE", font=face(SANS_B, 9), fill=CARD)


def draw_bitcoin_pic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 20, 44))
    pts = [(x + 10, y + 14), (x + 40, y + 22), (x + 70, y + 18),
           (x + 100, y + h - 14), (x + 130, y + h - 22),
           (x + 160, y + 26), (x + w - 10, y + 12)]
    d.line(pts, fill=GOLD, width=3)
    d.text((x + 8, y + 4), "$55,100", font=face(SANS_B, 15), fill=GOLD)
    d.text((x + w - 8, y + h - 16), "+8% REBOUND",
           font=face(SANS_B, 9), fill=(80, 200, 120), anchor="ra")


def draw_crowd_pic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    for i in range(6):
        cx = x + 20 + i * 28
        d.ellipse([cx - 8, y + 10, cx + 8, y + 26], fill=INK)
        d.polygon([(cx - 12, y + h - 8), (cx - 10, y + 28),
                   (cx + 10, y + 28), (cx + 12, y + h - 8)], fill=INK)
    d.text((x + w - 8, y + 4), "82,500", font=face(SANS_B, 16), fill=INK,
           anchor="ra")
    d.text((x + w - 8, y + 24), "MARCHERS", font=face(SANS_B, 9),
           fill=GREY, anchor="ra")


def draw_rugby_pic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(34, 110, 60))
    d.line([(x, y + h // 2), (x + w, y + h // 2)], fill=CARD, width=2)
    d.ellipse([x + 18, y + 12, x + 66, y + h - 12], fill=(120, 72, 40),
              outline=CARD, width=2)
    d.line([(x + 38, y + 12), (x + 46, y + h - 12)], fill=CARD, width=2)
    d.text((x + w - 10, y + 8), "37\u201312", font=face(SANS_B, 20),
           fill=CARD, anchor="ra")
    d.text((x + w - 10, y + 32), "RECORD", font=face(SANS_B, 10),
           fill=CARD, anchor="ra")


def draw_trophy_pic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(48, 32, 72))
    cx, cy = x + 40, y + h // 2
    d.polygon([(cx - 16, y + 8), (cx + 16, y + 8), (cx + 12, y + 26),
               (cx - 12, y + 26)], fill=GOLD)
    d.ellipse([cx - 20, y + 6, cx - 12, y + 18], outline=GOLD, width=3)
    d.ellipse([cx + 12, y + 6, cx + 20, y + 18], outline=GOLD, width=3)
    d.rectangle([cx - 3, y + 26, cx + 3, y + h - 14], fill=GOLD)
    d.rectangle([cx - 12, y + h - 14, cx + 12, y + h - 8], fill=GOLD)
    d.text((x + 66, y + 8), "5", font=face(SANS_B, 24), fill=GOLD)
    d.text((x + 66, y + 34), "AWARDS", font=face(SANS_B, 10), fill=CARD)


PICTURES = {
    "gulf": draw_gulf_map,
    "cop31": draw_cop31,
    "mexico": draw_mexico_map,
}


def draw_small_picture(d, kind, x, y, w, h):
    if kind == "quake67":
        draw_quake_pic(d, x, y, w, h, "M6.7", "108 KM DEEP")
    elif kind == "quake68":
        draw_quake_pic(d, x, y, w, h, "M6.8", "100 KM DEEP")
    elif kind == "mercury":
        draw_mercury_pic(d, x, y, w, h)
    elif kind == "eu-id":
        draw_eu_id_pic(d, x, y, w, h)
    elif kind == "robot":
        draw_robot_pic(d, x, y, w, h)
    elif kind == "ship":
        draw_ship_pic(d, x, y, w, h)
    elif kind == "bitcoin":
        draw_bitcoin_pic(d, x, y, w, h)
    elif kind == "crowd":
        draw_crowd_pic(d, x, y, w, h)
    elif kind == "rugby":
        draw_rugby_pic(d, x, y, w, h)
    elif kind == "trophy":
        draw_trophy_pic(d, x, y, w, h)


# ---------------------------------------------------------------- cards

def draw_status_badge(d, x_right, y, status, size=9):
    """Small filled badge, right-aligned to x_right. Returns its width."""
    f = face(SANS_B, size)
    tw = text_w(f, status)
    bw = tw + 12
    d.rectangle([x_right - bw, y, x_right, y + 14],
                fill=STATUS_COLORS[status])
    d.text((x_right - bw + 6, y + 2), status, font=f, fill=CARD)
    return bw


def draw_hero_card(d, story, x, y, w, h):
    num, region, kicker, status, headline, deck, sources, pic, _ll = story
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=FAINT, width=1)
    d.rectangle([x, y, x + w, y + 4], fill=REGION_COLORS[region])
    # picture
    PICTURES[pic](d, x + 1, y + 5, w - 2, 138)
    # kicker + status
    kf = face(SANS_B, 11)
    d.text((x + 10, y + 149), kicker, font=kf, fill=REGION_COLORS[region])
    draw_status_badge(d, x + w - 10, y + 148, status)
    # headline, two lines
    hf = face(SERIF_B, 21)
    lines = wrap_text(hf, headline, w - 20)[:2]
    for i, line in enumerate(lines):
        d.text((x + 10, y + 166 + i * 24), line, font=hf, fill=INK)
    # deck, two lines
    df = face(SANS, 11)
    for i, line in enumerate(wrap_text(df, deck, w - 20)[:2]):
        d.text((x + 10, y + 216 + i * 14), line, font=df, fill=(60, 60, 60))
    # sources
    d.text((x + 10, y + h - 12), sources, font=face(SANS, 9), fill=GREY)


def draw_small_card(d, story, x, y, w, h):
    num, region, kicker, status, headline, deck, sources, pic, _ll = story
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=FAINT, width=1)
    d.rectangle([x, y, x + w, y + 3], fill=REGION_COLORS[region])
    # picture
    draw_small_picture(d, pic, x + 1, y + 4, w - 2, 55)
    # kicker (truncated at a word boundary to fit) + status badge
    kf = face(SANS_B, 9)
    bf = face(SANS_B, 8)
    badge_w = text_w(bf, status) + 12
    avail_k = w - 16 - badge_w - 6
    k = kicker
    if text_w(kf, k) > avail_k:
        words = k.split()
        k = ""
        for wd in words:
            trial = (k + " " + wd).strip()
            if text_w(kf, trial) <= avail_k or not k:
                k = trial
            else:
                break
        k = k.rstrip() + "\u2026"
    d.text((x + 8, y + 62), k, font=kf, fill=REGION_COLORS[region])
    draw_status_badge(d, x + w - 8, y + 61, status, size=8)
    # headline, two lines
    hf = face(SANS_B, 13)
    lines = wrap_text(hf, headline, w - 16)[:2]
    for i, line in enumerate(lines):
        d.text((x + 8, y + 75 + i * 14), line, font=hf, fill=INK)
    # deck, two lines
    df = face(SANS, 10)
    for i, line in enumerate(wrap_text(df, deck, w - 16)[:2]):
        d.text((x + 8, y + 104 + i * 11), line, font=df, fill=(70, 70, 70))
    # sources
    d.text((x + 8, y + h - 11), sources, font=face(SANS, 8), fill=GREY)


# ---------------------------------------------------------------- bottom

def _project(mx0, my0, mw, mh, lon, lat):
    """Equirectangular lon/lat -> map pixels (lat clipped to -60..85)."""
    lat = max(-60.0, min(85.0, lat))
    return (mx0 + (lon + 180.0) / 360.0 * mw,
            my0 + (85.0 - lat) / 145.0 * mh)


# Pins for the pictured stories that have a place on Earth. European pins
# are nudged apart so the cluster stays readable at this size.
PIN_OFFSET = {2: (5, 3), 6: (-5, -4), 7: (4, 4), 8: (0, -5), 11: (-7, 4),
              12: (-3, -7)}


def draw_world_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    for poly in WORLD_LAND:
        pts = [_project(x, y, w, h, lo, la) for lo, la in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    # pins for the pictured stories that have a place on Earth
    for story in HERO + CARDS:
        num, region = story[0], story[1]
        ll = story[8]
        if ll is None:
            continue
        px, py = _project(x, y, w, h, ll[0], ll[1])
        ox, oy = PIN_OFFSET.get(num, (0, 0))
        px, py = px + ox, py + oy
        r = 7
        d.ellipse([px - r, py - r, px + r, py + r],
                  fill=REGION_COLORS[region], outline=CARD, width=1)
        nf = face(SANS_B, 8)
        label = str(num)
        d.text((px, py), label, font=nf, fill=CARD, anchor="mm")


def draw_bottom(d):
    y0 = 757
    # ---- map box (left)
    mw = 336
    d.rectangle([MARGIN, y0, MARGIN + mw, y0 + 204], fill=CARD,
                outline=FAINT, width=1)
    tf = face(SANS_B, 12)
    d.text((MARGIN + 10, y0 + 8), "WHERE IT HAPPENED", font=tf, fill=INK)
    d.text((MARGIN + 10, y0 + 24),
           "pins match the stories \u2022 pin colour = the region",
           font=face(SANS, 9), fill=GREY)
    draw_world_map(d, MARGIN + 8, y0 + 40, mw - 16, 132)
    lf = face(SANS, 9)
    d.text((MARGIN + 10, y0 + 178), "HOW SURE:  CONFIRMED 2+ outlets",
           font=lf, fill=GREY)
    d.text((MARGIN + 10, y0 + 190),
           "OFFICIAL on record  \u2022  REPORTED 1 outlet  \u2022  "
           "CLAIM 1 side",
           font=lf, fill=GREY)
    # ---- also list (right)
    ax = MARGIN + mw + 8
    aw = RIGHT - ax
    d.text((ax, y0 + 8), "ALSO ON SATURDAY 21 NOVEMBER 2026 \u2014 24 MORE",
           font=tf, fill=INK)
    d.text((ax, y0 + 24), "in order of consequence \u2022 sources at the end",
           font=face(SANS, 9), fill=GREY)
    col_w = (aw - 8) // 2
    hf = face(SANS_B, 11)
    sf = face(SANS, 8)
    for i, (num, region, headline, sources) in enumerate(ALSO):
        col = 0 if i < 12 else 1
        row = i % 12
        cx = ax + col * (col_w + 8)
        cy = y0 + 42 + row * 15
        # number pin
        r = 6
        px = cx + r
        py = cy + 6
        d.ellipse([px - r, py - r, px + r, py + r],
                  fill=REGION_COLORS[region])
        d.text((px, py), str(num), font=face(SANS_B, 8), fill=CARD,
               anchor="mm")
        # headline + source on one line, truncated to fit
        tx = cx + 16
        avail = col_w - 16
        full = headline + "  \u2022  " + sources
        if text_w(hf, full) <= avail:
            d.text((tx, cy), headline, font=hf, fill=INK)
            d.text((tx + text_w(hf, headline + "  \u2022  "), cy), sources,
                   font=sf, fill=GREY)
        else:
            # shrink the headline until headline + source fits
            words = headline.split()
            head = headline
            while words and text_w(hf, head + " \u2026  \u2022  " + sources) > avail:
                words = words[:-1]
                head = " ".join(words)
            shown = (head + " \u2026") if words else headline
            d.text((tx, cy), shown, font=hf, fill=INK)
            d.text((tx + text_w(hf, shown + "  \u2022  "), cy), sources,
                   font=sf, fill=GREY)


def draw_date_check(d):
    y0, y1 = 965, 995
    d.rectangle([MARGIN, y0, RIGHT, y1], fill=(255, 250, 235),
                outline=FAINT, width=1)
    d.rectangle([MARGIN, y0, MARGIN + 4, y1], fill=CRIMSON)
    f = face(SANS, 11)
    lines = wrap_text(f, DATE_CHECK, CONTENT_W - 24)
    for i, line in enumerate(lines[:2]):
        d.text((MARGIN + 12, y0 + 4 + i * 14), line, font=f, fill=INK)


def draw_footer(d):
    f = face(SANS, 10)
    draw_centered(d, PAGE_W // 2, 999, FOOTER, f, GREY)


# ---------------------------------------------------------------- build

def build_page():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(img)
    draw_top_meta(d)
    draw_masthead(d)
    draw_subbar(d)
    draw_ticker(d)
    draw_utc_strip(d)
    draw_region_bar(d)
    # hero row: 3 cards
    hw = (CONTENT_W - 16) // 3
    for i, story in enumerate(HERO):
        draw_hero_card(d, story, MARGIN + i * (hw + 8), 203, hw, 262)
    # small cards: two rows of five
    cw = (CONTENT_W - 24) // 5
    for i, story in enumerate(CARDS[:5]):
        draw_small_card(d, story, MARGIN + i * (cw + 6), 469, cw, 140)
    for i, story in enumerate(CARDS[5:]):
        draw_small_card(d, story, MARGIN + i * (cw + 6), 613, cw, 140)
    draw_bottom(d)
    draw_date_check(d)
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
