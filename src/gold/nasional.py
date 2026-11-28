"""Tahap 6 (persiapan) — tabel nasional Gold: satu baris per periode x seri (x rincian).

Isi: angka nasional seri utama (var1241, var2012, var2013, var2753, var2754) dan seri pembanding
(EN.POP.SLUM.UR.ZS). Kolom `asal` menyatakan dari mana tiap angka berasal:

- baris_indonesia : baris Indonesia (wilayah 9999) yang diterbitkan sumber. Sebagian dari Silver;
                    bila Silver tidak memuatnya (var2753, dihapus dari Silver oleh K-002) baris
                    yang sama dipulihkan dari berkas mentah lewat pembaca ekstraksi, lengkap dengan
                    lineage berkas aslinya. Silver tidak diubah.
- pembanding_wdi  : seri pembanding WDI (Indonesia) dari Silver.
- agregat_provinsi: disediakan bila suatu seri utama tidak menerbitkan baris Indonesia sama sekali
                    dan diputuskan diagregasi dari provinsi (aturan bobot ditulis di log). Pada
                    Kasus 19 tidak dipakai: semua seri utama menerbitkan baris Indonesia.

Satuan mengikuti aturan Gold (persen tetap, massa ke ton; lihat src.gold._target_satuan) dengan
nilai asli dan satuan asli tetap disimpan. Nilai persen dan ton tidak berbagi kolom.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.manifest import baca as baca_manifest
from src.ekstraksi.bps import baca_csv
from src.silver.katalog import ambil as ambil_katalog

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "gold"

ASAL_SAH = {"baris_indonesia", "agregat_provinsi", "pembanding_wdi"}
KUNCI = ["indikator", "periode"]
KOLOM = [
    "periode", "indikator", "nama_indikator", "seri_kode", "rincian", "sumber", "peran", "asal",
    "satuan", "nilai_persen", "nilai_ton", "satuan_asli", "nilai_asli", "penanda_patahan",
    "_berkas_raw", "_sha256_raw",
]


def _dari_silver(silver):
    """Baris Indonesia (9999) di Silver: seri utama BPS dan pembanding WDI."""
    n = silver.loc[silver["wilayah_kode"] == 9999].copy()
    n["periode"] = n["periode"].astype(str)
    n["nilai_asli"] = n["nilai"].astype(float)
    n["satuan_asli"] = n["satuan"].astype(str)
    n["asal"] = np.where(n["sumber"] == "wdi", "pembanding_wdi", "baris_indonesia")
    return n[["seri_kode", "rincian", "periode", "sumber", "asal", "nilai_asli", "satuan_asli",
              "penanda_patahan", "_berkas_raw", "_sha256_raw"]]


def _dari_mentah(seri):
    """Baris Indonesia (wilayah_id 9999) dari berkas mentah BPS untuk seri yang tidak punya di Silver.

    Nilai tidak diubah (K-013: satuan var2753 diganti labelnya, bukan dikonversi); satuan asli
    mengikuti katalog Silver supaya sama dengan seri itu di tempat lain.
    """
    k = ambil_katalog(seri)
    mentah = baca_csv(k["berkas_data"])
    n = mentah.loc[mentah["wilayah_id"].astype(str) == "9999"]
    return pd.DataFrame({
        "seri_kode": seri,
        "rincian": n["turvar"].astype(str).to_numpy(),
        "periode": n["tahun"].astype(str).to_numpy(),
        "sumber": k["sumber"],
        "asal": "baris_indonesia",
        "nilai_asli": n["nilai"].astype(float).to_numpy(),
        "satuan_asli": k["satuan"],
        "penanda_patahan": "",
        "_berkas_raw": n["_berkas_raw"].to_numpy(),
        "_sha256_raw": n["_sha256_raw"].to_numpy(),
    })


def _periksa(tabel):
    """Berhenti bila kunci kembar, asal tak sah, lineage kosong atau tak cocok MANIFEST, atau satuan campur."""
    if tabel.duplicated(KUNCI).any():
        raise ValueError(f"nasional: kunci {KUNCI} kembar")
    if not set(tabel["asal"]) <= ASAL_SAH:
        raise ValueError(f"nasional: asal tidak sah {set(tabel['asal']) - ASAL_SAH}")
    if tabel[["_berkas_raw", "_sha256_raw"]].isna().any().any():
        raise ValueError("nasional: ada baris tanpa _berkas_raw/_sha256_raw")
    manifest = baca_manifest()
    salah = [b for b, s in tabel[["_berkas_raw", "_sha256_raw"]].drop_duplicates().itertuples(index=False)
             if manifest.get(b) != s]
    if salah:
        raise ValueError(f"nasional: sha256 tidak cocok MANIFEST untuk {salah}")
    if (tabel["nilai_persen"].notna() & tabel["nilai_ton"].notna()).any() or \
            (tabel["nilai_persen"].isna() & tabel["nilai_ton"].isna()).any():
        raise ValueError("nasional: tiap baris harus punya tepat satu nilai (persen atau ton)")


def bangun_tabel_nasional(silver):
    # Diimpor di sini (bukan di atas) agar tidak melingkar dengan src/gold/__init__.py.
    from src.gold import SERI_UTAMA, _nama_indikator, _target_satuan

    bagian = [_dari_silver(silver)]
    ada = set(bagian[0]["seri_kode"])
    tanpa_nasional = []
    for seri in SERI_UTAMA:
        if seri in ada:
            continue
        pulih = _dari_mentah(seri)
        if pulih.empty:
            tanpa_nasional.append(seri)   # tidak menerbitkan baris Indonesia sama sekali
        else:
            bagian.append(pulih)
            print(f"nasional: {seri} tidak punya baris Indonesia di Silver; {len(pulih)} baris dipulihkan dari mentah")
    if tanpa_nasional:
        print(f"nasional: tanpa padanan nasional: {tanpa_nasional}")

    t = pd.concat(bagian, ignore_index=True)
    satuan = t["satuan_asli"].map(lambda s: _target_satuan(s))
    t["satuan"] = satuan.map(lambda x: x[0])
    t["nilai"] = t["nilai_asli"] * satuan.map(lambda x: x[1])
    t["nilai_persen"] = t["nilai"].where(t["satuan"] == "persen")
    t["nilai_ton"] = t["nilai"].where(t["satuan"] == "ton")
    t["indikator"] = np.where(t["rincian"] == "Tidak ada", t["seri_kode"], t["seri_kode"] + "_" + t["rincian"])
    t["nama_indikator"] = [_nama_indikator(s, r) for s, r in zip(t["seri_kode"], t["rincian"])]
    t["peran"] = np.where(t["asal"] == "pembanding_wdi", "pembanding", "utama")
    t = t[KOLOM].sort_values(["indikator", "periode"], kind="stable").reset_index(drop=True)
    for kol in KOLOM:
        if t[kol].dtype == object:
            t[kol] = t[kol].astype("string")
    _periksa(t)
    return t


def jalankan(silver):
    """Bangun tabel nasional Gold dan simpan ke data/gold/nasional.parquet."""
    t = bangun_tabel_nasional(silver)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    t.to_parquet(OUTPUT / "nasional.parquet", index=False)
    per_asal = t["asal"].value_counts().to_dict()
    print(f"Gold nasional: {len(t):,} baris, {t['indikator'].nunique()} indikator, asal {per_asal}")
    return t
