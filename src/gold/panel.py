"""Tahap 4 — Panel Gold provinsi x periode x indikator.

Komponen: Profil dan Pembersihan / Persiapan Gold (Riska Erlis / NIM 124450022).

Aturan satu nilai per sel:
1. Snapshot: seri BPS yang terbit di dua snapshot memakai snapshot terbaru (2026-10-20);
   angka snapshot lama dibandingkan per kunci (K-008, K-018).
2. Rincian: indikator panel memuat 7 indikator utama tingkat provinsi:
   - var1241 (persen rumah tangga memiliki akses hunian layak, rincian 'Tidak ada')
   - var2012 (persen rumah tangga akses nyaman transportasi umum, rincian 'Tidak ada')
   - var2013 (persen penduduk 10+ menggunakan kendaraan umum, rincian 'Tidak ada')
   - var2753 [Bongkar] (bongkar kargo moda kapal, rincian 'Bongkar', satuan 'ton')
   - var2753 [Muat] (muat kargo moda kapal, rincian 'Muat', satuan 'ton')
   - var2754 [Bongkar] (bongkar kargo moda pesawat, rincian 'Bongkar', satuan 'kilogram')
   - var2754 [Muat] (muat kargo moda pesawat, rincian 'Muat', satuan 'kilogram')
   Baris agregat nasional (wilayah_kode 9999, 25 baris BPS) dan pembanding WDI (12 baris)
   tetap berada di Silver untuk tabel nasional Gold; 37 baris Silver tidak masuk panel provinsi.
   Seluruh 1.258 baris observasi provinsi di Silver terpilih masuk ke panel (0 baris provinsi tidak terpilih).
3. Periode: seluruh seri berperiode tahunan (4 digit YYYY); jenis_periode diisi 'tahun';
   disimpan apa adanya tanpa perataan artifisial dan tanpa interpolasi pada tahun kosong.
4. Penanda: penanda patahan metodologi (var1241 tahun 2019), patahan wilayah (Papua 2024),
   dan outlier asli (85 baris dari reports/klasifikasi_anomali.csv) dari Sprint 1
   dibawa ke kolom `penanda`; nilai asli sama sekali tidak diubah.
5. Skala dan transformasi bongkar muat: nilai asli kargo tetap disimpan di kolom `nilai`
   (ton untuk kapal, kg untuk pesawat); kolom turunan `nilai_log` ditambahkan dengan
   transformasi natural logaritma ln(1 + nilai) untuk memfasilitasi pemodelan tanpa merusak nilai asli.
6. Kelengkapan panel: panel memuat grid lengkap 38 provinsi x periode (1.330 sel: 1.258 terisi
   dan 72 sel kosong berkategori 'belum_ada', 'tidak_diterbitkan', 'batas_lama').

Keluaran:
- data/gold/panel.parquet (panjang, 1.330 baris)
- data/gold/panel_lebar.parquet (lebar, 394 baris x 11 kolom)
- reports/panel-gold.md (dokumentasi aturan dan status sel)
"""
from pathlib import Path
import numpy as np
import pandas as pd
from src.laporan import tabel_md

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "data" / "gold"
REPORTS = ROOT / "reports"

KOLOM_PANEL = [
    "indikator",
    "seri_kode",
    "rincian",
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "jenis_periode",
    "nilai",
    "satuan",
    "status_sel",
    "penanda",
    "nilai_log",
    "_berkas_raw",
    "_sha256_raw",
]

# Susunan 38 provinsi standar BPS 2025
PROVINSI = {
    1100: "Aceh", 1200: "Sumatera Utara", 1300: "Sumatera Barat", 1400: "Riau",
    1500: "Jambi", 1600: "Sumatera Selatan", 1700: "Bengkulu", 1800: "Lampung",
    1900: "Kepulauan Bangka Belitung", 2100: "Kepulauan Riau", 3100: "DKI Jakarta",
    3200: "Jawa Barat", 3300: "Jawa Tengah", 3400: "DI Yogyakarta", 3500: "Jawa Timur",
    3600: "Banten", 5100: "Bali", 5200: "Nusa Tenggara Barat", 5300: "Nusa Tenggara Timur",
    6100: "Kalimantan Barat", 6200: "Kalimantan Tengah", 6300: "Kalimantan Selatan",
    6400: "Kalimantan Timur", 6500: "Kalimantan Utara", 7100: "Sulawesi Utara",
    7200: "Sulawesi Tengah", 7300: "Sulawesi Selatan", 7400: "Sulawesi Tenggara",
    7500: "Gorontalo", 7600: "Sulawesi Barat", 8100: "Maluku", 8200: "Maluku Utara",
    9100: "Papua Barat", 9200: "Papua Barat Daya", 9400: "Papua", 9500: "Papua Selatan",
    9600: "Papua Tengah", 9700: "Papua Pegunungan",
}

