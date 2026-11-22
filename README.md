# THE WORLD TODAY — Saturday 21 November 2026 (v4)

A newspaper front page for 21 November 2026: 40 stories across
8 regions (36 numbered + hero + 3 features). Lead story: Iran
strikes US bases in Bahrain, and Russia's triple-tap kills a boy of
7 in Kryvyi Rih — with missiles down in Poland and the APEC
three-way summit in Shenzhen ending with no breakthrough. Also: the
AI sell-off on Wall Street, the ICJ ruling that Myanmar is guilty of
genocide, and the capture of 'El Chapo Isidro' in Sinaloa.

v4 vs v3: the hero drops v3's overstated "peace declaration"
framing (the summit ended with no breakthrough) and leads with the
day's biggest verified story, the Iran strike on US bases, which v3
missed; adds the Poland missile incursion, Nvidia's H200 halt, and
the FBI database-hack probe; rebalances away from v3's
Ukraine-heavy list (10 stories) toward 8 regions.

## How it is made

`compose.py` renders the 1024×1024 front page with Pillow
(Liberation Serif/Sans + DejaVu). Regenerate `entry.png` with:

    python3 compose.py

`main.ts` is the entrypoint (Node 22, standard library only): it
copies `entry.png` to the grader's output path, byte for byte.

## Sources

AP, CNN, UN, ICJ, ISW.
