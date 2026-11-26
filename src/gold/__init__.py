"""Tahap 4–6 — fondasi Gold dan Rekonsiliasi.

Dua bentuk panel dilengkapi agar kompatibel dengan pekerjaan tim:

1. ``panel.parquet`` dan ``panel_lebar.parquet`` dari ``src/gold/panel.py``:
   panel panjang/lebar dengan status sel dan penanda anomali.
2. ``panel_<seri>.parquet`` dan ``panel_provinsi.parquet`` dari modul ini:
   panel per seri dengan satuan Gold yang diseragamkan dan lineage per sel.

Aturan sel mengikuti keputusan pembersihan yang sudah dicatat:

- K-004: grid 38 provinsi; agregat nasional 9999 tidak masuk panel provinsi.
- K-005: sel tanpa observasi tetap NaN, bukan nol dan tanpa imputasi.
- K-006: Bongkar dan Muat menjadi indikator terpisah; cakupan var2753
  (36 provinsi) tetap terlihat sebagai sel kosong pada grid 38 provinsi.
- K-009: nilai ekstrem yang valid dipertahankan.
- K-010: baris var1241 tahun 2019 diberi penanda patahan metodologi.
- K-013/K-014: satuan bongkar muat di Silver adalah ton (var2753) dan
  kilogram (var2754).

Seragamisasi satuan dilakukan di Gold (K-025): setiap indikator hanya
memakai satu satuan. Indikator persen memakai persen; indikator bongkar
muat diseragamkan ke ton, sehingga var2754 dikonversi dari kilogram ke ton.
Nilai asli tetap disimpan di kolom ``nilai_asli`` dan ``satuan_asli``.
Transformasi log10 dari nilai ton disimpan di ``nilai_log10`` untuk
analisis skala besar (K-026); nilai asli tidak diubah.

Keluaran unit-safe di ``data/gold/``:

- ``panel_<seri>.parquet``: satu tabel per seri, kunci
  (kode_prov, periode, indikator).
- ``panel_provinsi.parquet``: gabungan long semua seri dengan kolom nilai
  terpisah menurut satuan (``nilai_persen``, ``nilai_ton``,
  ``nilai_log10_ton``) agar satu kolom nilai tidak mencampur satuan.

Setiap sel terisi membawa ``_baris_silver`` dan ``_kunci_silver`` sehingga
dapat ditelusuri ke baris Silver asalnya; sel kosong tidak punya lineage
(K-027).

Keluaran kompatibilitas tim:
- data/gold/panel.parquet (panjang, 1.330 baris)
- data/gold/panel_lebar.parquet (lebar, 394 baris x 11 kolom)
- data/gold/panel_dasar.parquet (dasar, 1.295 baris untuk kompatibilitas)
- data/gold/rekonsiliasi.parquet (tabel rekonsiliasi integrasi, 28 baris)
- reports/panel-gold.md
- reports/tabel_rekonsiliasi.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.skema import KUNCI
from src.gold import panel as panel_lama
from src.gold import rekonsiliasi
from src.silver.katalog import ambil as ambil_katalog

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "gold"

SERI_UTAMA = ("var1241", "var2012", "var2013", "var2753", "var2754")

KOLOM_PANEL = [
    "kode_prov",
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "indikator",
    "nama_indikator",
    "rincian",
    "tingkat",
    "sumber",
    "seri_kode",
    "satuan",
    "satuan_asli",
    "nilai",
    "nilai_asli",
    "nilai_log10",
    "penanda_patahan",
    "_berkas_raw",
    "_sha256_raw",
    "_baris_silver",
    "_kunci_silver",
]

KOLOM_GABUNGAN = [
    "kode_prov",
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "indikator",
    "nama_indikator",
    "rincian",
    "tingkat",
    "sumber",
    "seri_kode",
    "satuan",
    "nilai_persen",
    "nilai_ton",
    "nilai_log10_ton",
    "penanda_patahan",
    "_berkas_raw",
    "_sha256_raw",
    "_baris_silver",
    "_kunci_silver",
]

KOLOM_TEKS = [
    "nama_wilayah",
    "periode",
    "indikator",
    "nama_indikator",
    "rincian",
    "tingkat",
    "sumber",
    "seri_kode",
    "satuan",
    "satuan_asli",
    "penanda_patahan",
    "_berkas_raw",
    "_sha256_raw",
    "_kunci_silver",
]


def _siapkan_silver(silver):
    """Salin Silver dengan nomor baris dan kunci lineage yang stabil."""
    s = silver.copy().reset_index(drop=True)
    s["_baris_silver"] = s.index.astype("Int64")
    s["_kunci_silver"] = s[KUNCI].astype(str).agg("|".join, axis=1)
    return s


def _provinsi(silver):
    """Daftar 38 provinsi dari Silver, tanpa agregat nasional 9999."""
    bagian = (
        silver.loc[silver["wilayah_kode"] != 9999, ["wilayah_kode", "nama_wilayah"]]
        .drop_duplicates()
        .copy()
    )
    bagian["kode_prov"] = bagian["wilayah_kode"] // 100
    bagian["nama_wilayah"] = bagian["nama_wilayah"].astype(str).str.upper()

    if bagian["kode_prov"].duplicated().any():
        contoh = bagian.loc[
            bagian["kode_prov"].duplicated(keep=False), ["kode_prov", "nama_wilayah"]
        ].head(3)
        raise ValueError(
            "kode_prov ganda dengan nama berbeda: "
            f"{contoh.to_dict('records')}"
        )

    bagian = (
        bagian[["kode_prov", "nama_wilayah"]]
        .sort_values("kode_prov")
        .reset_index(drop=True)
    )

    if len(bagian) != 38:
        raise ValueError(
            f"grid provinsi harus 38, ditemukan {len(bagian)} "
            f"({bagian['kode_prov'].tolist()})"
        )

    return bagian


def _periode(silver, seri):
    """Periode tahunan yang tersedia untuk satu seri."""
    periode = sorted(
        silver.loc[silver["seri_kode"] == seri, "periode"].astype(str).unique()
    )

    if not periode:
        raise ValueError(f"seri {seri} tidak punya periode di Silver")

    if not all(len(p) == 4 and p.isdigit() for p in periode):
        raise ValueError(f"seri {seri} punya periode bukan tahun empat digit: {periode}")

    return periode


def _rincian(silver, seri):
    """Rincian yang benar-benar ada di Silver untuk satu seri."""
    rincian = sorted(
        silver.loc[
            (silver["seri_kode"] == seri) & (silver["wilayah_kode"] != 9999),
            "rincian",
        ]
        .astype(str)
        .unique()
    )

    if not rincian:
        raise ValueError(f"seri {seri} tidak punya rincian provinsi di Silver")

    return rincian


def _satuan_asli(silver, seri):
    """Satu satuan Silver untuk seri ini; gagal bila tidak seragam."""
    satuan = (
        silver.loc[silver["seri_kode"] == seri, "satuan"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if len(satuan) != 1:
        raise ValueError(f"seri {seri} punya satuan Silver tidak seragam: {satuan}")

    return satuan[0]


def _target_satuan(satuan_asli):
    """Satuan Gold dan faktor konversi dari satuan Silver.

    Persen tetap persen. Satuan massa diseragamkan ke ton agar nilai
    var2753 dan var2754 sebanding dalam satu kolom.
    """
    if satuan_asli == "persen":
        return "persen", 1.0
    if satuan_asli == "ton":
        return "ton", 1.0
    if satuan_asli == "kilogram":
        return "ton", 0.001
    raise ValueError(f"satuan Silver {satuan_asli!r} belum punya aturan Gold")


def _nama_indikator(seri, rincian):
    """Label indikator yang mudah dibaca, diturunkan dari katalog Silver."""
    nama = ambil_katalog(seri)["nama"]
    if rincian != "Tidak ada":
        nama = f"{nama} - {rincian}"
    return nama


def _panel_indikator(silver, provinsi, seri, rincian):
    """Grid provinsi x periode untuk satu seri dan satu rincian."""
    satuan_asli = _satuan_asli(silver, seri)
    satuan_gold, faktor = _target_satuan(satuan_asli)
    indikator = seri if rincian == "Tidak ada" else f"{seri}_{rincian}"

    bagian = silver.loc[
        (silver["seri_kode"] == seri)
        & (silver["rincian"] == rincian)
        & (silver["wilayah_kode"] != 9999)
    ].copy()
    bagian["kode_prov"] = bagian["wilayah_kode"] // 100
    bagian["periode"] = bagian["periode"].astype(str)

    if bagian.duplicated(["kode_prov", "periode"]).any():
        contoh = bagian.loc[
            bagian.duplicated(["kode_prov", "periode"], keep=False),
            ["kode_prov", "periode"],
        ].head(3)
        raise ValueError(
            f"{indikator}: kunci provinsi-periode ganda di Silver, "
            f"mis. {contoh.to_dict('records')}"
        )

    periode = _periode(silver, seri)

    grid = pd.MultiIndex.from_product(
        [provinsi["kode_prov"], periode], names=["kode_prov", "periode"]
    ).to_frame(index=False)
    grid = grid.merge(provinsi, on="kode_prov", how="left")

    panel = grid.merge(
        bagian, on=["kode_prov", "periode"], how="left", suffixes=("", "_silver")
    )

    if "nama_wilayah_silver" in panel.columns:
        panel = panel.drop(columns=["nama_wilayah_silver"])

    # Kolom tetap terisi untuk seluruh grid; nilai dan lineage boleh kosong.
    panel["wilayah_kode"] = panel["kode_prov"] * 100
    panel["seri_kode"] = seri
    panel["indikator"] = indikator
    panel["nama_indikator"] = _nama_indikator(seri, rincian)
    panel["rincian"] = rincian
    panel["tingkat"] = "provinsi"
    panel["sumber"] = "bps"
    panel["satuan"] = satuan_gold
    panel["satuan_asli"] = satuan_asli

    # Nilai asli dari Silver disimpan sebelum konversi satuan.
    panel["nilai_asli"] = panel["nilai"].astype(float)
    panel["nilai"] = panel["nilai_asli"] * faktor

    # Log10 hanya untuk indikator massa; persen tetap tanpa transformasi.
    panel["nilai_log10"] = np.nan
    if satuan_gold == "ton":
        positif = panel["nilai"] > 0
        panel.loc[positif, "nilai_log10"] = np.log10(panel.loc[positif, "nilai"])

    # Penanda patahan K-010 berlaku untuk seluruh grid var1241 tahun 2019,
    # termasuk sel kosong, karena patahan melekat pada periode pengukuran.
    panel["penanda_patahan"] = panel["penanda_patahan"].fillna("")
    patahan = (seri == "var1241") & (panel["periode"].astype(str) == "2019")
    panel.loc[patahan, "penanda_patahan"] = "patahan_metodologi"

    panel["_baris_silver"] = panel["_baris_silver"].astype("Int64")
    for kol in KOLOM_TEKS:
        panel[kol] = panel[kol].astype("string")

    panel = panel[KOLOM_PANEL].sort_values(
        ["kode_prov", "periode", "indikator"], kind="stable"
    )
    return panel.reset_index(drop=True)


def _panel_seri(silver, provinsi, seri):
    """Gabungkan rincian satu seri menjadi tabel panel seri."""
    panel = pd.concat(
        [
            _panel_indikator(silver, provinsi, seri, rincian)
            for rincian in _rincian(silver, seri)
        ],
        ignore_index=True,
    )

    kunci = ["kode_prov", "periode", "indikator"]
    if panel.duplicated(kunci).any():
        raise ValueError(f"panel_{seri}: kunci {kunci} kembar")

    return panel


def _gabung_panel(panels):
    """Panel long semua seri dengan nilai dipisah menurut satuan."""
    gabungan = pd.concat(panels.values(), ignore_index=True)

    # Satu kolom nilai tidak boleh mencampur persen dan ton.
    gabungan["nilai_persen"] = gabungan["nilai"].where(
        gabungan["satuan"] == "persen"
    )
    gabungan["nilai_ton"] = gabungan["nilai"].where(gabungan["satuan"] == "ton")
    gabungan["nilai_log10_ton"] = gabungan["nilai_log10"].where(
        gabungan["satuan"] == "ton"
    )

    gabungan = gabungan[KOLOM_GABUNGAN].sort_values(
        ["kode_prov", "periode", "indikator"], kind="stable"
    ).reset_index(drop=True)

    kunci = ["kode_prov", "periode", "indikator"]
    if gabungan.duplicated(kunci).any():
        contoh = gabungan.loc[
            gabungan.duplicated(kunci, keep=False), kunci
        ].head(3)
        raise ValueError(
            f"panel_provinsi: kunci {kunci} kembar, mis. {contoh.to_dict('records')}"
        )

    if (gabungan["nilai_persen"].notna() & gabungan["nilai_ton"].notna()).any():
        raise ValueError("panel_provinsi: ada baris dengan nilai persen dan ton sekaligus")

    return gabungan


def jalankan(silver):
    """Jalankan pembentukan panel Gold, panel unit-safe, dan rekonsiliasi."""
    # Panel panjang/lebar yang sudah menjadi keluaran tim dan dipakai tes.
    hasil = panel_lama.jalankan(silver)

    # Panel per seri dengan satuan Gold seragam dan lineage per sel.
    s = _siapkan_silver(silver)
    provinsi = _provinsi(s)

    panels = {
        seri: _panel_seri(s, provinsi, seri)
        for seri in SERI_UTAMA
    }
    gabungan = _gabung_panel(panels)

    OUTPUT.mkdir(parents=True, exist_ok=True)

    for seri, panel in panels.items():
        panel.to_parquet(OUTPUT / f"panel_{seri}.parquet", index=False)

    gabungan.to_parquet(OUTPUT / "panel_provinsi.parquet", index=False)

    # Panel dasar dipertahankan untuk kompatibilitas audit lapis Bronze/Silver.
    panel_dasar = silver.copy()
    panel_dasar["kode_prov"] = panel_dasar["wilayah_kode"] // 100
    panel_dasar["tingkat"] = panel_dasar["wilayah_kode"].map(
        lambda kode: "nasional" if kode == 9999 else "provinsi"
    )
    panel_dasar.to_parquet(OUTPUT / "panel_dasar.parquet", index=False)

    kosong = int(
        (gabungan["nilai_persen"].isna() & gabungan["nilai_ton"].isna()).sum()
    )
    patahan = int(
        gabungan["penanda_patahan"].eq("patahan_metodologi").sum()
    )

    print(
        f"Gold panel unit-safe: {len(gabungan):,} baris, "
        f"{gabungan['seri_kode'].nunique()} seri, "
        f"{gabungan['indikator'].nunique()} indikator, "
        f"{kosong} sel kosong, {patahan} baris berpatahan"
    )
    print(f"Lokasi: {OUTPUT}")

    hasil.update({f"panel_{seri}": isi for seri, isi in panels.items()})
    hasil["panel_provinsi"] = gabungan
    hasil["panel_dasar"] = panel_dasar

    # Tahap 6: Bangun tabel rekonsiliasi.
    df_rekon = rekonsiliasi.jalankan(silver, hasil.get("panel"))
    hasil["rekonsiliasi"] = df_rekon

    return hasil
