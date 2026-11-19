"""Tahap 8 — validasi minimum Silver dan tabel dasar Gold (pertemuan XIV–XV).

Pemeriksaan ini adalah lantai tambahan di atas src/common/skema.py: rentang nilai
per satuan, kelengkapan kolom, keunikan kunci, dan lineage ke MANIFEST.csv.
Laporan hasil ditulis ke reports/validasi.md setiap kali pipeline berjalan.
"""
from pathlib import Path

import pandas as pd

from src.common.manifest import baca as baca_manifest
from src.common.skema import KUNCI, periksa_silver

ROOT = Path(__file__).resolve().parents[2]
LAPORAN = ROOT / "reports" / "validasi.md"


def _periksa_rentang(silver):
    salah = []
    persen = silver["satuan"].eq("persen")
    luar = persen & ~silver["nilai"].between(0, 100)
    if luar.any():
        contoh = silver.loc[luar, ["seri_kode", "wilayah_kode", "periode", "nilai"]].head(3)
        salah.append(f"{int(luar.sum())} nilai persen di luar 0–100, mis. "
                     f"{contoh.to_dict('records')}")

    berat = silver["satuan"].isin({"ton", "kilogram"})
    negatif = berat & (silver["nilai"] < 0)
    if negatif.any():
        salah.append(f"{int(negatif.sum())} nilai berat negatif")
    return salah


def _periksa_gold(gold):
    salah = []
    panel = gold.get("panel_dasar")
    if panel is None or panel.empty:
        return ["tabel dasar Gold kosong"]
    if panel.duplicated(KUNCI).any():
        salah.append("tabel dasar Gold punya kunci Silver kembar")
    if not {"kode_prov", "tingkat"}.issubset(panel.columns):
        salah.append("tabel dasar Gold tidak memuat kolom kode_prov/tingkat")
    return salah


def jalankan(silver, gold):
    salah = list(periksa_silver(silver, baca_manifest()))
    salah.extend(_periksa_rentang(silver))
    salah.extend(_periksa_gold(gold))

    baris = [
        "# Laporan validasi",
        "",
        "Dihasilkan otomatis oleh `python pipeline.py` (tahap 8).",
        "",
        "## Ringkasan",
        "",
        f"- Baris Silver: {len(silver):,}",
        f"- Seri Silver: {silver['seri_kode'].nunique()}",
        f"- Wilayah Silver: {silver['wilayah_kode'].nunique()}",
        f"- Berkas sumber Silver: {silver['_berkas_raw'].nunique()}",
        f"- Hasil: {'LOLOS' if not salah else 'GAGAL'}",
        "",
        "## Pemeriksaan",
        "",
        "| Pemeriksaan | Hasil |",
        "|---|---|",
        f"| Skema minimal dan lineage MANIFEST | {'lolos' if not salah else 'periksa pesan di bawah'} |",
        f"| Kunci unik {', '.join(KUNCI)} | {'lolos' if not silver.duplicated(KUNCI).any() else 'gagal'} |",
        f"| Rentang persen 0–100 dan berat tidak negatif | {'lolos' if not _periksa_rentang(silver) else 'gagal'} |",
        f"| Tabel dasar Gold | {'lolos' if not _periksa_gold(gold) else 'gagal'} |",
        "",
    ]
    if salah:
        baris.extend(["## Pelanggaran", ""])
        baris.extend(f"- {pesan}" for pesan in salah)
        baris.append("")

    LAPORAN.parent.mkdir(parents=True, exist_ok=True)
    LAPORAN.write_text("\n".join(baris), encoding="utf-8")

    if salah:
        raise ValueError("validasi gagal: " + "; ".join(salah))

    print(f"Validasi: {len(silver)} baris Silver, {len(gold.get('panel_dasar', []))} baris Gold dasar")
    print(f"Laporan: {LAPORAN}")
    return {"silver": len(silver), "gold": len(gold.get("panel_dasar", []))}
