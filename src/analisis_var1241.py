# ANALISIS DESKRIPTIF DAN DETEKSI CALON ANOMALI VAR1241

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# 1. MENENTUKAN LOKASI FILE
# Mengambil folder utama project
ROOT = Path(__file__).resolve().parents[1]

# Lokasi file CSV
INPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "bps"
    / "2026-10-20"
    / "sdg11_11_1_1_a_v1241.csv"
)

# Lokasi penyimpanan hasil analisis
REPORT_DIR = ROOT / "reports"
IMAGE_DIR = REPORT_DIR / "gambar"

# Membuat folder jika belum tersedia
REPORT_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


# 2. MEMBACA DATA
df = pd.read_csv(INPUT_FILE)

# Memastikan kolom angka terbaca sebagai numerik
df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")
df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")

# Menghapus baris yang tidak memiliki nilai atau tahun
df = df.dropna(subset=["nilai", "tahun"])

print("DATA BERHASIL DIBACA")
print("Jumlah baris:", len(df))
print(df.head())


# 3. STATISTIK DESKRIPTIF KESELURUHAN

statistik_keseluruhan = df["nilai"].describe()

statistik_keseluruhan.to_csv(
    REPORT_DIR / "profil_var1241_keseluruhan.csv"
)

print("\nSTATISTIK DESKRIPTIF KESELURUHAN")
print(statistik_keseluruhan)


# 4. STATISTIK DESKRIPTIF PER PROVINSI
profil_provinsi = (
    df.groupby("wilayah")["nilai"]
    .agg(
        jumlah_data="count",
        rata_rata="mean",
        median="median",
        standar_deviasi="std",
        minimum="min",
        maksimum="max",
        Q1=lambda x: x.quantile(0.25),
        Q3=lambda x: x.quantile(0.75)
    )
    .reset_index()
)

profil_provinsi.to_csv(
    REPORT_DIR / "profil_var1241_per_provinsi.csv",
    index=False
)

print("\nSTATISTIK PER PROVINSI")
print(profil_provinsi)


# 5. DETEKSI CALON ANOMALI MENGGUNAKAN METODE IQR

def deteksi_anomali_iqr(grup):
    """
    Mendeteksi nilai yang berada di luar batas IQR
    untuk setiap wilayah.
    """

    # Minimal 4 data agar perhitungan kuartil lebih layak
    if len(grup) < 4:
        return pd.DataFrame()

    Q1 = grup["nilai"].quantile(0.25)
    Q3 = grup["nilai"].quantile(0.75)

    IQR = Q3 - Q1

    batas_bawah = Q1 - 1.5 * IQR
    batas_atas = Q3 + 1.5 * IQR

    anomali = grup[
        (grup["nilai"] < batas_bawah)
        | (grup["nilai"] > batas_atas)
    ].copy()

    anomali["Q1"] = Q1
    anomali["Q3"] = Q3
    anomali["IQR"] = IQR
    anomali["batas_bawah"] = batas_bawah
    anomali["batas_atas"] = batas_atas

    anomali["alasan"] = anomali["nilai"].apply(
        lambda x: (
            "Di bawah batas bawah IQR"
            if x < batas_bawah
            else "Di atas batas atas IQR"
        )
    )

    return anomali


daftar_anomali = []

for wilayah, grup in df.groupby("wilayah"):
    hasil = deteksi_anomali_iqr(grup)

    if not hasil.empty:
        daftar_anomali.append(hasil)

if daftar_anomali:
    calon_anomali = pd.concat(daftar_anomali)
else:
    calon_anomali = pd.DataFrame(
        columns=list(df.columns)
        + ["Q1", "Q3", "IQR", "batas_bawah",
           "batas_atas", "alasan"]
    )

calon_anomali.to_csv(
    REPORT_DIR / "calon_anomali_var1241.csv",
    index=False
)

print("\nCALON ANOMALI")
print(calon_anomali)


# 6. MEMBUAT BOXPLOT PER WILAYAH

plt.figure(figsize=(18, 8))

df.boxplot(
    column="nilai",
    by="wilayah",
    rot=90
)

plt.title("Boxplot Nilai Var1241 per Wilayah")
plt.suptitle("")
plt.xlabel("Wilayah")
plt.ylabel("Nilai (Persen)")
plt.tight_layout()

plt.savefig(
    IMAGE_DIR / "boxplot_var1241_per_wilayah.png",
    dpi=300
)

plt.close()


# 7. MEMBUAT GRAFIK DERET WAKTU
plt.figure(figsize=(16, 9))

for wilayah, grup in df.groupby("wilayah"):
    grup = grup.sort_values("tahun")

    plt.plot(
        grup["tahun"],
        grup["nilai"],
        marker="o",
        linewidth=1,
        label=wilayah
    )

plt.title("Deret Waktu Var1241 per Wilayah")
plt.xlabel("Tahun")
plt.ylabel("Nilai (Persen)")
plt.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    fontsize=7
)

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    IMAGE_DIR / "timeseries_var1241_per_wilayah.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()



# 8. RINGKASAN HASIL
print("\n====================================")
print("ANALISIS VAR1241 SELESAI")
print("====================================")

print("Jumlah data:", len(df))
print("Jumlah wilayah:", df["wilayah"].nunique())
print("Jumlah calon anomali:", len(calon_anomali))

print("\nFile hasil tersimpan di:")
print(REPORT_DIR)

print("\nGrafik tersimpan di:")
print(IMAGE_DIR)
