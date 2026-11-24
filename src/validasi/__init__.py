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
from src.silver.katalog import satuan as satuan_katalog

ROOT = Path(__file__).resolve().parents[2]
LAPORAN = ROOT / "reports" / "validasi.md"


def _periksa_rentang(silver):
    salah = []

    # Nilai persen harus berada pada rentang 0-100.
    persen = silver["satuan"].eq("persen")
    luar = persen & ~silver["nilai"].between(0, 100)

    if luar.any():
        contoh = silver.loc[
            luar,
            ["seri_kode", "wilayah_kode", "periode", "nilai"]
        ].head(3)

        salah.append(
            f"{int(luar.sum())} nilai persen di luar 0-100, "
            f"misalnya {contoh.to_dict('records')}"
        )

    # Nilai berat bongkar muat tidak boleh negatif.
    berat = silver["satuan"].isin({"ton", "kilogram"})
    negatif = berat & (silver["nilai"] < 0)

    if negatif.any():
        salah.append(
            f"{int(negatif.sum())} nilai bongkar muat negatif"
        )

    return salah


def _periksa_satuan(silver):
    salah = []

    # Setiap seri harus menggunakan satuan sesuai katalog.
    for seri in silver["seri_kode"].unique():
        data_seri = silver[silver["seri_kode"] == seri]

        satuan_harapan = satuan_katalog(seri)
        satuan_aktual = data_seri["satuan"].dropna().unique()

        if len(satuan_aktual) != 1:
            salah.append(
                f"Seri {seri} memiliki satuan tidak seragam: "
                f"{list(satuan_aktual)}"
            )

        elif satuan_aktual[0] != satuan_harapan:
            salah.append(
                f"Seri {seri} memiliki satuan {satuan_aktual[0]}, "
                f"seharusnya {satuan_harapan}"
            )

    return salah


def _periksa_patahan(silver):
    salah = []

    if "penanda_patahan" not in silver.columns:
        return ["kolom penanda_patahan tidak ditemukan"]

    # Baris yang ditandai harus tepat merupakan var1241 tahun 2019.
    ditandai = silver["penanda_patahan"].eq("patahan_metodologi")

    seharusnya = (
        (silver["seri_kode"] == "var1241")
        & (silver["periode"].astype(str) == "2019")
    )

    if not seharusnya.any():
        salah.append(
            "baris var1241 tahun 2019 tidak ditemukan"
        )

    if not ditandai.equals(seharusnya):
        salah.append(
            "penanda patahan tidak sesuai dengan seri var1241 tahun 2019"
        )

    jumlah = int(ditandai.sum())

    if jumlah != 35:
        salah.append(
            f"jumlah baris berpatahan adalah {jumlah}, seharusnya 35"
        )

    return salah


def _periksa_gold(gold):
    salah = []

    panel_dasar = gold.get("panel_dasar")
    if panel_dasar is not None and not panel_dasar.empty:
        if panel_dasar.duplicated(KUNCI).any():
            salah.append("tabel dasar Gold punya kunci Silver kembar")
        if not {"kode_prov", "tingkat"}.issubset(panel_dasar.columns):
            salah.append("tabel dasar Gold tidak memuat kolom kode_prov dan tingkat")

    p = gold.get("panel")
    if p is not None and not p.empty:
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
    # Pemeriksaan skema dan lineage MANIFEST.
    salah_skema = []
    try:
        hasil_skema = periksa_silver(silver, baca_manifest())
        if hasil_skema:
            salah_skema.extend(hasil_skema)
    except Exception as exc:
        salah_skema.append(str(exc))

    # Pemeriksaan kunci unik.
    duplikat = silver.duplicated(KUNCI)
    salah_kunci = []
    if duplikat.any():
        salah_kunci.append(
            f"Ditemukan {int(duplikat.sum())} baris dengan kunci duplikat"
        )

    # Pemeriksaan rentang, satuan, patahan, dan Gold.
    salah_rentang = _periksa_rentang(silver)
    salah_satuan = _periksa_satuan(silver)
    salah_patahan = _periksa_patahan(silver)
    salah_gold = _periksa_gold(gold)

    # Mengumpulkan seluruh pelanggaran.
    pemeriksaan = {
        "Skema minimal dan lineage MANIFEST": salah_skema,
        "Keunikan kunci Silver": salah_kunci,
        "Rentang persen dan berat": salah_rentang,
        "Konsistensi satuan Silver": salah_satuan,
        "Penanda patahan metodologi": salah_patahan,
        "Integritas panel dan tabel dasar Gold": salah_gold,
    }

    semua_salah = []
    for nama, daftar_salah in pemeriksaan.items():
        for pesan in daftar_salah:
            semua_salah.append(f"{nama}: {pesan}")

    panel = gold.get("panel", pd.DataFrame())
    panel_dasar = gold.get("panel_dasar", pd.DataFrame())

    # Menyusun laporan validasi.
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
        f"- Baris patahan metodologi: {int(silver['penanda_patahan'].eq('patahan_metodologi').sum())}",
        f"- Hasil: {'LOLOS' if not semua_salah else 'GAGAL'}",
        "",
        "## Pemeriksaan",
        "",
        "| Pemeriksaan | Hasil |",
        "|---|---|",
    ]

    for nama, daftar_salah in pemeriksaan.items():
        hasil = "lolos" if not daftar_salah else "gagal"
        baris.append(f"| {nama} | {hasil} |")

    baris.append("")

    if semua_salah:
        baris.extend(["## Pelanggaran", ""])
        baris.extend(f"- {pesan}" for pesan in semua_salah)
        baris.append("")

    # Menyimpan laporan.
    LAPORAN.parent.mkdir(parents=True, exist_ok=True)
    LAPORAN.write_text("\n".join(baris), encoding="utf-8")

    if semua_salah:
        raise ValueError("Validasi gagal: " + "; ".join(semua_salah))

    print(f"Validasi: {len(silver)} baris Silver, {len(panel)} baris Panel Gold")
    print(f"Laporan: {LAPORAN}")

    return {
        "silver": len(silver),
        "gold_panel": len(panel),
        "gold_dasar": len(panel_dasar),
    }
