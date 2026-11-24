
"""Tahap 8 - validasi minimum Silver dan panel Gold provinsi.

Pemeriksaan meliputi skema, lineage MANIFEST, keunikan kunci, rentang nilai,
konsistensi satuan, penanda patahan, grid panel Gold, pemisahan kolom nilai
menurut satuan, dan lineage setiap sel Gold ke baris Silver asalnya.

Laporan ditulis ke reports/validasi.md setiap kali pipeline berjalan.
"""

from pathlib import Path

import numpy as np

from src.common.manifest import baca as baca_manifest
from src.common.skema import KUNCI, periksa_silver
from src.silver.katalog import satuan as satuan_katalog


ROOT = Path(__file__).resolve().parents[2]
LAPORAN = ROOT / "reports" / "validasi.md"

SERI_UTAMA = ("var1241", "var2012", "var2013", "var2753", "var2754")
KUNCI_PANEL = ["kode_prov", "periode", "indikator"]


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


def _provinsi_acuan(silver):
    """Kode provinsi dua digit yang harus ada pada grid Gold."""
    return (
        silver.loc[silver["wilayah_kode"] != 9999, "wilayah_kode"]
        .drop_duplicates()
        .floordiv(100)
        .sort_values()
        .tolist()
    )


def _periksa_lineage(panel, silver, nama):
    """Setiap sel terisi harus menunjuk baris Silver yang benar."""
    salah = []

    for kol in ("_baris_silver", "_kunci_silver"):
        if kol not in panel.columns:
            return [f"{nama}: kolom {kol} tidak ditemukan"]

    terisi = panel["_baris_silver"].notna()
    if not terisi.any():
        return [f"{nama}: tidak ada baris terisi untuk diperiksa lineage"]

    if panel.loc[terisi, "_kunci_silver"].isna().any():
        salah.append(f"{nama}: ada baris terisi tanpa _kunci_silver")

    idx = panel.loc[terisi, "_baris_silver"].astype("int64").to_numpy()
    if idx.min() < 0 or idx.max() >= len(silver):
        return [f"{nama}: _baris_silver di luar rentang Silver"]

    acuan = silver.reset_index(drop=True).iloc[idx].reset_index(drop=True)
    uji = panel.loc[terisi].reset_index(drop=True)

    for kol in (
        "seri_kode",
        "wilayah_kode",
        "periode",
        "rincian",
        "_berkas_raw",
        "_sha256_raw",
    ):
        if kol not in uji.columns:
            continue
        a = uji[kol].astype("string").fillna("<NA>")
        b = acuan[kol].astype("string").fillna("<NA>")
        beda = int((a != b).sum())
        if beda:
            salah.append(f"{nama}: {beda} baris {kol} tidak cocok dengan Silver")

    kunci_acuan = acuan[KUNCI].astype(str).agg("|".join, axis=1).astype("string")
    kunci_uji = uji["_kunci_silver"].astype("string").fillna("<NA>")
    beda = int((kunci_uji != kunci_acuan).sum())
    if beda:
        salah.append(f"{nama}: {beda} _kunci_silver tidak cocok dengan Silver")

    if "nilai_asli" in uji.columns:
        a = uji["nilai_asli"].astype(float).to_numpy()
        b = acuan["nilai"].astype(float).to_numpy()
        beda = int((~np.isclose(a, b, equal_nan=True)).sum())
        if beda:
            salah.append(f"{nama}: {beda} nilai_asli tidak sama dengan Silver")

    return salah


