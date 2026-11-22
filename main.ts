// Salin gambar berita 21 November 2026 ke folder keluaran grader.
//
// Grader menjalankan program ini dari repo read-only (/bot) dengan folder
// keluaran yang bisa ditulis di $MAKEFUN_OUTPUT_DIR. Karena /bot tidak bisa
// ditulis, salinan gambar HARUS mendarat di folder keluaran itu, bukan di
// samping file ini. Bila variabel lingkungan tidak diset (misalnya saat
// dijalankan lokal), gambar ditulis di samping file ini. Argumen pertama
// di baris perintah, bila diberikan, dipakai sebagai jalur tujuan lengkap
// dan mengalahkan kedua pilihan di atas.

import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// Folder tempat file ini tinggal — di situlah entry.png tersimpan.
const here = dirname(fileURLToPath(import.meta.url));
const picture = join(here, "entry.png");

// Tentukan jalur tujuan, dengan urutan prioritas:
// 1. argumen baris perintah, 2. $MAKEFUN_OUTPUT_DIR, 3. folder file ini.
const givenTarget = process.argv[2];
const outFolder = process.env.MAKEFUN_OUTPUT_DIR;
const destination =
  givenTarget !== undefined
    ? resolve(givenTarget)
    : join(resolve(outFolder ?? here), "entry.png");

// Pastikan folder tujuan ada, lalu salin byte demi byte.
mkdirSync(dirname(destination), { recursive: true });
copyFileSync(picture, destination);

console.log(`Wrote ${destination}`);
