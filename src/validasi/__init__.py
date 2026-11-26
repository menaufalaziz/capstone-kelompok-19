
"""Tahap 8 — validasi minimum Silver, Gold, dan rekonsiliasi."""

from pathlib import Path
import pandas as pd

from src.common.manifest import baca as baca_manifest
from src.common.skema import KUNCI, periksa_silver
from src.silver.katalog import satuan as satuan_katalog

ROOT = Path(__file__).resolve().parents[2]
LAPORAN = ROOT / "reports" / "validasi.md"


# ATURAN SPRINT 1

def _periksa_rentang(silver):
    salah = []

    persen = silver["satuan"].eq("persen")
    luar = persen & ~silver["nilai"].between(0, 100)

    if luar.any():
        salah.append(f"{int(luar.sum())} nilai persen di luar 0-100")

    berat = silver["satuan"].isin({"ton", "kilogram"})
    negatif = berat & (silver["nilai"] < 0)

    if negatif.any():
        salah.append(f"{int(negatif.sum())} nilai berat negatif")

    return salah


def _periksa_satuan(silver):
    salah = []

    for seri in silver["seri_kode"].unique():
        data_seri = silver[silver["seri_kode"] == seri]
        harapan = satuan_katalog(seri)
        aktual = data_seri["satuan"].dropna().unique()

        if len(aktual) != 1:
            salah.append(
                f"Seri {seri} memiliki satuan tidak seragam: {list(aktual)}"
            )
        elif aktual[0] != harapan:
            salah.append(
                f"Seri {seri} memiliki satuan {aktual[0]}, "
                f"seharusnya {harapan}"
            )

    return salah


def _periksa_patahan(silver):
    salah = []

    if "penanda_patahan" not in silver.columns:
        return ["kolom penanda_patahan tidak ditemukan"]

    ditandai = silver["penanda_patahan"].eq("patahan_metodologi")

    seharusnya = (
        silver["seri_kode"].eq("var1241")
        & silver["periode"].astype(str).eq("2019")
    )

    if not seharusnya.any():
        salah.append("baris var1241 tahun 2019 tidak ditemukan")

    if not ditandai.equals(seharusnya):
        salah.append("penanda patahan tidak sesuai dengan var1241 tahun 2019")

    if int(ditandai.sum()) != 35:
        salah.append(
            f"jumlah baris berpatahan {int(ditandai.sum())}, seharusnya 35"
        )

    return salah


def _periksa_gold_dasar(gold):
    salah = []
    dasar = gold.get("panel_dasar")

    if dasar is None or dasar.empty:
        return ["tabel panel_dasar tidak ditemukan atau kosong"]

    if dasar.duplicated(KUNCI).any():
        salah.append("tabel dasar Gold memiliki kunci Silver duplikat")

    if not {"kode_prov", "tingkat"}.issubset(dasar.columns):
        salah.append("kolom kode_prov dan tingkat tidak ditemukan")

    return salah


# ATURAN SPRINT 2

def _periksa_kunci_panel(gold):
    salah = []
    panel = gold.get("panel")

    if panel is None or panel.empty:
        return ["panel Gold tidak ditemukan atau kosong"]

    kunci = ["indikator", "wilayah_kode", "periode"]

    if not set(kunci).issubset(panel.columns):
        return ["kolom kunci panel Gold tidak lengkap"]

    duplikat = panel.duplicated(kunci)

    if duplikat.any():
        salah.append(
            f"{int(duplikat.sum())} baris memiliki kunci panel duplikat"
        )

    return salah


def _periksa_satuan_panel(gold):
    salah = []
    panel = gold.get("panel")

    if panel is None or panel.empty:
        return ["panel Gold tidak ditemukan"]

    if not {"indikator", "satuan"}.issubset(panel.columns):
        return ["kolom indikator atau satuan tidak ditemukan"]

    jumlah_satuan = panel.groupby("indikator")["satuan"].nunique(
        dropna=False
    )

    tidak_seragam = jumlah_satuan[jumlah_satuan != 1]

    for indikator, jumlah in tidak_seragam.items():
        salah.append(
            f"Indikator {indikator} memiliki {jumlah} variasi satuan"
        )

    return salah


def _periksa_pasangan_silver(silver, gold):
    salah = []
    panel = gold.get("panel")

    if panel is None or panel.empty:
        return ["panel Gold tidak ditemukan"]

    kolom = ["seri_kode", "wilayah_kode", "periode", "rincian"]

    if not set(kolom + ["status_sel", "nilai"]).issubset(panel.columns):
        return ["kolom pencocokan Silver-Gold tidak lengkap"]

    if not set(kolom).issubset(silver.columns):
        return ["kolom kunci pencocokan Silver tidak lengkap"]

    # Hanya sel terisi yang wajib memiliki pasangan observasi Silver.
    terisi = panel[
        panel["status_sel"].eq("terisi") & panel["nilai"].notna()
    ]

    kunci_silver = set(
        map(
            tuple,
            silver[kolom].astype(str).to_numpy()
        )
    )

    kunci_gold = terisi[kolom].astype(str)

    cocok = kunci_gold.apply(
        lambda baris: tuple(baris) in kunci_silver,
        axis=1
    )

    jumlah_tidak_cocok = int((~cocok).sum())

    if jumlah_tidak_cocok:
        salah.append(
            f"{jumlah_tidak_cocok} sel Gold terisi tidak memiliki "
            "pasangan di Silver"
        )

    return salah


