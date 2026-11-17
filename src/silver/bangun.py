from pathlib import Path

import pandas as pd

from src.common.manifest import sha256_raw
from src.common.skema import KOLOM, periksa_silver

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "bps" / "2026-10-20"
OUTPUT = ROOT / "data" / "silver" / "silver.parquet"

DATASETS = {
    1241: "sdg11_11_1_1_a_v1241.csv",
    2012: "sdg11_11_2_1_a_v2012.csv",
    2013: "sdg11_11_2_1_b_v2013.csv",
    2753: "sdg9_9_1_2_v2753.csv",
    2754: "sdg9_9_1_2_v2754.csv",
}

def bangun_silver():
    hasil = []

    for seri, nama_file in DATASETS.items():
        jalur = RAW / nama_file
        df = pd.read_csv(jalur, dtype={"tahun": str})

        for _, baris in df.iterrows():
            # Keputusan K-002: agregat nasional var2753 dikeluarkan.
            if seri == 2753 and int(baris["wilayah_id"]) == 9999:
                continue

            satuan = str(baris["satuan"]).strip()
            if not satuan or satuan.lower() == "nan":
                satuan = "Tidak dinyatakan dalam sumber"

            rincian = str(baris["turvar"]).strip()
            if not rincian or rincian.lower() == "nan":
                rincian = "Tidak ada"

            hasil.append({
                "sumber": "BPS",
                "seri_kode": str(seri),
                "wilayah_kode": int(baris["wilayah_id"]),
                "nama_wilayah": str(baris["wilayah"]).strip(),
                "periode": str(baris["tahun"]),
                "jenis_periode": "tahun",
                "rincian": rincian,
                "nilai": pd.to_numeric(baris["nilai"], errors="raise"),
                "satuan": satuan,
                "_berkas_raw": f"bps/2026-10-20/{nama_file}",
                "_sha256_raw": sha256_raw(
                    f"bps/2026-10-20/{nama_file}"
                ),
            })

    silver = pd.DataFrame(hasil, columns=KOLOM)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    silver.to_parquet(OUTPUT, index=False)

    periksa_silver(silver)

    print("Silver berhasil dibuat!")
    print(f"Lokasi: {OUTPUT}")
    print(f"Jumlah baris: {len(silver)}")
    print(f"Jumlah kolom: {len(silver.columns)}")

if __name__ == "__main__":
    bangun_silver()