def _periksa_nilai_gabungan(panel, silver, nama):
    """Nilai panel gabungan harus sama dengan Silver setelah konversi satuan."""
    salah = []
    terisi = panel["_baris_silver"].notna()

    if not terisi.any():
        return salah

    idx = panel.loc[terisi, "_baris_silver"].astype("int64").to_numpy()
    acuan = silver.reset_index(drop=True).iloc[idx].reset_index(drop=True)
    uji = panel.loc[terisi].reset_index(drop=True)

    nilai = acuan["nilai"].astype(float).to_numpy()
    faktor = np.where(
        acuan["seri_kode"].astype(str).to_numpy() == "var2754", 0.001, 1.0
    )
    harapan = nilai * faktor

    satuan = uji["satuan"].astype(str).to_numpy()
    persen = satuan == "persen"
    ton = satuan == "ton"

    if persen.any():
        aktual = uji.loc[persen, "nilai_persen"].astype(float).to_numpy()
        beda = int((~np.isclose(aktual, harapan[persen], equal_nan=True)).sum())
        if beda:
            salah.append(f"{nama}: {beda} nilai_persen tidak sesuai Silver")

    if ton.any():
        aktual = uji.loc[ton, "nilai_ton"].astype(float).to_numpy()
        beda = int((~np.isclose(aktual, harapan[ton], equal_nan=True)).sum())
        if beda:
            salah.append(f"{nama}: {beda} nilai_ton tidak sesuai Silver")

        log_aktual = uji.loc[ton, "nilai_log10_ton"].astype(float).to_numpy()
        log_harapan = np.log10(harapan[ton])
        beda = int((~np.isclose(log_aktual, log_harapan, equal_nan=True)).sum())
        if beda:
            salah.append(f"{nama}: {beda} nilai_log10_ton tidak sesuai")

    return salah


def _periksa_panel_seri(panel, seri, silver):
    """Periksa satu tabel panel seri: kunci, grid, satuan, nilai, lineage."""
    nama = f"panel_{seri}"
    salah = []

    if panel is None or panel.empty:
        return [f"{nama}: kosong"]

    wajib = (
        "kode_prov",
        "periode",
        "indikator",
        "satuan",
        "nilai",
        "nilai_asli",
        "satuan_asli",
        "nilai_log10",
        "penanda_patahan",
        "_baris_silver",
        "_kunci_silver",
    )
    kurang = [kol for kol in wajib if kol not in panel.columns]
    if kurang:
        return [f"{nama}: kolom tidak lengkap {kurang}"]

    dup = int(panel.duplicated(KUNCI_PANEL).sum())
    if dup:
        salah.append(f"{nama}: {dup} baris kembar pada kunci {KUNCI_PANEL}")

    acuan_prov = set(_provinsi_acuan(silver))
    aktual_prov = set(panel["kode_prov"].dropna().astype(int))
    if aktual_prov != acuan_prov:
        salah.append(
            f"{nama}: provinsi tidak sama dengan grid 38 "
            f"(hilang {sorted(acuan_prov - aktual_prov)}, "
            f"lebih {sorted(aktual_prov - acuan_prov)})"
        )

    if not panel["periode"].astype(str).str.fullmatch(r"\d{4}").all():
        salah.append(f"{nama}: ada periode bukan tahun empat digit")

    rincian = sorted(
        silver.loc[
            (silver["seri_kode"] == seri) & (silver["wilayah_kode"] != 9999),
            "rincian",
        ]
        .astype(str)
        .unique()
    )
    periode_acuan = sorted(
        silver.loc[silver["seri_kode"] == seri, "periode"].astype(str).unique()
    )
    harap = len(acuan_prov) * len(periode_acuan) * len(rincian)
    if len(panel) != harap:
        salah.append(f"{nama}: {len(panel)} baris, seharusnya {harap}")

    if panel["indikator"].nunique() != len(rincian):
        salah.append(
            f"{nama}: {panel['indikator'].nunique()} indikator, "
            f"seharusnya {len(rincian)}"
        )

    satuan = set(panel["satuan"].dropna().astype(str))
    if len(satuan) != 1:
        salah.append(f"{nama}: satuan tidak seragam {sorted(satuan)}")
    else:
        unit = next(iter(satuan))
        nilai = panel["nilai"].astype(float)
        if unit not in {"persen", "ton"}:
            salah.append(f"{nama}: satuan Gold {unit!r} tidak dikenal")
        elif unit == "persen":
            luar = nilai.notna() & ~nilai.between(0, 100)
            if luar.any():
                salah.append(f"{nama}: {int(luar.sum())} nilai persen di luar 0-100")
        else:
            negatif = nilai.notna() & (nilai < 0)
            if negatif.any():
                salah.append(f"{nama}: {int(negatif.sum())} nilai ton negatif")
            log = panel["nilai_log10"].astype(float)
            kurang_log = nilai.notna() & log.isna()
            if kurang_log.any():
                salah.append(
                    f"{nama}: {int(kurang_log.sum())} nilai ton tanpa log10"
                )

    satuan_asli = set(panel["satuan_asli"].dropna().astype(str))
    harap_asli = set(
        silver.loc[silver["seri_kode"] == seri, "satuan"].dropna().astype(str)
    )
    if satuan_asli != harap_asli:
        salah.append(
            f"{nama}: satuan_asli {sorted(satuan_asli)} != Silver "
            f"{sorted(harap_asli)}"
        )

    terisi = panel["nilai"].notna()
    if terisi.any():
        nilai = panel.loc[terisi, "nilai"].astype(float).to_numpy()
        asli = panel.loc[terisi, "nilai_asli"].astype(float).to_numpy()
        faktor = 0.001 if seri == "var2754" else 1.0
        beda = int((~np.isclose(nilai, asli * faktor)).sum())
        if beda:
            salah.append(f"{nama}: {beda} nilai tidak sesuai konversi satuan")

    salah.extend(_periksa_lineage(panel, silver, nama))

    if seri == "var1241":
        patahan = panel["periode"].astype(str) == "2019"
        if not panel.loc[patahan, "penanda_patahan"].eq(
            "patahan_metodologi"
        ).all():
            salah.append(f"{nama}: penanda patahan 2019 tidak lengkap")
        if panel.loc[~patahan, "penanda_patahan"].ne("").any():
            salah.append(f"{nama}: ada penanda patahan di luar 2019")
    elif panel["penanda_patahan"].ne("").any():
        salah.append(f"{nama}: ada penanda patahan pada seri tanpa patahan")

    return salah


