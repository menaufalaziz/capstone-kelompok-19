
import pandas as pd
from pathlib import Path

file_path = Path("data/raw/bps/2026-10-20/sdg9_9_1_2_v2754.csv")

df = pd.read_csv(file_path)

print("DATA BERHASIL DIBACA")
print("Jumlah baris:", len(df))

print("\nNama kolom:")
print(df.columns.tolist())

print("\nLima data pertama:")
print(df.head())

print("\nInformasi data:")
print(df.info())

print("\nStatistik deskriptif:")
print(df["nilai"].describe())

print("\nJumlah data kosong:")
print(df.isnull().sum())

print("\nKategori turvar:")
print(df["turvar"].value_counts(dropna=False))

print("\nTahun:")
print(sorted(df["tahun"].dropna().unique()))

print("\nSatuan:")
print(df["satuan"].value_counts(dropna=False))


from pathlib import Path

output_dir = Path("reports")
output_dir.mkdir(exist_ok=True)

# Statistik deskriptif keseluruhan berdasarkan kategori
profil_keseluruhan = df.groupby("turvar")["nilai"].describe()

print("\nSTATISTIK DESKRIPTIF KESELURUHAN:")
print(profil_keseluruhan)

profil_keseluruhan.to_csv(
    output_dir / "profil_var2754_keseluruhan.csv"
)

# Mengeluarkan data agregat Indonesia dari analisis per provinsi
df_provinsi = df[df["wilayah"].str.upper() != "INDONESIA"].copy()

# Statistik deskriptif per provinsi dan kategori
profil_provinsi = (
    df_provinsi.groupby(["wilayah", "turvar"])["nilai"]
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

print("\nPROFIL STATISTIK PER PROVINSI:")
print(profil_provinsi.to_string(index=False))

profil_provinsi.to_csv(
    output_dir / "profil_var2754_per_provinsi.csv",
    index=False
)

print("\nFILE PROFIL BERHASIL DISIMPAN DI FOLDER reports")


import matplotlib.pyplot as plt

gambar_dir = Path("reports/gambar")
gambar_dir.mkdir(parents=True, exist_ok=True)

# Membuat boxplot terpisah untuk setiap kategori
for kategori in ["Bongkar", "Muat"]:
    data_kategori = df_provinsi[df_provinsi["turvar"] == kategori]

    data_boxplot = [
        data_kategori[data_kategori["tahun"] == tahun]["nilai"]
        for tahun in sorted(data_kategori["tahun"].unique())
    ]

    plt.figure(figsize=(10, 6))
    plt.boxplot(
        data_boxplot,
        tick_labels=sorted(data_kategori["tahun"].unique())
    )
    plt.title(f"Boxplot {kategori} per Tahun - Var2754")
    plt.xlabel("Tahun")
    plt.ylabel("Nilai (KG)")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        gambar_dir / f"boxplot_var2754_{kategori.lower()}_per_tahun.png"
    )
    plt.close()


# Membuat grafik deret waktu terpisah untuk setiap kategori
for kategori in ["Bongkar", "Muat"]:
    data_kategori = df_provinsi[df_provinsi["turvar"] == kategori]

    plt.figure(figsize=(14, 8))

    for wilayah in sorted(data_kategori["wilayah"].unique()):
        data_wilayah = data_kategori[
            data_kategori["wilayah"] == wilayah
        ].sort_values("tahun")

        plt.plot(
            data_wilayah["tahun"],
            data_wilayah["nilai"],
            marker="o",
            label=wilayah
        )

    plt.title(f"Grafik Deret Waktu {kategori} per Wilayah - Var2754")
    plt.xlabel("Tahun")
    plt.ylabel("Nilai (KG)")
    plt.xticks(sorted(data_kategori["tahun"].unique()))
    plt.grid(alpha=0.3)
    plt.legend(
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        fontsize=7
    )
    plt.tight_layout()

    plt.savefig(
        gambar_dir / f"timeseries_var2754_{kategori.lower()}_per_wilayah.png"
    )
    plt.close()

print("\nSEMUA GRAFIK VAR2754 BERHASIL DISIMPAN")


print("\nPEMERIKSAAN POLA GRAFIK")

for kategori in ["Bongkar", "Muat"]:
    data_kategori = df_provinsi[
        df_provinsi["turvar"] == kategori
    ]

    print(f"\nKATEGORI: {kategori}")

    print("\nRATA-RATA NILAI PER TAHUN:")
    print(
        data_kategori.groupby("tahun")["nilai"]
        .mean()
        .round(2)
    )

    print("\nWILAYAH DENGAN NILAI TERTINGGI PER TAHUN:")
    print(
        data_kategori.loc[
            data_kategori.groupby("tahun")["nilai"].idxmax(),
            ["tahun", "wilayah", "nilai"]
        ].to_string(index=False)
    )

    print("\nWILAYAH DENGAN NILAI TERENDAH PER TAHUN:")
    print(
        data_kategori.loc[
            data_kategori.groupby("tahun")["nilai"].idxmin(),
            ["tahun", "wilayah", "nilai"]
        ].to_string(index=False)
    )

print("\nDETEKSI CALON ANOMALI MENGGUNAKAN IQR")

hasil_anomali = []

for kategori in ["Bongkar", "Muat"]:
    for tahun in sorted(df_provinsi["tahun"].unique()):

        data = df_provinsi[
            (df_provinsi["turvar"] == kategori) &
            (df_provinsi["tahun"] == tahun)
        ].copy()

        Q1 = data["nilai"].quantile(0.25)
        Q3 = data["nilai"].quantile(0.75)
        IQR = Q3 - Q1

        batas_bawah = Q1 - 1.5 * IQR
        batas_atas = Q3 + 1.5 * IQR

        anomali = data[
            (data["nilai"] < batas_bawah) |
            (data["nilai"] > batas_atas)
        ].copy()

        anomali["batas_bawah"] = batas_bawah
        anomali["batas_atas"] = batas_atas

        hasil_anomali.append(anomali)

        print(f"\nKategori: {kategori} | Tahun: {tahun}")
        print("Jumlah calon anomali:", len(anomali))

        if len(anomali) > 0:
            print(
                anomali[["wilayah", "nilai"]]
                .to_string(index=False)
            )

if hasil_anomali:
    hasil_anomali = pd.concat(hasil_anomali, ignore_index=True)
else:
    hasil_anomali = pd.DataFrame()

hasil_anomali.to_csv(
    output_dir / "calon_anomali_var2754.csv",
    index=False
)

print("\nJumlah seluruh calon anomali:", len(hasil_anomali))
print("Hasil deteksi disimpan di reports/calon_anomali_var2754.csv")