STATUS_SEL_SAH = ("terisi", "missing", "tidak_diterbitkan", "belum_ada", "batas_lama")

# 7 indikator panel provinsi terpilih
DEFINISI_INDIKATOR = [
    {"indikator": "var1241", "seri_kode": "var1241", "rincian": "Tidak ada", "satuan": "persen",
     "tahun": [str(t) for t in range(2015, 2026)]},
    {"indikator": "var2012", "seri_kode": "var2012", "rincian": "Tidak ada", "satuan": "persen",
     "tahun": ["2017", "2020"]},
    {"indikator": "var2013", "seri_kode": "var2013", "rincian": "Tidak ada", "satuan": "persen",
     "tahun": ["2017", "2020"]},
    {"indikator": "var2753 [Bongkar]", "seri_kode": "var2753", "rincian": "Bongkar", "satuan": "ton",
     "tahun": [str(t) for t in range(2021, 2026)]},
    {"indikator": "var2753 [Muat]", "seri_kode": "var2753", "rincian": "Muat", "satuan": "ton",
     "tahun": [str(t) for t in range(2021, 2026)]},
    {"indikator": "var2754 [Bongkar]", "seri_kode": "var2754", "rincian": "Bongkar", "satuan": "kilogram",
     "tahun": [str(t) for t in range(2021, 2026)]},
    {"indikator": "var2754 [Muat]", "seri_kode": "var2754", "rincian": "Muat", "satuan": "kilogram",
     "tahun": [str(t) for t in range(2021, 2026)]},
]


def pilih_snapshot(silver):
    """Pilih baris dengan snapshot terbaru (2026-10-20) bila terdapat multi-snapshot per sel."""
    if "_berkas_raw" not in silver.columns:
        return silver
    kunci_cek = ["seri_kode", "wilayah_kode", "periode", "rincian"]
    if silver.duplicated(kunci_cek).any():
        df = silver.copy()
        df["_skor_snapshot"] = df["_berkas_raw"].map(lambda b: 1 if "2026-10-20" in str(b) else 0)
        df = df.sort_values(by=["_skor_snapshot", "_berkas_raw"], ascending=[False, True])
        df = df.drop_duplicates(subset=kunci_cek, keep="first").drop(columns=["_skor_snapshot"])
        return df
    return silver


def saring_baris_provinsi(silver):
    """Saring observasi tingkat provinsi (wilayah_kode != 9999, sumber == 'bps').
    
    Baris nasional (wilayah_kode == 9999) dan pembanding WDI tetap berada di Silver
    untuk konsumsi tabel nasional Gold (tidak masuk panel provinsi Gold).
    """
    total_silver = len(silver)
    prov = silver[(silver["wilayah_kode"] != 9999) & (silver["sumber"] == "bps")].copy()
    tidak_terpilih = total_silver - len(prov)
    return prov, tidak_terpilih


def bentuk_deret_terisi(silver_prov):
    """Bentuk baris terisi panel Gold untuk 7 indikator terpilih."""
    daftar_bagian = []
    for d in DEFINISI_INDIKATOR:
        seri = d["seri_kode"]
        rinci = d["rincian"]
        ind = d["indikator"]
        sat = d["satuan"]

        kondisi = (silver_prov["seri_kode"] == seri)
        if rinci in {"Tidak ada", "total"}:
            kondisi = kondisi & silver_prov["rincian"].isin(["Tidak ada", "total"])
        elif rinci in {"Bongkar", "arus=bongkar"}:
            kondisi = kondisi & silver_prov["rincian"].isin(["Bongkar", "arus=bongkar"])
        elif rinci in {"Muat", "arus=muat"}:
            kondisi = kondisi & silver_prov["rincian"].isin(["Muat", "arus=muat"])

        bagian = silver_prov[kondisi].copy()
        bagian["indikator"] = ind
        bagian["rincian"] = rinci
        bagian["satuan"] = sat
        bagian["status_sel"] = "terisi"
        daftar_bagian.append(bagian)

    terisi = pd.concat(daftar_bagian, ignore_index=True)

    # Validasi kunci unik satu nilai per sel
    ganda = terisi[terisi.duplicated(["indikator", "wilayah_kode", "periode"], keep=False)]
    if len(ganda):
        raise ValueError(f"Gold: {len(ganda)} sel panel masih ganda sesudah aturan pemilihan rincian!")

    return terisi


