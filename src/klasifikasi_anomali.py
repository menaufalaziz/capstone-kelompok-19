import csv
from pathlib import Path

folder = Path("reports")
files = sorted(folder.glob("calon_anomali_var*.csv"))

alasan = {
    "2013": "Nilai ekstrem dibandingkan provinsi lain, tetapi pola nilai tinggi muncul kembali pada wilayah tertentu. Nilai sesuai data sumber dan tidak ditemukan bukti salah input.",
    "2753": "Nilai ekstrem berdasarkan deteksi IQR dan muncul berulang pada wilayah tertentu. Tidak ditemukan lonjakan serentak antarprovinsi atau bukti salah input pada data sumber.",
    "2754": "Nilai ekstrem berdasarkan deteksi IQR dan pola nilai tinggi muncul berulang pada wilayah tertentu. Nilai sesuai data sumber dan tidak ditemukan bukti salah input. Riwayat alokasi wilayah Papua Pegunungan tetap perlu diperhatikan."
}

rows = []
kolom = []

for file in files:
    with file.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames:
            for col in reader.fieldnames:
                if col not in kolom:
                    kolom.append(col)

        for row in reader:
            var = row.get("var_id", "")
            var = "".join(c for c in var if c.isdigit())

            row["kategori"] = "outlier asli"
            row["alasan_klasifikasi"] = alasan.get(
                var,
                "Tidak ditemukan bukti yang cukup untuk menyatakan nilai sebagai galat input."
            )
            row["tindakan"] = "Dipertahankan; tidak dilakukan koreksi."
            rows.append(row)

kolom += ["kategori", "alasan_klasifikasi", "tindakan"]

output = folder / "klasifikasi_anomali.csv"
with output.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=kolom)
    writer.writeheader()
    writer.writerows(rows)

print(f"File dibuat: {output}")
print(f"Jumlah calon anomali diklasifikasikan: {len(rows)}")
