"""Tahap 4–6 — fondasi Gold (pertemuan VII, IX, XI, XII). Milik tim.

Sprint 1 menyimpan tabel dasar dari Silver apa adanya: semua rincian (termasuk
Bongkar/Muat) dan agregat nasional tetap menjadi baris. Pemilihan rincian yang
sebanding, grid 38 provinsi, rekonsiliasi pembanding, dan tabel Gold final
dikerjakan pada Sprint 2.

Keluaran: data/gold/panel_dasar.parquet.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "gold"


def jalankan(silver):
    """Terima Silver, simpan tabel dasar, kembalikan {nama_tabel: DataFrame}."""
    panel = silver.copy()
    panel["kode_prov"] = panel["wilayah_kode"] // 100
    panel["tingkat"] = panel["wilayah_kode"].map(
        lambda kode: "nasional" if kode == 9999 else "provinsi"
    )

    OUTPUT.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(OUTPUT / "panel_dasar.parquet", index=False)

    print(f"Gold dasar: {len(panel)} baris -> {OUTPUT / 'panel_dasar.parquet'}")
    print("Pemilihan rincian sebanding dan grid panel dikerjakan Sprint 2.")
    return {"panel_dasar": panel}
