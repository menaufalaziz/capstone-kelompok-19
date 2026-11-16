
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Menentukan lokasi folder proyek
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "raw" / "bps" / "2026-10-20"
REPORTS = ROOT / "reports"
GAMBAR = REPORTS / "gambar"

REPORTS.mkdir(exist_ok=True)
GAMBAR.mkdir(exist_ok=True)

# Membaca data
file_csv = DATA / "sdg9_9_1_2_v2753.csv"
df = pd.read_csv(file_csv)

df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")

print("DATA BERHASIL DIBACA")
print("Jumlah baris:", len(df))
print("Kategori:", df["turvar"].unique())
print("Wilayah:", df["wilayah"].nunique())
print("Tahun:", sorted(df["tahun"].unique()))

# Memisahkan data Indonesia dan provinsi
provinsi = df[
    df["wilayah"].str.upper() != "INDONESIA"
].copy()

# Profil keseluruhan berdasarkan jenis kegiatan
profil_keseluruhan = (
    df.groupby("turvar")["nilai"]
    .describe()
    .reset_index()
)

profil_keseluruhan.to_csv(
    REPORTS / "profil_var2753_keseluruhan.csv",
    index=False
)

# Profil setiap provinsi berdasarkan jenis kegiatan
profil_provinsi = (
    provinsi.groupby(["wilayah", "turvar"])["nilai"]
    .agg(
        jumlah_data="count",
        rata_rata="mean",
        median="median",
        minimum="min",
        maksimum="max",
        standar_deviasi="std"
    )
    .reset_index()
)

profil_provinsi.to_csv(
    REPORTS / "profil_var2753_per_provinsi.csv",
    index=False
)

# Deteksi calon anomali menggunakan IQR
daftar_anomali = []

for jenis in provinsi["turvar"].dropna().unique():
    for tahun in sorted(provinsi["tahun"].dropna().unique()):
        kelompok = provinsi[
            (provinsi["turvar"] == jenis) &
            (provinsi["tahun"] == tahun)
        ].copy()

        q1 = kelompok["nilai"].quantile(0.25)
        q3 = kelompok["nilai"].quantile(0.75)
        iqr = q3 - q1

        batas_bawah = q1 - 1.5 * iqr
        batas_atas = q3 + 1.5 * iqr

        calon = kelompok[
            (kelompok["nilai"] < batas_bawah) |
            (kelompok["nilai"] > batas_atas)
        ].copy()

        if not calon.empty:
            calon["batas_bawah"] = batas_bawah
            calon["batas_atas"] = batas_atas
            calon["alasan"] = "Nilai berada di luar batas IQR"
            daftar_anomali.append(calon)

if daftar_anomali:
    hasil_anomali = pd.concat(daftar_anomali, ignore_index=True)
else:
    hasil_anomali = pd.DataFrame(
        columns=[
            "wilayah", "turvar", "tahun", "nilai",
            "batas_bawah", "batas_atas", "alasan"
        ]
    )

hasil_anomali.to_csv(
    REPORTS / "calon_anomali_var2753.csv",
    index=False
)

# Membuat grafik terpisah untuk Bongkar dan Muat
for jenis in provinsi["turvar"].dropna().unique():
    data_jenis = provinsi[
        provinsi["turvar"] == jenis
    ].copy()

    nama_jenis = str(jenis).lower().replace(" ", "_")

    # Boxplot per tahun
    plt.figure(figsize=(10, 6))
    data_jenis.boxplot(
        column="nilai",
        by="tahun",
        grid=False
    )
    plt.title(f"Boxplot {jenis} per Tahun - Var2753")
    plt.suptitle("")
    plt.xlabel("Tahun")
    plt.ylabel("Nilai (KG)")
    plt.tight_layout()
    plt.savefig(
        GAMBAR / f"boxplot_var2753_{nama_jenis}_per_tahun.png"
    )
    plt.close()

    # Grafik deret waktu per provinsi
    plt.figure(figsize=(12, 7))

    for wilayah, kelompok in data_jenis.groupby("wilayah"):
        kelompok = kelompok.sort_values("tahun")
        plt.plot(
            kelompok["tahun"],
            kelompok["nilai"],
            marker="o",
            label=wilayah
        )

    plt.title(f"Deret Waktu {jenis} per Wilayah - Var2753")
    plt.xlabel("Tahun")
    plt.ylabel("Nilai (KG)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(
        GAMBAR / f"timeseries_var2753_{nama_jenis}_per_wilayah.png"
    )
    plt.close()

print("\nANALISIS VAR2753 SELESAI")
print("Jumlah calon anomali:", len(hasil_anomali))
print("Semua hasil disimpan di folder reports.")
