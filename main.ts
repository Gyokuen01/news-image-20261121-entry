// news-image-20261121 entry (Node 22, standard library only).
//
// The front page itself is drawn by compose.py and committed as entry.png
// beside this file. This program's only job is to place that exact image
// at the grader's output path, byte for byte, on every run.
//
// Run it locally with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
// and compare out/entry.png with the committed entry.png.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, "entry.png"), readFileSync(join(here, "entry.png")));
