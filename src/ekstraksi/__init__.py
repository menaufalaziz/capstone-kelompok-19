
"""Tahap 1 — Ekstraksi (pertemuan X). Milik tim.

Baca setiap berkas di data/raw/ menjadi DataFrame mentah yang setia pada sumbernya: jangan membersihkan
di sini, cukup ratakan struktur dan catat asal tiap baris (`_berkas_raw` relatif data/raw/,
`_sha256_raw` dari src.common.manifest). Kolom asal dipertahankan; penyeragaman nama, satuan, dan
wilayah dikerjakan di tahap berikutnya (gabungkan wilayah lewat kode: `wilayah_id`, bukan ejaan `wilayah`).

Keluaran jalankan(): {"bps", "bps_asal", "wdi", "wdi_metadata", "wdi_sumber": DataFrame mentah}.
Berkas di MANIFEST.csv yang tidak terbaca membuat jalankan() gagal (tidak ada yang terlewat diam-diam).
"""
from src.common.manifest import baca as baca_manifest

from .bps import baca_bps, baca_bps_asal
from .wdi import baca_wdi


def cakupan(tabel):
    """(berkas di MANIFEST yang tidak terbaca, berkas terbaca yang tidak ada di MANIFEST)."""
    terbaca = {b for df in tabel.values() for b in df["_berkas_raw"].unique()}
    manifest = set(baca_manifest())
    return sorted(manifest - terbaca), sorted(terbaca - manifest)


def ejaan_wilayah(df):
    """Diagnostik tanpa mengubah data: kode dengan >1 ejaan, dan ejaan yang dipakai >1 kode."""
    kode = df.groupby("wilayah_id")["wilayah"].nunique()
    nama = df.groupby("wilayah")["wilayah_id"].nunique()
    return kode[kode > 1].index.tolist(), nama[nama > 1].index.tolist()


def ringkasan(tabel):
    """Angka untuk results/<nim>/metrics.json: berkas_dibaca, baris_mentah, format (jumlah format berkas)."""
    return {"berkas_dibaca": len({b for df in tabel.values() for b in df["_berkas_raw"].unique()}),
            "baris_mentah": sum(len(df) for df in tabel.values()),
            "format": len({f for df in tabel.values() for f in df["_format"].unique()})}


def jalankan():
    """Kembalikan {nama_sumber: DataFrame mentah}."""
    bps, _ = baca_bps()
    asal, _ = baca_bps_asal()
    wdi, _ = baca_wdi()
    tabel = {"bps": bps, "bps_asal": asal, **wdi}

    hilang, asing = cakupan(tabel)
    if hilang or asing:
        raise RuntimeError(f"cakupan ekstraksi tidak cocok dengan MANIFEST.csv: terlewat={hilang}, tidak terdaftar={asing}")
    kode_ganda, nama_ganda = ejaan_wilayah(bps)
    r = ringkasan(tabel)
    print(f"ekstraksi: {r['berkas_dibaca']} berkas, {r['baris_mentah']} baris mentah, {r['format']} format; "
          f"wilayah_id dengan >1 ejaan: {len(kode_ganda)}, ejaan dengan >1 kode: {len(nama_ganda)}")
    return tabel