def _periksa_kategori_rekonsiliasi(gold):
    salah = []
    rekon = gold.get("rekonsiliasi")

    if rekon is None or rekon.empty:
        return ["tabel rekonsiliasi tidak ditemukan atau kosong"]

    if not {"pasangan", "kategori"}.issubset(rekon.columns):
        return ["kolom pasangan atau kategori tidak ditemukan"]

    # Baris yang memiliki pasangan wajib mempunyai kategori.
    berpasangan = (
        rekon["pasangan"].notna()
        & rekon["pasangan"].astype(str).str.strip().ne("")
    )

    kategori_kosong = (
        rekon["kategori"].isna()
        | rekon["kategori"].astype(str).str.strip().eq("")
    )

    tanpa_kategori = berpasangan & kategori_kosong

    if tanpa_kategori.any():
        salah.append(
            f"{int(tanpa_kategori.sum())} baris rekonsiliasi berpasangan "
            "tidak memiliki kategori"
        )

    return salah


def _periksa_status_panel(gold):
    salah = []
    panel = gold.get("panel")

    if panel is None or panel.empty:
        return ["panel Gold tidak ditemukan"]

    status_sah = {
        "terisi",
        "missing",
        "tidak_diterbitkan",
        "belum_ada",
        "batas_lama",
    }

    luar_status = ~panel["status_sel"].isin(status_sah)

    if luar_status.any():
        salah.append(
            f"{int(luar_status.sum())} baris memiliki status_sel tidak sah"
        )

    tidak_sinkron = (
        panel["status_sel"].eq("terisi") != panel["nilai"].notna()
    )

    if tidak_sinkron.any():
        salah.append(
            f"{int(tidak_sinkron.sum())} baris memiliki status_sel "
            "yang tidak sesuai dengan nilai"
        )

    return salah


# MENJALANKAN SELURUH VALIDASI

def jalankan(silver, gold):

    salah_skema = []
    try:
        hasil_skema = periksa_silver(silver, baca_manifest())
        if hasil_skema:
            salah_skema.extend(hasil_skema)
    except Exception as exc:
        salah_skema.append(str(exc))

    duplikat = silver.duplicated(KUNCI)
    salah_kunci = []

    if duplikat.any():
        salah_kunci.append(
            f"{int(duplikat.sum())} baris Silver memiliki kunci duplikat"
        )

    # Enam aturan Sprint 1.
    pemeriksaan = {
        "1. Skema minimal dan lineage MANIFEST": salah_skema,
        "2. Keunikan kunci Silver": salah_kunci,
        "3. Rentang persen dan berat": _periksa_rentang(silver),
        "4. Konsistensi satuan Silver": _periksa_satuan(silver),
        "5. Penanda patahan metodologi": _periksa_patahan(silver),
        "6. Integritas tabel dasar Gold": _periksa_gold_dasar(gold),

        # Empat aturan Sprint 2.
        "7. Keunikan kunci panel Gold": _periksa_kunci_panel(gold),
        "8. Konsistensi satuan per indikator Gold": _periksa_satuan_panel(gold),
        "9. Pasangan setiap sel Gold dengan Silver": _periksa_pasangan_silver(
            silver, gold
        ),
        "10. Kategori setiap pasangan rekonsiliasi": (
            _periksa_kategori_rekonsiliasi(gold)
        ),
    }

    # Pemeriksaan tambahan status sel panel.
    salah_status = _periksa_status_panel(gold)

    semua_salah = []

    for nama, daftar in pemeriksaan.items():
        for pesan in daftar:
            semua_salah.append(f"{nama}: {pesan}")

    for pesan in salah_status:
        semua_salah.append(f"Integritas status sel panel: {pesan}")

    panel = gold.get("panel", pd.DataFrame())
    panel_dasar = gold.get("panel_dasar", pd.DataFrame())
    rekon = gold.get("rekonsiliasi", pd.DataFrame())

    jumlah_lolos = sum(not daftar for daftar in pemeriksaan.values())

    baris = [
        "# Laporan validasi",
        "",
        "Dihasilkan otomatis oleh `python pipeline.py`.",
        "",
        "## Ringkasan",
        "",
        f"- Baris Silver: {len(silver):,}",
        f"- Baris Panel Gold: {len(panel):,}",
        f"- Baris Rekonsiliasi: {len(rekon):,}",
        f"- Aturan validasi: {len(pemeriksaan)}",
        f"- Aturan lolos: {jumlah_lolos}",
        f"- Hasil: {'LOLOS' if not semua_salah else 'GAGAL'}",
        "",
        "## Pemeriksaan",
        "",
        "| Pemeriksaan | Hasil |",
        "|---|---|",
    ]

    for nama, daftar in pemeriksaan.items():
        hasil = "LOLOS" if not daftar else "GAGAL"
        baris.append(f"| {nama} | {hasil} |")

    baris.append(
        f"| Integritas status sel panel | "
        f"{'LOLOS' if not salah_status else 'GAGAL'} |"
    )

    baris.append("")

    if semua_salah:
        baris.extend(["## Pelanggaran", ""])
        baris.extend(f"- {pesan}" for pesan in semua_salah)
        baris.append("")

    LAPORAN.parent.mkdir(parents=True, exist_ok=True)
    LAPORAN.write_text("\n".join(baris), encoding="utf-8")

    if semua_salah:
        raise ValueError(
            "Validasi gagal: " + "; ".join(semua_salah)
        )

    print(
        f"Validasi: {len(silver)} Silver, "
        f"{len(panel)} Panel Gold, {len(rekon)} Rekonsiliasi"
    )
    print(f"Aturan validasi: {len(pemeriksaan)}")
    print(f"Aturan lolos: {jumlah_lolos}")
    print(f"Laporan: {LAPORAN}")

    return {
        "silver": len(silver),
        "gold_panel": len(panel),
        "gold_dasar": len(panel_dasar),
        "rekonsiliasi": len(rekon),
        "aturan_validasi": len(pemeriksaan),
        "aturan_lolos": jumlah_lolos,
    }
