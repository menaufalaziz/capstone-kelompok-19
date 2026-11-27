
"""Modul Tahap 6 — Integrasi dan Rekonsiliasi Data.

Komponen: Profil dan Pembersihan / Analis Utama (NIM 124450022).

Fungsi modul:
1. Membandingkan:
   a. BPS var1241 dengan WDI EN.POP.SLUM.UR.ZS.
   b. Agregat kargo udara var2754 dengan baris nasional BPS.
   c. Rerata provinsi var2012 dan var2013 dengan baris nasional BPS.
   d. Agregat kargo laut var2753 dengan cakupan provinsi yang tersedia.
2. Mengklasifikasikan perbedaan berdasarkan definisi, metode,
   cakupan, vintage, atau kondisi yang belum terjelaskan.
3. Menyimpan hasil ke Parquet dan CSV.

NIM: 124450022
"""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
GOLD_DIR = ROOT / "data" / "gold"
REPORTS_DIR = ROOT / "reports"


def bangun_tabel_rekonsiliasi(silver: pd.DataFrame) -> pd.DataFrame:
    """Membangun tabel rekonsiliasi komprehensif dari data Silver."""

    # 1. BPS var1241 vs WDI EN.POP.SLUM.UR.ZS
    v1241_nas = (
        silver[
            (silver["seri_kode"] == "var1241")
            & (silver["wilayah_kode"] == 9999)
        ][["periode", "nilai", "satuan"]]
        .rename(
            columns={
                "nilai": "nilai_utama",
                "satuan": "satuan_utama",
            }
        )
        .copy()
    )
    v1241_nas["periode"] = v1241_nas["periode"].astype(str)

    wdi = (
        silver[
            silver["seri_kode"] == "EN.POP.SLUM.UR.ZS"
        ][["periode", "nilai", "satuan"]]
        .rename(
            columns={
                "nilai": "nilai_pembanding",
                "satuan": "satuan_pembanding",
            }
        )
        .copy()
    )
    wdi["periode"] = wdi["periode"].astype(str)

    m1 = pd.merge(v1241_nas, wdi, on="periode", how="inner")
    m1["pasangan"] = (
        "var1241 (BPS Nasional) vs WDI EN.POP.SLUM.UR.ZS"
    )
    m1["kategori"] = "Definisi berbeda"
    m1["selisih"] = (
        m1["nilai_utama"] - m1["nilai_pembanding"]
    )
    m1["persen_selisih"] = (
        m1["selisih"] / m1["nilai_pembanding"]
    ) * 100

    m1["penjelasan"] = m1["periode"].map({
        "2016": (
            "BPS mengukur persentase rumah tangga dengan hunian layak, "
            "sedangkan WDI mengukur persentase penduduk perkotaan "
            "yang tinggal di kawasan kumuh. Pada 2016–2018, BPS naik "
            "dari 94,00% menjadi 95,70% (+1,70 pp), sedangkan WDI "
            "turun dari 21,89% menjadi 20,24% (-1,65 pp). "
            "Keduanya memiliki arah perubahan berlawanan."
        ),
        "2018": (
            "BPS mencapai 95,70% dengan kriteria pengukuran "
            "periode 2015–2018, sedangkan WDI berada pada 20,24%. "
            "Kenaikan hunian layak searah secara konseptual dengan "
            "penurunan kawasan kumuh perkotaan."
        ),
        "2020": (
            "BPS turun menjadi 59,54% akibat patahan seri "
            "metodologi empat kriteria SDG (K-010). "
            "WDI turun tipis menjadi 19,41%. "
            "Perubahan BPS tidak dapat langsung dianggap sebagai "
            "penurunan kondisi hunian sebesar nilai selisih tersebut."
        ),
        "2022": (
            "BPS naik menjadi 60,66% setelah patahan seri, "
            "sedangkan WDI tetap pada 19,41% dalam data yang digunakan. "
            "Perbedaan tetap dipengaruhi oleh definisi dan cakupan "
            "indikator yang tidak sama."
        ),
    })

    # 2. Agregat provinsi var2754 vs BPS Nasional
    v2754_nas = (
        silver[
            (silver["seri_kode"] == "var2754")
            & (silver["wilayah_kode"] == 9999)
        ][["rincian", "periode", "nilai", "satuan"]]
        .rename(
            columns={
                "nilai": "nilai_pembanding",
                "satuan": "satuan_pembanding",
            }
        )
        .copy()
    )
    v2754_nas["periode"] = v2754_nas["periode"].astype(str)

    v2754_prov = (
        silver[
            (silver["seri_kode"] == "var2754")
            & (silver["wilayah_kode"] != 9999)
        ]
        .groupby(["rincian", "periode"])["nilai"]
        .sum()
        .reset_index()
        .rename(columns={"nilai": "nilai_utama"})
    )
    v2754_prov["periode"] = v2754_prov["periode"].astype(str)
    v2754_prov["satuan_utama"] = "kilogram"

    m2 = pd.merge(
        v2754_prov,
        v2754_nas,
        on=["rincian", "periode"],
    )
    m2["pasangan"] = (
        "var2754 "
        + m2["rincian"]
        + " (Jumlah Provinsi vs BPS Nasional)"
    )
    m2["kategori"] = "Metode berbeda"
    m2["selisih"] = (
        m2["nilai_utama"] - m2["nilai_pembanding"]
    )
    m2["persen_selisih"] = (
        m2["selisih"] / m2["nilai_pembanding"]
    ) * 100

    m2["penjelasan"] = np.where(
        m2["periode"] == "2023",
        (
            "Agregat provinsi sama dengan angka nasional BPS "
            "(selisih 0 kg)."
        ),
        (
            "Selisih kecil pada agregat provinsi dan angka nasional "
            "BPS diduga berkaitan dengan pembulatan angka nasional "
            "pada berkas sumber, sedangkan agregat provinsi "
            "dihitung dari penjumlahan nilai provinsi."
        ),
    )
    m2 = m2.drop(columns=["rincian"])

    # 3. Rerata provinsi var2012 dan var2013 vs BPS Nasional
    rows_trans = []

    for vk, nama in [
        (
            "var2012",
            "var2012 Moda Transportasi "
            "(Rerata Provinsi vs BPS Nasional)",
        ),
        (
            "var2013",
            "var2013 Kemacetan/Angkutan "
            "(Rerata Provinsi vs BPS Nasional)",
        ),
    ]:
        nas = (
            silver[
                (silver["seri_kode"] == vk)
                & (silver["wilayah_kode"] == 9999)
            ][["periode", "nilai", "satuan"]]
            .rename(
                columns={
                    "nilai": "nilai_pembanding",
                    "satuan": "satuan_pembanding",
                }
            )
            .copy()
        )
        nas["periode"] = nas["periode"].astype(str)

        prov = (
            silver[
                (silver["seri_kode"] == vk)
                & (silver["wilayah_kode"] != 9999)
            ]
            .groupby("periode")["nilai"]
            .mean()
            .reset_index()
            .rename(columns={"nilai": "nilai_utama"})
        )
        prov["periode"] = prov["periode"].astype(str)
        prov["satuan_utama"] = "persen"

        m = pd.merge(prov, nas, on="periode")
        m["pasangan"] = nama
        m["kategori"] = "Metode berbeda"
        m["selisih"] = (
            m["nilai_utama"] - m["nilai_pembanding"]
        )
        m["persen_selisih"] = (
            m["selisih"] / m["nilai_pembanding"]
        ) * 100

        if vk == "var2012":
            m["penjelasan"] = (
                "Rerata provinsi dihitung tanpa pembobotan "
                "(unweighted), sedangkan angka nasional BPS "
                "menggunakan pembobotan sesuai metode agregasi "
                "indikator. Perbedaan metode menghasilkan "
                "selisih sekitar 3,2–3,3 poin persentase."
            )
        else:
            m["penjelasan"] = (
                "Rerata provinsi dihitung tanpa pembobotan "
                "(unweighted), sedangkan angka nasional BPS "
                "menggunakan pembobotan sesuai metode agregasi "
                "indikator. Rerata provinsi menghasilkan nilai "
                "sekitar 4,0–5,0% dan berbeda dari angka nasional."
            )

        rows_trans.append(m)

    m3 = pd.concat(rows_trans, ignore_index=True)

    # 4. Agregat kargo laut var2753: cakupan 36 provinsi
    v2753_prov = (
        silver[
            (silver["seri_kode"] == "var2753")
            & (silver["wilayah_kode"] != 9999)
        ]
        .groupby(["rincian", "periode"])["nilai"]
        .sum()
        .reset_index()
    )
    v2753_prov["periode"] = v2753_prov["periode"].astype(str)

    rows_laut = []

    for _, r in v2753_prov.iterrows():
        rincian = r["rincian"]
        periode = r["periode"]
        nilai = r["nilai"]

        rows_laut.append({
            "periode": periode,
            "nilai_utama": float(nilai),
            "satuan_utama": "ton",
            "nilai_pembanding": np.nan,
            "satuan_pembanding": "ton",
            "pasangan": (
                f"var2753 {rincian} "
                "(Agregat 36 Provinsi vs Nasional)"
            ),
            "kategori": "Cakupan berbeda",
            "selisih": np.nan,
            "persen_selisih": np.nan,
            "penjelasan": (
                "BPS tidak menerbitkan baris ringkasan nasional "
                "(INDONESIA) pada berkas sumber. Agregat dihitung "
                "dari 36 provinsi yang memiliki data kargo laut. "
                "Karena pembanding nasional tidak tersedia, "
                "selisih numerik tidak dapat dihitung."
            ),
        })

    m4 = pd.DataFrame(rows_laut)

    # Gabungkan seluruh tabel rekonsiliasi
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

    rekon_all = pd.concat(
        [m1, m2, m3, m4],
        ignore_index=True,
    )[kolom]

    return rekon_all


def jalankan(
    silver: pd.DataFrame,
    gold_panel: pd.DataFrame = None,
) -> pd.DataFrame:
    """Membangun dan menyimpan tabel rekonsiliasi."""

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    df_rekon = bangun_tabel_rekonsiliasi(silver)

    parquet_path = GOLD_DIR / "rekonsiliasi.parquet"
    csv_path = REPORTS_DIR / "tabel_rekonsiliasi.csv"

    df_rekon.to_parquet(parquet_path, index=False)
    df_rekon.to_csv(
        csv_path,
        index=False,
        encoding="utf-8",
    )

    return df_rekon


if __name__ == "__main__":
    silver_path = ROOT / "data" / "silver" / "silver.parquet"

    silver = pd.read_parquet(silver_path)
    hasil = jalankan(silver)

    print(
        "Berhasil membangun tabel rekonsiliasi: "
        f"{len(hasil)} baris."
    )
