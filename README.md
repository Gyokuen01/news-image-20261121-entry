# Saturday 21 November 2026 (v5)

A front page for 21 November 2026: 37 stories across 9 regions, every
one dated Saturday 21 November 2026 (UTC). The date itself is the
masthead; a UTC strip shows the day unfolding; a colour-coded region
bar counts the breadth; three large pictured stories (Iran strikes
Bahrain as tankers are hit in Hormuz; COP31 deadlocked over fossil
fuels in overtime; Mexico captures 'El Chapo Isidro'), ten more
pictured cards (Peru quake, BepiColombo at Mercury, EU-Indonesia
trade pact, Geneva killer-robot talks, Sparta II ablaze, Banda Sea
quake, Bitcoin, France marches, England rugby, BTS at the MAMAs), a
world map with pins, a 24-story list, a DATE CHECK box naming the
stories left out because they belong to another day, and a HOW SURE
legend. Every story carries its sources and a status (CONFIRMED /
OFFICIAL / REPORTED / CLAIM).

v5 vs v4: the date becomes the masthead; the story set is corrected to
Saturday alone — v4's lead and features were largely Friday/Thursday
news (the Wall Street sell-off, the Kryvyi Rih strike, the ICJ Myanmar
ruling, the APEC Shenzhen summit), all now named in the DATE CHECK box
instead; adds the UTC strip, the world map, pictures for the top 13
stories, per-story sources and status badges, and a region bar. The
dense 36-story small-type grid is replaced by 10 pictured cards plus a
24-story list, so the page stays legible at about 300 pixels across.

## How it is made

`compose.py` renders the 1024x1024 front page with Pillow (DejaVu
Serif/Sans only, no network). Regenerate `entry.png` with:

    python3 compose.py

`main.ts` is the entrypoint (Node 22, standard library only): it
copies `entry.png` to the grader's output path, byte for byte.

## Sources

Named beside each story: AP, Reuters, AFP, BBC, USGS, ESA, JAXA,
UKMTO, EU, FBI, and others.