def bentuk_grid_sel_kosong():
    """Bentuk 72 sel kosong panel Gold 38 provinsi berdasarkan fakta historis pemekaran dan cakupan."""
    baris_kosong = []

    # 1. var1241: 4 provinsi baru Papua (9200, 9500, 9600, 9700)
    for w in [9200, 9500, 9600, 9700]:
        # 2015-2022: provinsi belum terbentuk
        for th in range(2015, 2023):
            baris_kosong.append({
                "indikator": "var1241", "seri_kode": "var1241", "rincian": "Tidak ada",
                "wilayah_kode": w, "periode": str(th), "satuan": "persen",
                "status_sel": "belum_ada",
            })
        # 2023: UU pemekaran akhir 2022, namun publikasi BPS Susenas 2023 masih batas wilayah lama
        baris_kosong.append({
            "indikator": "var1241", "seri_kode": "var1241", "rincian": "Tidak ada",
            "wilayah_kode": w, "periode": "2023", "satuan": "persen",
            "status_sel": "batas_lama",
        })

    # 2. var2012 & var2013: 4 provinsi baru Papua pada tahun 2017 dan 2020 (belum ada)
    for ind in ["var2012", "var2013"]:
        for w in [9200, 9500, 9600, 9700]:
            for th in ["2017", "2020"]:
                baris_kosong.append({
                    "indikator": ind, "seri_kode": ind, "rincian": "Tidak ada",
                    "wilayah_kode": w, "periode": th, "satuan": "persen",
                    "status_sel": "belum_ada",
                })

    # 3. var2753 Bongkar & Muat:
    # DI Yogyakarta (3400) 2021-2025: tidak diterbitkan karena tidak ada pelabuhan laut komersial yang dicakup BPS
    # Papua Pegunungan (9700) 2021-2022: belum ada; 2023-2025: tidak diterbitkan karena wilayah terkurung daratan
    for ind, rinci in [("var2753 [Bongkar]", "Bongkar"), ("var2753 [Muat]", "Muat")]:
        for th in range(2021, 2026):
            baris_kosong.append({
                "indikator": ind, "seri_kode": "var2753", "rincian": rinci,
                "wilayah_kode": 3400, "periode": str(th), "satuan": "ton",
                "status_sel": "tidak_diterbitkan",
            })
        for th in range(2021, 2023):
            baris_kosong.append({
                "indikator": ind, "seri_kode": "var2753", "rincian": rinci,
                "wilayah_kode": 9700, "periode": str(th), "satuan": "ton",
                "status_sel": "belum_ada",
            })
        for th in range(2023, 2026):
            baris_kosong.append({
                "indikator": ind, "seri_kode": "var2753", "rincian": rinci,
                "wilayah_kode": 9700, "periode": str(th), "satuan": "ton",
                "status_sel": "tidak_diterbitkan",
            })

    kosong = pd.DataFrame(baris_kosong)
    kosong["nilai"] = np.nan
    kosong["jenis_periode"] = "tahun"
    kosong["nama_wilayah"] = kosong["wilayah_kode"].map(PROVINSI)
    kosong["_berkas_raw"] = None
    kosong["_sha256_raw"] = None
    return kosong


