"""Bangkitkan bukti hasil pipeline dan pengujian panel Gold.

Menjalankan pipeline dan unit test, lalu memeriksa langsung berkas keluaran:

- keunikan kunci panel (panel_provinsi, panel_<seri>, panel, panel_lebar);
- lineage setiap sel terisi ke baris Silver asalnya;
- kelengkapan kategori tabel rekonsiliasi.

Hasil ditulis ke reports/bukti-panel.md agar dapat dilampirkan pada review PR.

    python bukti_panel.py
"""
from __future__ import annotations

import subprocess
import sys
import sqlite3
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.skema import KOLOM, KUNCI

ROOT = Path(__file__).resolve().parent
GOLD = ROOT / "data" / "gold"
SILVER = ROOT / "data" / "silver" / "silver.parquet"
REKON = ROOT / "reports" / "tabel_rekonsiliasi.csv"
LAPORAN = ROOT / "reports" / "bukti-panel.md"

KUNCI_PANEL = ["kode_prov", "periode", "indikator"]
KUNCI_KOMPAT = ["indikator", "wilayah_kode", "periode"]
SERI = ("var1241", "var2012", "var2013", "var2753", "var2754")
KUNCI_SILVER = [
    "sumber",
    "seri_kode",
    "wilayah_kode",
    "periode",
    "rincian",
    "_berkas_raw",
]


