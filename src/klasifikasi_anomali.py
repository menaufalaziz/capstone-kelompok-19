
import csv
from pathlib import Path

folder = Path("reports")
files = sorted(folder.glob("calon_anomali_var*.csv"))

alasan = {
    "2013": (
        "Nilai ekstrem berdasarkan deteksi IQR dan telah dicocokkan "
        "dengan JSON sumber BPS. Seluruh 4 kandidat sesuai dengan nilai "
        "sumber. Nilai tinggi juga muncul pada beberapa wilayah dan "
        "pengamatan. Tidak ditemukan bukti kesalahan input."
    ),
    "2753": (
        "Nilai ekstrem berdasarkan deteksi IQR dan telah dicocokkan "
        "dengan JSON/CSV sumber BPS. Seluruh 33 kandidat sesuai dengan "
        "nilai sumber. Nilai tinggi berulang pada wilayah tertentu "
        "selama periode pengamatan. Tidak ditemukan bukti kesalahan input."
    ),
    "2754": (
        "Nilai ekstrem berdasarkan deteksi IQR dan telah dicocokkan "
        "dengan CSV sumber BPS. Seluruh 48 kandidat sesuai dengan nilai "
        "sumber. Nilai tinggi berulang pada wilayah tertentu selama "
        "periode pengamatan. Tidak ditemukan bukti kesalahan input."
    )
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
            var = "".join(
                c for c in row.get("var_id", "") if c.isdigit()
            )

            row["kategori"] = "outlier asli"
            row["alasan_klasifikasi"] = alasan.get(
                var,
                "Belum tersedia alasan klasifikasi khusus."
            )
            row["tindakan"] = (
                "Dipertahankan; tidak dilakukan koreksi."
            )

            rows.append(row)

kolom += [
    "kategori",
    "alasan_klasifikasi",
    "tindakan"
]

output = folder / "klasifikasi_anomali.csv"

with output.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=kolom)
    writer.writeheader()
    writer.writerows(rows)

print(f"File dibuat: {output}")
print(f"Jumlah calon anomali diklasifikasikan: {len(rows)}")