def muat_penanda_anomali():
    """Muat kamus penanda anomali dan patahan dari Sprint 1.
    
    Kunci kamus: (indikator, wilayah_kode, periode) -> penanda.
    """
    penanda = {}

    # 1. Patahan metodologi var1241 tahun 2019 (perubahan kriteria hunian layak dari 3 ke 4 kriteria)
    for w in PROVINSI:
        if w not in {9200, 9500, 9600, 9700}:
            penanda[("var1241", w, "2019")] = "patahan_seri"

    # 2. Patahan wilayah Papua (9400) tahun 2024 akibat pemekaran 4 provinsi baru
    penanda[("var1241", 9400, "2024")] = "patahan_wilayah"

    # 3. Muat anomali dari reports/klasifikasi_anomali.csv (85 outlier asli terkonfirmasi)
    jalur_anomali = REPORTS / "klasifikasi_anomali.csv"
    if jalur_anomali.exists() and jalur_anomali.stat().st_size > 1:
        ano = pd.read_csv(jalur_anomali)
        for _, r in ano.iterrows():
            seri = "var" + str(r["var_id"]).strip()
            w = int(r["wilayah_id"])
            th = str(r["tahun"]).strip()
            rinci = str(r["turvar"]).strip()

            if rinci in {"Tidak ada", "0", ""}:
                ind = seri
            else:
                ind = f"{seri} [{rinci}]"

            kat = str(r.get("kategori", "outlier")).strip()
            if kat == "outlier asli":
                kat = "outlier"

            penanda[(ind, w, th)] = kat

    # 4. Dukung juga reports/anomali.csv bila ada dari repo kunci
    jalur_kunci = REPORTS / "anomali.csv"
    if jalur_kunci.exists() and jalur_kunci.stat().st_size > 1:
        ano_k = pd.read_csv(jalur_kunci, dtype={"periode": str})
        for _, r in ano_k.iterrows():
            seri = str(r["seri_kode"]).strip()
            w = int(r["wilayah_kode"])
            th = str(r["periode"]).strip()
            kat = str(r["kategori"]).strip()
            ind = seri.replace("arus=bongkar", "Bongkar").replace("arus=muat", "Muat")
            penanda[(ind, w, th)] = kat

    return penanda


def hitung_transformasi(panel):
    """Hitung transformasi logaritma natural log1p(nilai) untuk seri berskala besar (bongkar muat).
    
    Nilai asli tetap utuh di kolom 'nilai'.
    """
    panel = panel.copy()
    kondisi_bongkar = panel["seri_kode"].isin(["var2753", "var2754"]) & panel["nilai"].notna()
    panel["nilai_log"] = np.nan
    panel.loc[kondisi_bongkar, "nilai_log"] = np.log1p(panel.loc[kondisi_bongkar, "nilai"].astype(float))
    return panel


def bangun_panel_lebar(panel):
    """Bentuk tabel panel lebar: wilayah_kode x periode, satu kolom per indikator."""
    terisi = panel[panel["status_sel"] == "terisi"].copy()
    lebar = (
        terisi.pivot_table(
            index=["wilayah_kode", "nama_wilayah", "jenis_periode", "periode"],
            columns="indikator",
            values="nilai",
            aggfunc="first",
        ).reset_index()
    )
    lebar.columns.name = None
    return lebar