def _periksa_gabungan(panel, gold, silver):
    """Periksa panel long gabungan dan pemisahan kolom nilai per satuan."""
    nama = "panel_provinsi"
    salah = []

    if panel is None or panel.empty:
        return [f"{nama}: kosong"]

    wajib = (
        "kode_prov",
        "periode",
        "indikator",
        "satuan",
        "nilai_persen",
        "nilai_ton",
        "nilai_log10_ton",
        "penanda_patahan",
        "_baris_silver",
        "_kunci_silver",
    )
    kurang = [kol for kol in wajib if kol not in panel.columns]
    if kurang:
        return [f"{nama}: kolom tidak lengkap {kurang}"]

    dup = int(panel.duplicated(KUNCI_PANEL).sum())
    if dup:
        salah.append(f"{nama}: {dup} baris kembar pada kunci {KUNCI_PANEL}")

    acuan_prov = set(_provinsi_acuan(silver))
    aktual_prov = set(panel["kode_prov"].dropna().astype(int))
    if aktual_prov != acuan_prov:
        salah.append(f"{nama}: provinsi tidak sama dengan grid 38")

    panels = [gold.get(f"panel_{seri}") for seri in SERI_UTAMA]
    if all(p is not None for p in panels):
        harap = sum(len(p) for p in panels)
        if len(panel) != harap:
            salah.append(f"{nama}: {len(panel)} baris, jumlah panel seri {harap}")

    both = panel["nilai_persen"].notna() & panel["nilai_ton"].notna()
    if both.any():
        salah.append(
            f"{nama}: {int(both.sum())} baris punya nilai persen dan ton"
        )

    for indikator, bagian in panel.groupby("indikator"):
        satuan = set(bagian["satuan"].dropna().astype(str))
        if len(satuan) != 1:
            salah.append(
                f"{nama}/{indikator}: satuan tidak seragam {sorted(satuan)}"
            )
            continue

        unit = next(iter(satuan))
        if unit == "persen":
            if bagian["nilai_ton"].notna().any():
                salah.append(
                    f"{nama}/{indikator}: indikator persen punya nilai_ton"
                )
            nilai = bagian["nilai_persen"].dropna()
            if not nilai.between(0, 100).all():
                salah.append(
                    f"{nama}/{indikator}: nilai persen di luar 0-100"
                )
        elif unit == "ton":
            if bagian["nilai_persen"].notna().any():
                salah.append(
                    f"{nama}/{indikator}: indikator ton punya nilai_persen"
                )
            if bagian["nilai_ton"].dropna().lt(0).any():
                salah.append(f"{nama}/{indikator}: nilai ton negatif")
            log = bagian["nilai_log10_ton"].dropna()
            if not log.empty and not np.isfinite(log).all():
                salah.append(
                    f"{nama}/{indikator}: nilai log10 tidak hingga"
                )
        else:
            salah.append(f"{nama}/{indikator}: satuan {unit!r} tidak dikenal")

    kosong = panel["nilai_persen"].isna() & panel["nilai_ton"].isna()
    if int(kosong.sum()) != 72:
        salah.append(
            f"{nama}: {int(kosong.sum())} sel kosong, seharusnya 72"
        )

    salah.extend(_periksa_lineage(panel, silver, nama))
    salah.extend(_periksa_nilai_gabungan(panel, silver, nama))

    patahan = (panel["seri_kode"].astype(str) == "var1241") & (
        panel["periode"].astype(str) == "2019"
    )
    if not panel.loc[patahan, "penanda_patahan"].eq(
        "patahan_metodologi"
    ).all():
        salah.append(f"{nama}: penanda patahan var1241 2019 tidak lengkap")
    if panel.loc[~patahan, "penanda_patahan"].ne("").any():
        salah.append(f"{nama}: ada penanda patahan di luar var1241 2019")

    return salah


