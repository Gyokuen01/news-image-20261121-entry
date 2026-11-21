# THE WORLD TODAY — Saturday 21 November 2026

A newspaper front page for 21 November 2026: 36 dated stories across
7 regions. Lead story: the Trump–Putin–Xi summit aftermath — a peace
declaration published, then Russia's heaviest strikes on Kyiv and
Kryvyi Rih. Also: the AI sell-off on Wall Street, the ICJ ruling that
Myanmar is guilty of genocide, and the capture of 'El Chapo Isidro'
in Sinaloa.

## How it is made

`compose.py` renders the 1024×1024 front page with Pillow
(Liberation Serif/Sans + DejaVu). Regenerate `entry.png` with:

    python3 compose.py

`main.ts` is the entrypoint (Node 22, standard library only): it
copies `entry.png` to the grader's output path, byte for byte.

## Sources

AP, NYT, The Telegraph, UN, ICJ.
