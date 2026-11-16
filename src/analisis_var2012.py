
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# 1. MENENTUKAN LOKASI FOLDER

ROOT = Path(__file__).resolve().parents[1]

FILE_CSV = (
    ROOT / "data" / "raw" / "bps" / "2026-10-20"
    / "sdg11_11_2_1_a_v2012.csv"
)

REPORTS = ROOT / "reports"
GAMBAR = REPORTS / "gambar"

REPORTS.mkdir(exist_ok=True)
GAMBAR.mkdir(exist_ok=True)


# 2. MEMBACA DATA

df = pd.read_csv(FILE_CSV)

print("DATA BERHASIL DIBACA")
print("Jumlah baris:", len(df))
print("\nNama kolom:")
print(df.columns.tolist())

print("\nLima data pertama:")
print(df.head())


# 3. MEMERIKSA STRUKTUR DATA

print("\nINFORMASI DATA")
print(df.info())

print("\nJUMLAH DATA KOSONG")
print(df.isnull().sum())

print("\nJUMLAH WILAYAH")
print(df["wilayah"].nunique())

print("\nTAHUN PENGAMATAN")
print(sorted(df["tahun"].dropna().unique()))


# 4. STATISTIK DESKRIPTIF KESELURUHAN

statistik = df["nilai"].describe()

statistik.to_csv(
    REPORTS / "profil_var2012_keseluruhan.csv"
)

print("\nSTATISTIK DESKRIPTIF")
print(statistik)


# 5. STATISTIK DESKRIPTIF PER PROVINSI

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
    REPORTS / "profil_var2012_per_provinsi.csv",
    index=False
)

print("\nPROFIL PER WILAYAH")
print(profil_wilayah)


# 6. DETEKSI CALON ANOMALI MENGGUNAKAN IQR

# Data hanya memiliki dua tahun pengamatan.
# Karena itu, IQR dihitung per tahun untuk
# membandingkan nilai antarwilayah pada tahun sama.

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

if daftar_anomali:
    hasil_anomali = pd.concat(
        daftar_anomali,
        ignore_index=True
    )
else:
    hasil_anomali = pd.DataFrame()

hasil_anomali.to_csv(
    REPORTS / "calon_anomali_var2012.csv",
    index=False
)

print("\nCALON ANOMALI")
print(hasil_anomali)


# 7. MEMBUAT BOXPLOT PER TAHUN

plt.figure(figsize=(8, 5))

df.boxplot(
    column="nilai",
    by="tahun",
    grid=False
)

plt.title("Boxplot Akses Transportasi Umum (var2012)")
plt.suptitle("")
plt.xlabel("Tahun")
plt.ylabel("Persentase (%)")
plt.tight_layout()

plt.savefig(
    GAMBAR / "boxplot_var2012_per_tahun.png",
    dpi=300
)

plt.close()


# 8. MEMBUAT GRAFIK DERET WAKTU

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

plt.title(
    "Perubahan Akses Transportasi Umum per Wilayah (var2012)"
)

plt.xlabel("Tahun")
plt.ylabel("Persentase (%)")
plt.xticks(sorted(df["tahun"].dropna().unique()))
plt.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    fontsize=7
)

plt.tight_layout()

plt.savefig(
    GAMBAR / "timeseries_var2012_per_wilayah.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# 9. MENAMPILKAN RINGKASAN
print("\n================================")
print("ANALISIS VAR2012 SELESAI")
print("================================")

print("File hasil analisis tersimpan di:", REPORTS)
print("Grafik tersimpan di:", GAMBAR)