def _periksa_gold(gold, silver):
    salah = []

    panel = gold.get("panel_provinsi")
    if panel is None or panel.empty:
        return ["panel Gold provinsi kosong"]

    for seri in SERI_UTAMA:
        bagian = gold.get(f"panel_{seri}")
        if bagian is None or bagian.empty:
            salah.append(f"panel_{seri}: kosong")
        else:
            salah.extend(_periksa_panel_seri(bagian, seri, silver))

    salah.extend(_periksa_gabungan(panel, gold, silver))
    return salah


def _periksa_kompatibilitas(gold):
    """Periksa panel panjang/lebar/dasar yang dipakai laporan dan tes tim."""
    salah = []

    panel = gold.get("panel")
    lebar = gold.get("panel_lebar")
    dasar = gold.get("panel_dasar")

    if panel is None or panel.empty:
        return ["panel panjang kompatibilitas kosong"]

    kunci = ["indikator", "wilayah_kode", "periode"]
    if panel.duplicated(kunci).any():
        salah.append(
            f"panel panjang: {int(panel.duplicated(kunci).sum())} kunci kembar"
        )

    if len(panel) != 1330:
        salah.append(f"panel panjang: {len(panel)} baris, seharusnya 1.330")

    status_sah = {
        "terisi",
        "missing",
        "tidak_diterbitkan",
        "belum_ada",
        "batas_lama",
    }
    if not set(panel["status_sel"].dropna().unique()).issubset(status_sah):
        salah.append("panel panjang: status_sel di luar daftar baku")

    sinkron = (panel["status_sel"] == "terisi") == panel["nilai"].notna()
    if not sinkron.all():
        salah.append(
            f"panel panjang: {int((~sinkron).sum())} status_sel "
            "tidak sinkron dengan nilai"
        )

    satuan = panel.groupby("indikator")["satuan"].nunique()
    if (satuan != 1).any():
        salah.append("panel panjang: ada indikator dengan lebih dari satu satuan")

    if lebar is None or lebar.empty:
        salah.append("panel lebar kompatibilitas kosong")
    else:
        if lebar.duplicated(["wilayah_kode", "periode"]).any():
            salah.append("panel lebar: kunci wilayah-periode kembar")
        if lebar.shape != (394, 11):
            salah.append(
                f"panel lebar: bentuk {lebar.shape}, seharusnya (394, 11)"
            )

    if dasar is None or dasar.empty:
        salah.append("panel dasar kompatibilitas kosong")
    else:
        if dasar.duplicated(KUNCI).any():
            salah.append("panel dasar: kunci Silver kembar")
        if not {"kode_prov", "tingkat"}.issubset(dasar.columns):
            salah.append("panel dasar: kolom kode_prov/tingkat tidak ada")

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
    salah_gold = _periksa_gold(gold, silver)
    salah_kompatibilitas = _periksa_kompatibilitas(gold)

    # Mengumpulkan seluruh pelanggaran.
    pemeriksaan = {
        "Skema minimal dan lineage MANIFEST": salah_skema,
        "Keunikan kunci Silver": salah_kunci,
        "Rentang persen dan berat": salah_rentang,
        "Konsistensi satuan Silver": salah_satuan,
        "Penanda patahan metodologi": salah_patahan,
        "Panel Gold provinsi dan lineage": salah_gold,
        "Panel Gold panjang/lebar kompatibilitas": salah_kompatibilitas,
    }

    semua_salah = []

    for nama, daftar_salah in pemeriksaan.items():
        for pesan in daftar_salah:
            semua_salah.append(f"{nama}: {pesan}")

    panel_gold = gold.get("panel_provinsi")
    baris_gold = len(panel_gold) if panel_gold is not None else 0
    panel_kompat = gold.get("panel")
    baris_kompat = len(panel_kompat) if panel_kompat is not None else 0
    seri_panel = (
        panel_gold["seri_kode"].nunique()
        if panel_gold is not None and not panel_gold.empty
        else 0
    )
    indikator_gold = (
        panel_gold["indikator"].nunique()
        if panel_gold is not None and not panel_gold.empty
        else 0
    )
    sel_kosong_gold = (
        int(
            (
                panel_gold["nilai_persen"].isna()
                & panel_gold["nilai_ton"].isna()
            ).sum()
        )
        if panel_gold is not None and not panel_gold.empty
        else 0
    )
    patahan_gold = (
        int(panel_gold["penanda_patahan"].eq("patahan_metodologi").sum())
        if panel_gold is not None and not panel_gold.empty
        else 0
    )

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
        f"- Baris patahan metodologi: "
        f"{int(silver['penanda_patahan'].eq('patahan_metodologi').sum())}",
        f"- Baris panel Gold: {baris_gold:,}",
        f"- Baris panel panjang kompatibilitas: {baris_kompat:,}",
        f"- Seri panel Gold: {seri_panel}",
        f"- Indikator panel Gold: {indikator_gold}",
        f"- Sel kosong panel Gold: {sel_kosong_gold}",
        f"- Baris berpatahan panel Gold: {patahan_gold}",
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
        raise ValueError(
            "Validasi gagal: " + "; ".join(semua_salah)
        )

    print(
        f"Validasi: {len(silver)} baris Silver, "
        f"{baris_gold} baris panel Gold, {seri_panel} seri, "
        f"{indikator_gold} indikator"
    )
    print(f"Laporan: {LAPORAN}")

    return {
        "silver": len(silver),
        "gold": baris_gold,
        "seri_panel": seri_panel,
        "baris_gold": baris_gold,
    }
