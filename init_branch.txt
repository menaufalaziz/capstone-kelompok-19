"""Tahap 8 — validasi minimum Silver dan tabel Gold (pertemuan XIV–XV).

Pemeriksaan ini adalah lantai tambahan di atas src/common/skema.py: rentang nilai
per satuan, kelengkapan kolom, keunikan kunci, dan lineage ke MANIFEST.csv,
serta keunikan kunci panel Gold dan konsistensi status sel.
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
    panel_dasar = gold.get("panel_dasar")
    if panel_dasar is not None and not panel_dasar.empty:
        if panel_dasar.duplicated(KUNCI).any():
            salah.append("tabel dasar Gold punya kunci Silver kembar")
        if not {"kode_prov", "tingkat"}.issubset(panel_dasar.columns):
            salah.append("tabel dasar Gold tidak memuat kolom kode_prov/tingkat")

    p = gold.get("panel")
    if p is None or p.empty:
        salah.append("tabel panel Gold kosong")
        return salah

    # 1. Kunci panel unik
    kunci_panel = ["indikator", "wilayah_kode", "periode"]
    if p.duplicated(kunci_panel).any():
        ganda = p[p.duplicated(kunci_panel, keep=False)]
        salah.append(f"{len(ganda)} baris kunci panel Gold kembar pada {kunci_panel}")

    # 2. Status sel baku dan sinkronisasi dengan nilai
    status_sah = {"terisi", "missing", "tidak_diterbitkan", "belum_ada", "batas_lama"}
    luar_status = ~p["status_sel"].isin(status_sah)
    if luar_status.any():
        salah.append(f"{int(luar_status.sum())} baris memiliki status_sel di luar daftar baku")

    tidak_sinkron = (p["status_sel"] == "terisi") != p["nilai"].notna()
    if tidak_sinkron.any():
        salah.append(f"{int(tidak_sinkron.sum())} baris status_sel != nilai (terisi harus bernilai, kosong harus NaN)")

    # 3. Satu satuan per indikator
    sat_unik = p.groupby("indikator")["satuan"].nunique()
    if (sat_unik != 1).any():
        salah.append("terdapat indikator yang memiliki lebih dari satu satuan")

    return salah


def jalankan(silver, gold):
    salah = list(periksa_silver(silver, baca_manifest()))
    salah.extend(_periksa_rentang(silver))
    salah.extend(_periksa_gold(gold))

    panel = gold.get("panel", pd.DataFrame())
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
        f"- Baris Panel Gold: {len(panel):,} (7 indikator, 38 provinsi)",
        f"- Hasil: {'LOLOS' if not salah else 'GAGAL'}",
        "",
        "## Pemeriksaan",
        "",
        "| Pemeriksaan | Hasil |",
        "|---|---|",
        f"| Skema minimal dan lineage MANIFEST | {'lolos' if not list(periksa_silver(silver, baca_manifest())) else 'gagal'} |",
        f"| Kunci unik Silver {', '.join(KUNCI)} | {'lolos' if not silver.duplicated(KUNCI).any() else 'gagal'} |",
        f"| Rentang persen 0–100 dan berat tidak negatif | {'lolos' if not _periksa_rentang(silver) else 'gagal'} |",
        f"| Integritas Panel Gold (kunci unik, status sel, satuan seragam) | {'lolos' if not _periksa_gold(gold) else 'gagal'} |",
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

    print(f"Validasi: {len(silver)} baris Silver, {len(panel)} baris Panel Gold")
    print(f"Laporan: {LAPORAN}")
    return {"silver": len(silver), "gold_panel": len(panel)}
