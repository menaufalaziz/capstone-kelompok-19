"""Katalog seri Kasus 19 — satuan dan kode SDG hasil audit berkas mentah.

Katalog awal di `data/KASUS.md` belum tentu benar. Setiap entri mencatat:

- klaim katalog awal: `satuan_katalog`, `kode_sdg_katalog`;
- nilai final yang dipakai Silver: `satuan`, `kode_sdg`;
- bukti sumber: `berkas_data`, `berkas_metadata`, `dasar_satuan`, `dasar_sdg`.

`perlu_log=True` berarti koreksi katalog wajib punya baris di `log-keputusan.csv`.
Periksa ulang seluruh entri terhadap berkas mentah dengan:

    python -m src.silver.katalog

Berkas 2026-10-17 dan 2026-10-20 untuk var1241, var2753, dan var2754 byte-identik
(sha256 sama di MANIFEST.csv); katalog memakai snapshot 2026-10-20 agar tiap seri
hanya punya satu berkas sumber.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
LOG = Path(__file__).resolve().parents[2] / "log-keputusan.csv"

SUMBER_SAH = {"bps", "wdi"}
SATUAN_SAH = {"persen", "ton", "kilogram"}

KATALOG = {
    "var1241": {
        "sumber": "bps",
        "nama": "11.1.1.(a) Persentase Rumah Tangga yang Memiliki Akses Terhadap "
                "Hunian Yang Layak Menurut Provinsi",
        "kode_sdg": "11.1.1",
        "kode_sdg_katalog": "11.1.1",
        "satuan": "persen",
        "satuan_mentah": "Persen",
        "satuan_katalog": "persen",
        "periode": "tahunan",
        "berkas_data": "bps/2026-10-20/sdg11_11_1_1_a_v1241.csv",
        "berkas_metadata": "bps/2026-10-20/json/sdg11_11_1_1_a_v1241.json",
        "dasar_satuan": "var[0].unit = 'Persen'; kolom satuan CSV = 'Persen'; "
                        "nilai 4,44-99,49",
        "dasar_sdg": "var[0].label diawali '11.1.1.(a)'; nama berkas "
                     "sdg11_11_1_1_a_v1241",
        "perlu_log": False,
    },
    "var2012": {
        "sumber": "bps",
        "nama": "Persentase rumah tangga yang memiliki akses nyaman (jarak 0.5 km) "
                "ke transportasi umum menurut provinsi",
        "kode_sdg": "11.2.1",
        "kode_sdg_katalog": "11.2.1",
        "satuan": "persen",
        "satuan_mentah": "",
        "satuan_katalog": "tidak_ada",
        "periode": "tahunan",
        "berkas_data": "bps/2026-10-20/sdg11_11_2_1_a_v2012.csv",
        "berkas_metadata": "bps/2026-10-20/json/sdg11_11_2_1_a_v2012.json",
        "dasar_satuan": "judul 'Persentase ...'; var[0].unit = ''; kolom satuan CSV "
                        "kosong; nilai 33,58-84,87",
        "dasar_sdg": "nama berkas sdg11_11_2_1_a_v2012 (kode tidak muncul di "
                     "var[0].label)",
        "perlu_log": True,
    },
    "var2013": {
        "sumber": "bps",
        "nama": "Persentase penduduk berumur 10 tahun ke atas yang menggunakan "
                "kendaraan bermotor umum dengan rute tertentu menurut provinsi",
        "kode_sdg": "11.2.1",
        "kode_sdg_katalog": "11.2.1",
        "satuan": "persen",
        "satuan_mentah": "",
        "satuan_katalog": "tidak_ada",
        "periode": "tahunan",
        "berkas_data": "bps/2026-10-20/sdg11_11_2_1_b_v2013.csv",
        "berkas_metadata": "bps/2026-10-20/json/sdg11_11_2_1_b_v2013.json",
        "dasar_satuan": "judul 'Persentase ...'; var[0].unit = ''; kolom satuan CSV "
                        "kosong; nilai 0,52-15,83",
        "dasar_sdg": "nama berkas sdg11_11_2_1_b_v2013 (kode tidak muncul di "
                     "var[0].label)",
        "perlu_log": True,
    },
    "var2753": {
        "sumber": "bps",
        "nama": "9.1.2* Jumlah Bongkar Muat Barang Moda Transportasi Kapal",
        "kode_sdg": "9.1.2",
        "kode_sdg_katalog": "9.1.2",
        "satuan": "ton",
        "satuan_mentah": "KG",
        "satuan_katalog": "kilogram",
        "periode": "tahunan",
        "berkas_data": "bps/2026-10-20/sdg9_9_1_2_v2753.csv",
        "berkas_metadata": "bps/2026-10-20/json/sdg9_9_1_2_v2753.json",
        "dasar_satuan": "metadata var[0].unit dan kolom satuan sama-sama 'KG', tetapi "
                        "besaran tidak cocok: nasional 2022 = 393.000.000; bongkar "
                        "Kaltara 2022 = 2.932.021 vs publikasi BPS 2.841.459 ton; "
                        "jika kg nilainya 1.000x terlalu kecil",
        "dasar_sdg": "var[0].label diawali '9.1.2*'; nama berkas sdg9_9_1_2_v2753",
        "perlu_log": True,
    },
    "var2754": {
        "sumber": "bps",
        "nama": "9.1.2*. Jumlah Bongkar Muat Barang Moda Transportasi Pesawat Terbang",
        "kode_sdg": "9.1.2",
        "kode_sdg_katalog": "9.1.2",
        "satuan": "kilogram",
        "satuan_mentah": "KG",
        "satuan_katalog": "kilogram",
        "periode": "tahunan",
        "berkas_data": "bps/2026-10-20/sdg9_9_1_2_v2754.csv",
        "berkas_metadata": "bps/2026-10-20/json/sdg9_9_1_2_v2754.json",
        "dasar_satuan": "var[0].unit = 'KG'; nilai nasional 2022 = 577 juta kg atau "
                        "sekitar 577 ribu ton, sejalan kargo udara nasional; jika ton "
                        "angkanya mustahil",
        "dasar_sdg": "var[0].label diawali '9.1.2*'; nama berkas sdg9_9_1_2_v2754",
        "perlu_log": True,
    },
    "EN.POP.SLUM.UR.ZS": {
        "sumber": "wdi",
        "nama": "Population living in slums (% of urban population)",
        "kode_sdg": "11.1.1",
        "kode_sdg_katalog": None,
        "satuan": "persen",
        "satuan_mentah": "",
        "satuan_katalog": None,
        "periode": "tahunan",
        "berkas_data": "wdi/2026-10-20/data/kelompok-01-hal-01.json",
        "berkas_metadata": "wdi/2026-10-20/metadata/sumber46_indikator.json",
        "dasar_satuan": "judul '% of urban population'; unit = ''; nilai 19,41-35,13",
        "dasar_sdg": "sourceNote WDI: '...the Sustainable Development Goal 11.1.1...'; "
                     "sumber 'Sustainable Development Goals'",
        "perlu_log": True,
    },
}


def ambil(kode):
    """Entri katalog satu seri; gagal keras bila seri tidak dikenal."""
    try:
        return KATALOG[kode]
    except KeyError:
        raise KeyError(f"seri {kode!r} tidak ada di katalog") from None


def satuan(kode):
    """Satuan final yang dipakai Silver untuk seri ini."""
    return ambil(kode)["satuan"]


def kode_sdg(kode):
    """Kode SDG final untuk seri ini."""
    return ambil(kode)["kode_sdg"]


def _muat_json(rel):
    with open(RAW / rel, encoding="utf-8") as f:
        return json.load(f)


def _cek_bps(kode, entri, salah):
    var = _muat_json(entri["berkas_metadata"])[0]["var"][0]
    if var["label"].strip() != entri["nama"].strip():
        salah.append(f"{kode}: label mentah {var['label']!r} != katalog {entri['nama']!r}")
    if (var.get("unit") or "") != entri["satuan_mentah"]:
        salah.append(f"{kode}: unit mentah {var.get('unit')!r} != "
                     f"satuan_mentah {entri['satuan_mentah']!r}")

    berkas = Path(entri["berkas_metadata"]).name
    if (entri["kode_sdg"] not in var["label"]
            and entri["kode_sdg"].replace(".", "_") not in berkas):
        salah.append(f"{kode}: kode SDG {entri['kode_sdg']} tidak ditemukan di label "
                     f"maupun nama berkas")

    df = pd.read_csv(RAW / entri["berkas_data"])
    satuan_mentah = {str(u) for u in df["satuan"].dropna().unique()}
    if entri["satuan_mentah"]:
        if satuan_mentah != {entri["satuan_mentah"]}:
            salah.append(f"{kode}: satuan kolom CSV {sorted(satuan_mentah)} != "
                         f"{entri['satuan_mentah']!r}")
    elif satuan_mentah:
        salah.append(f"{kode}: kolom satuan CSV harus kosong, ditemukan "
                     f"{sorted(satuan_mentah)}")

    if df["nilai"].isna().any() or (df["nilai"] < 0).any():
        salah.append(f"{kode}: nilai kosong atau negatif di berkas mentah")
    if entri["satuan"] == "persen" and (df["nilai"] > 100).any():
        salah.append(f"{kode}: satuan persen tetapi ada nilai > 100")
    if entri["periode"] == "tahunan" and set(df["periode"]) != {"Tahun"}:
        salah.append(f"{kode}: periode CSV {sorted(set(df['periode']))} bukan tahunan")


def _cek_wdi(kode, entri, salah):
    baris = []
    for blok in _muat_json(entri["berkas_data"]):
        if isinstance(blok, list):
            baris.extend(r for r in blok
                         if isinstance(r, dict)
                         and r.get("indicator", {}).get("id") == kode)
    if not baris:
        salah.append(f"{kode}: indikator tidak ditemukan di berkas data WDI")
        return

    nilai = [r["value"] for r in baris if r.get("value") is not None]
    if not nilai:
        salah.append(f"{kode}: tidak ada observasi bernilai di berkas data WDI")
    if entri["satuan"] == "persen" and any(not 0 <= v <= 100 for v in nilai):
        salah.append(f"{kode}: satuan persen tetapi ada nilai di luar 0-100")
    if any(not str(r["date"]).isdigit() or len(str(r["date"])) != 4
           for r in baris if r.get("value") is not None):
        salah.append(f"{kode}: ada tanggal WDI yang bukan tahun")

    meta = None
    for blok in _muat_json(entri["berkas_metadata"]):
        if isinstance(blok, list):
            for r in blok:
                if isinstance(r, dict) and r.get("id") == kode:
                    meta = r
    if meta is None:
        salah.append(f"{kode}: metadata indikator tidak ditemukan")
        return
    if meta.get("name") != entri["nama"]:
        salah.append(f"{kode}: nama metadata {meta.get('name')!r} != katalog "
                     f"{entri['nama']!r}")
    if entri["kode_sdg"] not in (meta.get("sourceNote") or ""):
        salah.append(f"{kode}: kode SDG tidak disebut di sourceNote metadata")


def _cek_log(salah):
    with open(LOG, encoding="utf-8") as f:
        tercatat = {r["seri_kode"] for r in csv.DictReader(f)}
    for kode, entri in KATALOG.items():
        # log menulis seri BPS tanpa awalan "var" (mis. 2753), katalog memakai "var2753"
        alias = kode.removeprefix("var")
        if entri["perlu_log"] and kode not in tercatat and alias not in tercatat:
            salah.append(f"{kode}: ada koreksi katalog tetapi tidak ada baris di "
                         f"log-keputusan.csv")


def periksa():
    """Daftar pelanggaran katalog (kosong = semua konsisten)."""
    salah = []
    for kode, entri in KATALOG.items():
        if entri["sumber"] not in SUMBER_SAH:
            salah.append(f"{kode}: sumber {entri['sumber']!r} tidak dikenal")
        if entri["satuan"] not in SATUAN_SAH:
            salah.append(f"{kode}: satuan {entri['satuan']!r} tidak dikenal")
        if not all(entri.get(k) for k in ("nama", "kode_sdg", "berkas_data",
                                          "berkas_metadata", "dasar_satuan",
                                          "dasar_sdg")):
            salah.append(f"{kode}: field wajib katalog ada yang kosong")
            continue
        if entri["sumber"] == "bps":
            _cek_bps(kode, entri, salah)
        else:
            _cek_wdi(kode, entri, salah)
    _cek_log(salah)
    return salah


def main():
    print(f"{'seri':<20} {'sumber':<6} {'SDG':<8} {'satuan':<9} katalog -> final")
    for kode, entri in KATALOG.items():
        katalog = f"{entri['satuan_katalog'] or '-'} / {entri['kode_sdg_katalog'] or '-'}"
        print(f"{kode:<20} {entri['sumber']:<6} {entri['kode_sdg']:<8} "
              f"{entri['satuan']:<9} {katalog} -> {entri['satuan']} / {entri['kode_sdg']}")
    salah = periksa()
    for pesan in salah:
        print(f"GAGAL  {pesan}")
    if salah:
        sys.exit(1)
    print(f"LOLOS  {len(KATALOG)} seri, satu satuan dan satu kode SDG per seri")


if __name__ == "__main__":
    main()
