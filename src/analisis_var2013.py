
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

FILE_CSV = (
    ROOT / "data" / "raw" / "bps" / "2026-10-20"
    / "sdg11_11_2_1_b_v2013.csv"
)

REPORTS = ROOT / "reports"
GAMBAR = REPORTS / "gambar"

REPORTS.mkdir(exist_ok=True)
GAMBAR.mkdir(exist_ok=True)

# Membaca data
df = pd.read_csv(FILE_CSV)

print("DATA BERHASIL DIBACA")
print("Jumlah baris:", len(df))

print("\nNama kolom:")
print(df.columns.tolist())

print("\nLima data pertama:")
print(df.head())

# Memeriksa struktur data
print("\nINFORMASI DATA")
df.info()

print("\nJUMLAH DATA KOSONG")
print(df.isnull().sum())

print("\nJUMLAH WILAYAH")
print(df["wilayah"].nunique())

print("\nTAHUN PENGAMATAN")
print(sorted(df["tahun"].dropna().unique()))

# Statistik deskriptif keseluruhan
statistik = df["nilai"].describe()

statistik.to_csv(
    REPORTS / "profil_var2013_keseluruhan.csv"
)

print("\nSTATISTIK DESKRIPTIF")
print(statistik)

# Statistik deskriptif per wilayah
profil_wilayah = (
    df.groupby("wilayah")["nilai"]
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

profil_wilayah.to_csv(
    REPORTS / "profil_var2013_per_provinsi.csv",
    index=False
)

print("\nPROFIL PER WILAYAH")
print(profil_wilayah)

# Deteksi calon anomali menggunakan IQR per tahun
daftar_anomali = []

for tahun, kelompok in df.groupby("tahun"):

    Q1 = kelompok["nilai"].quantile(0.25)
    Q3 = kelompok["nilai"].quantile(0.75)

    IQR = Q3 - Q1

    batas_bawah = Q1 - 1.5 * IQR
    batas_atas = Q3 + 1.5 * IQR

    anomali = kelompok[
        (kelompok["nilai"] < batas_bawah) |
        (kelompok["nilai"] > batas_atas)
    ].copy()

    anomali["alasan"] = (
        "Nilai berada di luar batas IQR pada tahun yang sama"
    )

    daftar_anomali.append(anomali)

hasil_anomali = pd.concat(
    daftar_anomali,
    ignore_index=True
)

hasil_anomali.to_csv(
    REPORTS / "calon_anomali_var2013.csv",
    index=False
)

print("\nCALON ANOMALI")
print(hasil_anomali)

# Membuat boxplot per tahun
plt.figure(figsize=(8, 5))

df.boxplot(
    column="nilai",
    by="tahun",
    grid=False
)

plt.title("Boxplot Penggunaan Kendaraan Bermotor (var2013)")
plt.suptitle("")
plt.xlabel("Tahun")
plt.ylabel("Nilai indikator")
plt.tight_layout()

plt.savefig(
    GAMBAR / "boxplot_var2013_per_tahun.png",
    dpi=300
)

plt.close()

# Membuat grafik deret waktu per wilayah
plt.figure(figsize=(14, 7))

for wilayah, kelompok in df.groupby("wilayah"):

    kelompok = kelompok.sort_values("tahun")

    plt.plot(
        kelompok["tahun"],
        kelompok["nilai"],
        marker="o",
        linewidth=1,
        label=wilayah
    )

plt.title("Perubahan Penggunaan Kendaraan Bermotor per Wilayah (var2013)")
plt.xlabel("Tahun")
plt.ylabel("Nilai indikator")
plt.xticks(sorted(df["tahun"].dropna().unique()))

plt.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    fontsize=7
)

plt.tight_layout()

plt.savefig(
    GAMBAR / "timeseries_var2013_per_wilayah.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nANALISIS VAR2013 SELESAI")
print("File hasil analisis tersimpan di:", REPORTS)
print("Grafik tersimpan di:", GAMBAR)