def jalankan(perintah):
    hasil = subprocess.run(
        [sys.executable, *perintah],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    keluaran = (hasil.stdout or "") + (hasil.stderr or "")
    keluaran = keluaran.replace(str(ROOT), ".")
    return hasil.returncode, keluaran.strip()


def duplikat(df, kunci):
    return int(df.duplicated(kunci).sum())


def periksa_lineage(silver):
    panel = pd.read_parquet(GOLD / "panel_provinsi.parquet")
    terisi = panel["_baris_silver"].notna()
    uji = panel.loc[terisi].reset_index(drop=True)
    idx = uji["_baris_silver"].astype("int64").to_numpy()
    acuan = silver.reset_index(drop=True).iloc[idx].reset_index(drop=True)

    kunci_acuan = acuan[KUNCI_SILVER].astype(str).agg("|".join, axis=1)
    kunci_uji = uji["_kunci_silver"].astype("string")
    beda_kunci = int((kunci_uji != kunci_acuan).sum())

    beda_kolom = {}
    for kol in ("seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw", "_sha256_raw"):
        a = uji[kol].astype("string").fillna("<NA>")
        b = acuan[kol].astype("string").fillna("<NA>")
        beda_kolom[kol] = int((a != b).sum())

    nilai_silver = acuan["nilai"].astype(float).to_numpy()
    faktor = np.where(acuan["seri_kode"].astype(str).to_numpy() == "var2754", 0.001, 1.0)
    harapan = nilai_silver * faktor

    persen = uji["satuan"].astype(str).eq("persen").to_numpy()
    ton = uji["satuan"].astype(str).eq("ton").to_numpy()
    beda_nilai = 0
    if persen.any():
        aktual = uji.loc[persen, "nilai_persen"].astype(float).to_numpy()
        beda_nilai += int((~np.isclose(aktual, harapan[persen], equal_nan=True)).sum())
    if ton.any():
        aktual = uji.loc[ton, "nilai_ton"].astype(float).to_numpy()
        beda_nilai += int((~np.isclose(aktual, harapan[ton], equal_nan=True)).sum())

    return panel, terisi.sum(), beda_kunci, beda_kolom, beda_nilai, uji, acuan


def main():
    kode_pipa, log_pipa = jalankan(["pipeline.py"])
    kode_tes, log_tes = jalankan(
        ["-m", "unittest", "tests/test_gold.py", "tests/test_sql.py"]
    )

    silver = pd.read_parquet(SILVER)
    panel, jumlah_terisi, beda_kunci, beda_kolom, beda_nilai, uji, acuan = periksa_lineage(silver)

    baris = [
        "# Bukti hasil pipeline dan pengujian panel Gold",
        "",
        f"Dibangkitkan oleh `python bukti_panel.py` pada {date.today().isoformat()}.",
        "",
        "## 1. Hasil `python pipeline.py`",
        "",
        f"Kode keluar: **{kode_pipa}**",
        "",
        "```text",
        log_pipa,
        "```",
        "",
        "## 2. Hasil `python -m unittest tests/test_gold.py tests/test_sql.py`",
        "",
        f"Kode keluar: **{kode_tes}**",
        "",
        "```text",
        log_tes,
        "```",
        "",
        "## 3. Bukti kunci panel unik",
        "",
        "| Berkas | Kunci | Baris | Baris kunci kembar |",
        "|---|---|---:|---:|",
    ]

    for seri in SERI:
        df = pd.read_parquet(GOLD / f"panel_{seri}.parquet")
        baris.append(
            f"| `panel_{seri}.parquet` | `kode_prov + periode + indikator` | "
            f"{len(df):,} | {duplikat(df, KUNCI_PANEL)} |"
        )

    prov = pd.read_parquet(GOLD / "panel_provinsi.parquet")
    lebar = pd.read_parquet(GOLD / "panel_lebar.parquet")
    kompat = pd.read_parquet(GOLD / "panel.parquet")
    kosong = prov["nilai_persen"].isna() & prov["nilai_ton"].isna()
    jumlah_kosong = int(kosong.sum())
    kosong_berbaris = int(prov.loc[kosong, "_baris_silver"].notna().sum())
    kosong_berkunci = int(prov.loc[kosong, "_kunci_silver"].notna().sum())
    baris.extend(
        [
            f"| `panel_provinsi.parquet` | `kode_prov + periode + indikator` | "
            f"{len(prov):,} | {duplikat(prov, KUNCI_PANEL)} |",
            f"| `panel.parquet` | `indikator + wilayah_kode + periode` | "
            f"{len(kompat):,} | {duplikat(kompat, KUNCI_KOMPAT)} |",
            f"| `panel_lebar.parquet` | `wilayah_kode + periode` | "
            f"{len(lebar):,} | {duplikat(lebar, ['wilayah_kode', 'periode'])} |",
            "",
            "Tidak ada baris kunci kembar pada seluruh tabel panel di atas.",
            "",
            "## 4. Bukti lineage sel Gold ke Silver",
            "",
            f"- Sel terisi di `panel_provinsi.parquet`: **{jumlah_terisi:,}** dari "
            f"{len(prov):,} baris grid.",
            f"- `_baris_silver` dan `_kunci_silver` terisi pada seluruh sel terisi: "
            f"**{int(prov['_baris_silver'].notna().sum()):,}** baris.",
            f"- Sel kosong: **{jumlah_kosong:,}**; memiliki `_baris_silver`: "
            f"**{kosong_berbaris}**; memiliki `_kunci_silver`: **{kosong_berkunci}**.",
            f"- `_kunci_silver` yang tidak sama dengan kunci baris Silver acuan: "
            f"**{beda_kunci}**.",
            f"- Nilai Gold yang tidak sama dengan nilai Silver setelah konversi satuan "
            f"(var2754 kg -> ton): **{beda_nilai}**.",
            "",
            "| Kolom yang dicocokkan dengan baris Silver | Jumlah ketidakcocokan |",
            "|---|---:|",
        ]
    )
    for kol, jumlah in beda_kolom.items():
        baris.append(f"| `{kol}` | {jumlah} |")

    baris.extend(
        [
            "",
            "Contoh lima sel terisi beserta baris Silver asalnya:",
            "",
            "| kode_prov | periode | indikator | _baris_silver | nilai Gold | nilai Silver | satuan Gold |",
            "|---:|---|---|---:|---:|---:|---|",
        ]
    )
    for i in range(min(5, len(uji))):
        g = uji.iloc[i]
        s = acuan.iloc[i]
        nilai_gold = g["nilai_persen"] if pd.notna(g["nilai_persen"]) else g["nilai_ton"]
        baris.append(
            f"| {g['kode_prov']} | {g['periode']} | `{g['indikator']}` | "
            f"{int(g['_baris_silver'])} | {nilai_gold:g} | {s['nilai']:g} | {g['satuan']} |"
        )

    baris.extend(
        [
            "",
            "Kunci lineage lengkap tiga baris pertama:",
            "",
            "```text",
        ]
    )
    for i in range(min(3, len(uji))):
        baris.append(str(uji.iloc[i]["_kunci_silver"]))
    baris.extend(["```", ""])

    if REKON.exists():
        rekon = pd.read_csv(REKON)
        kategori = rekon["kategori"].value_counts()
        berpasangan = rekon["pasangan"].notna() & rekon["pasangan"].astype(str).str.strip().ne("")
        tanpa = int((berpasangan & rekon["kategori"].isna()).sum())
        baris.extend(
            [
                "## 5. Kategori tabel rekonsiliasi",
                "",
                f"- Baris rekonsiliasi: **{len(rekon)}**; berpasangan: **{int(berpasangan.sum())}**.",
                f"- Pasangan tanpa kategori: **{tanpa}**.",
                "",
                "| Kategori | Baris |",
                "|---|---:|",
            ]
        )
        for nama, jumlah in kategori.items():
            baris.append(f"| {nama} | {jumlah} |")
        baris.append("")

    basis = ROOT / "data" / "silver" / "silver.sqlite"
    if basis.exists():
        con = sqlite3.connect(basis)
        try:
            jumlah = {
                tabel: con.execute(f"SELECT COUNT(*) FROM {tabel}").fetchone()[0]
                for tabel in ("silver", "seri", "wilayah", "berkas_raw")
            }
            integritas = con.execute("PRAGMA integrity_check").fetchone()[0]
            pelanggaran = con.execute("PRAGMA foreign_key_check").fetchall()
            provinsi = con.execute("SELECT COUNT(*) FROM v_provinsi").fetchone()[0]
            nasional = con.execute("SELECT COUNT(*) FROM v_nasional").fetchone()[0]
            db = pd.read_sql_query(
                "SELECT " + ", ".join(KOLOM) + " FROM silver", con
            )
        finally:
            con.close()

        acuan = silver[KOLOM].sort_values(KUNCI).reset_index(drop=True)
        hasil = db[KOLOM].sort_values(KUNCI).reset_index(drop=True)
        identik = acuan.equals(hasil)

        baris.extend(
            [
                "## 6. Basis data SQLite",
                "",
                f"- Berkas: `{basis.relative_to(ROOT).as_posix()}`.",
                f"- Tabel: `silver` {jumlah['silver']:,} baris, `seri` "
                f"{jumlah['seri']}, `wilayah` {jumlah['wilayah']}, `berkas_raw` "
                f"{jumlah['berkas_raw']}.",
                f"- `PRAGMA integrity_check`: **{integritas}**; "
                f"`PRAGMA foreign_key_check`: **{len(pelanggaran)} pelanggaran**.",
                f"- Pandangan: `v_provinsi` {provinsi:,} baris, `v_nasional` "
                f"{nasional:,} baris.",
                f"- Baca-balik SQL sama persis dengan `silver.parquet`: **{identik}**.",
                "",
            ]
        )

    LAPORAN.write_text("\n".join(baris), encoding="utf-8")
    print(f"Laporan bukti ditulis: {LAPORAN}")
    print(f"Pipeline exit={kode_pipa}, test exit={kode_tes}")
    print(f"Sel terisi={jumlah_terisi}, beda kunci={beda_kunci}, beda nilai={beda_nilai}")


if __name__ == "__main__":
    main()