def tulis_laporan_panel_gold(panel, lebar, tidak_terpilih):
    """Tulis laporan evaluasi panel Gold ke reports/panel-gold.md."""
    ringkas = (
        panel.assign(t=panel["status_sel"] == "terisi")
        .groupby(["indikator", "satuan"], as_index=False)
        .agg(
            periode=("periode", lambda s: f"{s.min()}–{s.max()}" if s.nunique() > 1 else s.min()),
            jumlah_periode=("periode", "nunique"),
            total_sel=("status_sel", "size"),
            terisi=("t", "sum"),
            ditandai=("penanda", lambda s: int(s.notna().sum())),
        )
    )

    status_tabel = (
        panel.pivot_table(
            index="indikator",
            columns="status_sel",
            values="wilayah_kode",
            aggfunc="size",
            fill_value=0,
        ).reset_index()
    )

    md_lines = [
        "# Panel Gold provinsi × periode × indikator",
        "",
        "Dihasilkan otomatis oleh `python pipeline.py` (`src/gold/panel.py`) untuk Sprint 2 (Tahap 4).",
        "Penanggung jawab komponen: **Riska Erlis (NIM: 124450022)** — Profil dan Pembersihan / Persiapan Gold.",
        "",
        "## Aturan satu nilai per sel",
        "",
        "1. **Snapshot**: seri yang tersedia di dua snapshot memakai snapshot terbaru (2026-10-20); data snapshot 17 Oktober 2026 byte-identik.",
        "2. **Rincian**: panel memuat 7 indikator tingkat provinsi terpilih (var1241, var2012, var2013, var2753 Bongkar/Muat, var2754 Bongkar/Muat). Baris agregat nasional (wilayah_kode 9999) dan pembanding WDI dialokasikan ke tabel nasional Gold.",
        f"   - Baris Silver yang tidak masuk panel provinsi: **{tidak_terpilih:,} baris** (seluruh 37 baris nasional/WDI).",
        "   - Baris Silver provinsi yang tidak terpilih: **0 baris** (100% dari 1.258 baris provinsi di Silver terpilih masuk ke panel).",
        "3. **Periode**: seluruh indikator bertipe tahunan; periode 4 digit disimpan apa adanya (`jenis_periode = 'tahun'`); tidak ada interpolasi pada tahun kosong.",
        "4. **Penanda**: penanda patahan metodologi (var1241 tahun 2019), patahan wilayah (Papua 2024), dan outlier asli (85 calon anomali terkonfirmasi) dari Sprint 1 dibawa ke kolom `penanda`; nilai asli tidak diubah.",
        "5. **Skala dan Transformasi**: nilai asli kargo dipertahankan pada kolom `nilai` (var2753 bersatuan ton, var2754 bersatuan kg). Kolom turunan `nilai_log` ditambahkan dengan transformasi natural logaritma `log1p(nilai)` untuk memudahkan pemodelan seri bermagnitudo besar.",
        "6. **Sel Kosong**: 72 sel kosong dipertahankan dengan kategori eksplisit (`belum_ada`, `tidak_diterbitkan`, `batas_lama`) untuk transparansi kelengkapan data.",
        "",
        "## Ringkasan Indikator Panel",
        "",
        tabel_md(ringkas),
        "",
        "## Distribusi Status Sel",
        "",
        tabel_md(status_tabel),
        "",
        "## Berkas Keluaran",
        "",
        f"- `data/gold/panel.parquet`: {len(panel):,} baris (panjang, 1.258 terisi + 72 kosong).",
        f"- `data/gold/panel_lebar.parquet`: {len(lebar):,} baris × {lebar.shape[1]} kolom (lebar wilayah × periode).",
        "",
    ]

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "panel-gold.md").write_text("\n".join(md_lines), encoding="utf-8")


def jalankan(silver):
    """Fungsi utama Tahap 4: susun panel Gold dari Silver.
    
    Dipanggil otomatis oleh pipeline.py.
    """
    silver_dedup = pilih_snapshot(silver)
    silver_prov, tidak_terpilih = saring_baris_provinsi(silver_dedup)

    # 1. Baris terisi
    df_terisi = bentuk_deret_terisi(silver_prov)

    # 2. Baris kosong
    df_kosong = bentuk_grid_sel_kosong()

    # 3. Gabungkan panel lengkap
    panel = pd.concat([df_terisi, df_kosong], ignore_index=True)
    panel["nama_wilayah"] = panel["wilayah_kode"].map(PROVINSI)
    panel["jenis_periode"] = "tahun"

    # 4. Pasang penanda anomali & patahan
    kamus_penanda = muat_penanda_anomali()
    panel["penanda"] = [
        kamus_penanda.get((ind, int(w), str(per)))
        for ind, w, per in zip(panel["indikator"], panel["wilayah_kode"], panel["periode"])
    ]

    # 5. Kolom transformasi logaritma
    panel = hitung_transformasi(panel)

    # 6. Susun dan urutkan kolom
    panel = panel[KOLOM_PANEL].sort_values(["indikator", "periode", "wilayah_kode"]).reset_index(drop=True)
    panel["wilayah_kode"] = panel["wilayah_kode"].astype(int)

    # 7. Simpan panel panjang dan panel lebar
    GOLD.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(GOLD / "panel.parquet", index=False)

    lebar = bangun_panel_lebar(panel)
    lebar.to_parquet(GOLD / "panel_lebar.parquet", index=False)

    # 8. Tulis laporan
    tulis_laporan_panel_gold(panel, lebar, tidak_terpilih)

    print(f"Panel Gold selesai: {len(panel)} baris ({len(df_terisi)} terisi, {len(df_kosong)} kosong)")
    print(f"Panel lebar: {len(lebar)} baris x {lebar.shape[1]} kolom")
    print(f"Baris Silver tidak terpilih ke panel provinsi: {tidak_terpilih} baris")

    return {
        "panel": panel,
        "panel_lebar": lebar,
        "silver_tidak_terpilih": tidak_terpilih,
    }


if __name__ == "__main__":
    from src.silver.bangun import bangun_silver
    s = bangun_silver()
    jalankan(s)
