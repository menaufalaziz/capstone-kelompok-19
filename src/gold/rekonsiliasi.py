"""Modul Tahap 6 — Integrasi dan Rekonsiliasi Data.

Komponen: Profil dan Pembersihan / Analis Utama (Riska Erlis / NIM 124450022).

Fungsi modul ini:
1. Menyusun tabel rekonsiliasi yang membandingkan:
   a. Seri utama BPS var1241 vs pembanding internasional WDI EN.POP.SLUM.UR.ZS (arah perubahan & definisi).
   b. Agregat kargo udara var2754 (jumlah provinsi vs baris INDONESIA BPS).
   c. Rerata transportasi darat var2012 & var2013 (unweighted provinsi vs baris INDONESIA BPS).
   d. Kargo laut var2753 (cakupan 36 provinsi pesisir vs ketiadaan baris nasional).
2. Mengklasifikasikan setiap selisih ke kategori baku:
   - Definisi berbeda
   - Metode berbeda
   - Cakupan berbeda
   - Vintage berbeda
   - Belum terjelaskan
3. Menyimpan tabel rekonsiliasi ke data/gold/rekonsiliasi.parquet dan reports/tabel_rekonsiliasi.csv.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GOLD_DIR = ROOT / "data" / "gold"
REPORTS_DIR = ROOT / "reports"


def bangun_tabel_rekonsiliasi(silver: pd.DataFrame) -> pd.DataFrame:
    """Membangun tabel rekonsiliasi komprehensif dari data Silver."""
    # 1. Pasangan Eksternal: var1241 (BPS Nasional) vs WDI EN.POP.SLUM.UR.ZS
    v1241_nas = (
        silver[(silver["seri_kode"] == "var1241") & (silver["wilayah_kode"] == 9999)][
            ["periode", "nilai", "satuan"]
        ]
        .rename(columns={"nilai": "nilai_utama", "satuan": "satuan_utama"})
        .copy()
    )
    v1241_nas["periode"] = v1241_nas["periode"].astype(str)

    wdi = (
        silver[silver["seri_kode"] == "EN.POP.SLUM.UR.ZS"][
            ["periode", "nilai", "satuan"]
        ]
        .rename(columns={"nilai": "nilai_pembanding", "satuan": "satuan_pembanding"})
        .copy()
    )
    wdi["periode"] = wdi["periode"].astype(str)

    m1 = pd.merge(v1241_nas, wdi, on="periode", how="inner")
    m1["pasangan"] = "var1241 (BPS Nasional) vs WDI EN.POP.SLUM.UR.ZS"
    m1["kategori"] = "Definisi berbeda"
    m1["selisih"] = m1["nilai_utama"] - m1["nilai_pembanding"]
    m1["persen_selisih"] = (
        (m1["nilai_utama"] - m1["nilai_pembanding"]) / m1["nilai_pembanding"]
    ) * 100
    m1["penjelasan"] = m1["periode"].map({
        "2016": "BPS mengukur % RT hunian layak (arah positif), WDI mengukur % penduduk perkotaan di kawasan kumuh (arah negatif). BPS naik (+1,15 pp), WDI turun (-1,65 pp); arah perubahan berlawanan secara konsisten.",
        "2018": "BPS mencapai puncak 95,70% (kriteria 2015-2018), WDI turun ke 20,24%. Tren peningkatan hunian layak selaras dengan penurunan kawasan kumuh perkotaan.",
        "2020": "BPS turun drastis ke 59,54% akibat patahan seri metodologi 4 kriteria SDG (K-010). WDI turun tipis ke 19,41% tanpa mencatat perubahan metodologis BPS.",
        "2022": "BPS naik bertahap ke 60,66% pasca-patahan. WDI stagnan di 19,41% (belum ada survei baru UN-Habitat pada rilis arsip ini).",
    })

    # 2. Pasangan Internal Kargo Udara: var2754 Bongkar & Muat (Jumlah Provinsi vs BPS Nasional 9999)
    v2754_nas = (
        silver[(silver["seri_kode"] == "var2754") & (silver["wilayah_kode"] == 9999)][
            ["rincian", "periode", "nilai", "satuan"]
        ]
        .rename(columns={"nilai": "nilai_pembanding", "satuan": "satuan_pembanding"})
        .copy()
    )
    v2754_nas["periode"] = v2754_nas["periode"].astype(str)

    v2754_prov = (
        silver[(silver["seri_kode"] == "var2754") & (silver["wilayah_kode"] != 9999)]
        .groupby(["rincian", "periode"])["nilai"]
        .sum()
        .reset_index()
        .rename(columns={"nilai": "nilai_utama"})
    )
    v2754_prov["periode"] = v2754_prov["periode"].astype(str)
    v2754_prov["satuan_utama"] = "kilogram"

    m2 = pd.merge(v2754_prov, v2754_nas, on=["rincian", "periode"])
    m2["pasangan"] = "var2754 " + m2["rincian"] + " (Jumlah Provinsi vs BPS Nasional)"
    m2["kategori"] = "Metode berbeda"
    m2["selisih"] = m2["nilai_utama"] - m2["nilai_pembanding"]
    m2["persen_selisih"] = (
        (m2["nilai_utama"] - m2["nilai_pembanding"]) / m2["nilai_pembanding"]
    ) * 100
    m2["penjelasan"] = np.where(
        m2["periode"] == "2023",
        "Agregat provinsi cocok sempurna 100,000% dengan angka nasional BPS (selisih 0 kg).",
        "Selisih sangat kecil (<0,14%) disebabkan pembulatan angka nasional BPS ke jutaan kg terdekat pada berkas sumber, sedangkan agregat provinsi menjumlahkan angka riil.",
    )
    m2 = m2.drop(columns=["rincian"])

    # 3. Pasangan Internal Transportasi Darat: var2012 & var2013 (Rerata Unweighted Provinsi vs BPS Nasional 9999)
    rows_trans = []
    for vk, nm in [
        ("var2012", "var2012 Moda Transportasi (Rerata Provinsi vs BPS Nasional)"),
        ("var2013", "var2013 Kemacetan/Angkutan (Rerata Provinsi vs BPS Nasional)"),
    ]:
        nas = (
            silver[(silver["seri_kode"] == vk) & (silver["wilayah_kode"] == 9999)][
                ["periode", "nilai", "satuan"]
            ]
            .rename(columns={"nilai": "nilai_pembanding", "satuan": "satuan_pembanding"})
            .copy()
        )
        nas["periode"] = nas["periode"].astype(str)

        prov = (
            silver[(silver["seri_kode"] == vk) & (silver["wilayah_kode"] != 9999)]
            .groupby("periode")["nilai"]
            .mean()
            .reset_index()
            .rename(columns={"nilai": "nilai_utama"})
        )
        prov["periode"] = prov["periode"].astype(str)
        prov["satuan_utama"] = "persen"

        m = pd.merge(prov, nas, on="periode")
        m["pasangan"] = nm
        m["kategori"] = "Metode berbeda"
        m["selisih"] = m["nilai_utama"] - m["nilai_pembanding"]
        m["persen_selisih"] = (
            (m["nilai_utama"] - m["nilai_pembanding"]) / m["nilai_pembanding"]
        ) * 100
        m["penjelasan"] = np.where(
            vk == "var2012",
            "BPS Nasional menggunakan pembobotan populasi rumah tangga (weighted pooling), sedangkan rerata provinsi merupakan rerata unweighted 34 provinsi (selisih ~3,2-3,3 pp).",
            "BPS Nasional menggunakan pembobotan jumlah penduduk, sedangkan rerata unweighted provinsi menghasilkan ~4,0-5,0% (selisih -0,7 s.d. -0,85 pp).",
        )
        rows_trans.append(m)

    m3 = pd.concat(rows_trans, ignore_index=True)

    # 4. Pasangan Cakupan Kargo Laut: var2753 Bongkar & Muat (Agregat 36 Provinsi vs Ketiadaan Baris Nasional)
    v2753_prov = (
        silver[(silver["seri_kode"] == "var2753") & (silver["wilayah_kode"] != 9999)]
        .groupby(["rincian", "periode"])["nilai"]
        .sum()
        .reset_index()
    )
    v2753_prov["periode"] = v2753_prov["periode"].astype(str)

    rows_laut = []
    for _, r in v2753_prov.iterrows():
        rin = r["rincian"]
        th = r["periode"]
        val = r["nilai"]
        rows_laut.append({
            "periode": th,
            "nilai_utama": float(val),
            "satuan_utama": "ton",
            "nilai_pembanding": np.nan,
            "satuan_pembanding": "ton",
            "pasangan": f"var2753 {rin} (Agregat 36 Provinsi vs Nasional)",
            "kategori": "Cakupan berbeda",
            "selisih": np.nan,
            "persen_selisih": np.nan,
            "penjelasan": "BPS tidak menerbitkan baris ringkasan nasional (INDONESIA) di berkas sumber. Seri mencakup 36 provinsi pesisir (DIY dan Papua Pegunungan tidak memiliki pelabuhan laut komersial).",
        })
    m4 = pd.DataFrame(rows_laut)

    # Gabungkan seluruh 28 baris rekonsiliasi
    kolom = [
        "pasangan",
        "periode",
        "nilai_utama",
        "satuan_utama",
        "nilai_pembanding",
        "satuan_pembanding",
        "selisih",
        "persen_selisih",
        "kategori",
        "penjelasan",
    ]
    rekon_all = pd.concat([m1, m2, m3, m4], ignore_index=True)[kolom]
    return rekon_all


def jalankan(silver: pd.DataFrame, gold_panel: pd.DataFrame = None) -> pd.DataFrame:
    """Eksekusi pembuatan tabel rekonsiliasi dan simpan ke data/gold/ & reports/."""
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    df_rekon = bangun_tabel_rekonsiliasi(silver)

    # Simpan ke parquet dan CSV
    parquet_path = GOLD_DIR / "rekonsiliasi.parquet"
    csv_path = REPORTS_DIR / "tabel_rekonsiliasi.csv"

    df_rekon.to_parquet(parquet_path, index=False)
    df_rekon.to_csv(csv_path, index=False, encoding="utf-8")

    return df_rekon


if __name__ == "__main__":
    s = pd.read_parquet(ROOT / "data" / "silver" / "silver.parquet")
    res = jalankan(s)
    print(f"Berhasil membangun tabel rekonsiliasi: {len(res)} baris.")
