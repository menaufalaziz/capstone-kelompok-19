"""Tahap 4–6 — fondasi Gold.

Komponen: Profil dan Pembersihan / Persiapan Gold (Riska Erlis / NIM 124450022).

Keluaran:
- data/gold/panel.parquet (panjang, 1.330 baris)
- data/gold/panel_lebar.parquet (lebar, 394 baris x 11 kolom)
- data/gold/panel_dasar.parquet (dasar, 1.295 baris untuk kompatibilitas)
- reports/panel-gold.md
"""
from pathlib import Path
from src.gold import panel

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "gold"


def jalankan(silver):
    """Jalankan pembentukan panel Gold dari data Silver."""
    hasil = panel.jalankan(silver)

    # Pertahankan panel_dasar untuk kompatibilitas dan audit lapis Bronze/Silver
    panel_dasar = silver.copy()
    panel_dasar["kode_prov"] = panel_dasar["wilayah_kode"] // 100
    panel_dasar["tingkat"] = panel_dasar["wilayah_kode"].map(
        lambda kode: "nasional" if kode == 9999 else "provinsi"
    )

    OUTPUT.mkdir(parents=True, exist_ok=True)
    panel_dasar.to_parquet(OUTPUT / "panel_dasar.parquet", index=False)
    hasil["panel_dasar"] = panel_dasar

    return hasil
