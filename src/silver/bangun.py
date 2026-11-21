
"""Bangun tabel Silver dari keluaran tahap ekstraksi.

Satu baris = satu seri x wilayah x periode x rincian x berkas sumber.
Nilai dari sumber berbeda tidak digabung di sini; pemilihan rincian yang
sebanding (Bongkar/Muat, dan pembanding nasional) dikerjakan di Gold.

Berkas sumber BPS dipilih dari snapshot 2026-10-20. Menurut MANIFEST.csv,
ketiga seri yang juga ada pada snapshot 2026-10-17 byte-identik, sedangkan
var2012 dan var2013 hanya tersedia pada snapshot 2026-10-20 (K-008).
"""

from pathlib import Path

import pandas as pd

from src.common.manifest import baca as baca_manifest
from src.common.skema import KOLOM, KUNCI, periksa_silver
from src.silver.katalog import satuan as satuan_katalog


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "silver" / "silver.parquet"

SNAPSHOT = "2026-10-20"

# Satu berkas CSV per seri. Versi JSON di data/raw adalah representasi lain
# dari angka yang sama; memakai keduanya akan membuat kunci Silver kembar.
DATASETS = {
    "var1241": "sdg11_11_1_1_a_v1241.csv",
    "var2012": "sdg11_11_2_1_a_v2012.csv",
    "var2013": "sdg11_11_2_1_b_v2013.csv",
    "var2753": "sdg9_9_1_2_v2753.csv",
    "var2754": "sdg9_9_1_2_v2754.csv",
}

WDI_SERI = "EN.POP.SLUM.UR.ZS"
RINCIAN_KOSONG = "Tidak ada"


def _teks(nilai):
    """Teks bersih tanpa mengubah arti nilai mentah."""
    teks = str(nilai).strip()
    return "" if teks.lower() in {"", "nan", "none"} else teks


def _rincian(turvar):
    """Rincian disimpan apa adanya; kategori kosong diberi label eksplisit."""
    return _teks(turvar) or RINCIAN_KOSONG


def _baris_bps(df, seri, berkas):
    """Baris Silver untuk satu seri BPS dari DataFrame hasil ekstraksi."""
    bagian = df[df["_berkas_raw"] == berkas]

    if bagian.empty:
        raise ValueError(f"{berkas} tidak ada di keluaran ekstraksi BPS")

    hasil = []

    for _, baris in bagian.iterrows():
        wilayah = int(str(baris["wilayah_id"]).strip())

        # Keputusan K-002: agregat nasional var2753 dikeluarkan dari Silver
        # agar tidak tercampur dengan observasi provinsi.
        # Seri lain tetap menyimpan baris 9999 karena Gold memisahkannya
        # dari panel provinsi (K-004).
        if seri == "var2753" and wilayah == 9999:
            continue

        periode = _teks(baris["tahun"])

        if not periode.isdigit() or len(periode) != 4:
            raise ValueError(
                f"{berkas}: periode {periode!r} bukan tahun empat digit"
            )

        jenis = _teks(baris["periode"]).lower()

        if jenis != "tahun":
            raise ValueError(
                f"{berkas}: jenis periode {jenis!r} belum didukung Silver"
            )

        hasil.append({
            "sumber": "bps",
            "seri_kode": seri,
            "wilayah_kode": wilayah,
            "nama_wilayah": _teks(baris["wilayah"]).upper(),
            "periode": periode,
            "jenis_periode": "tahun",
            "rincian": _rincian(baris["turvar"]),
            "nilai": float(baris["nilai"]),
            # Satuan final dari katalog hasil audit (K-011 s.d. K-014).
            "satuan": satuan_katalog(seri),
            "_berkas_raw": berkas,
            "_sha256_raw": _teks(baris["_sha256_raw"]),
        })

    return hasil


def _baris_wdi(df):
    """Baris Silver pembanding nasional WDI (Indonesia = 9999)."""
    bagian = df[df["indicator_id"] == WDI_SERI]

    if bagian.empty:
        raise ValueError(
            f"indikator WDI {WDI_SERI} tidak ada di keluaran ekstraksi"
        )

    hasil = []

    for _, baris in bagian.iterrows():
        if pd.isna(baris["value"]):
            # Silver hanya memuat observasi yang ada.
            # Sel kosong baru dibentuk sebagai grid di Gold.
            continue

        periode = _teks(baris["date"])

        if not periode.isdigit() or len(periode) != 4:
            raise ValueError(
                f"WDI {WDI_SERI}: periode {periode!r} bukan tahun empat digit"
            )

        hasil.append({
            "sumber": "wdi",
            "seri_kode": WDI_SERI,
            "wilayah_kode": 9999,
            "nama_wilayah": (
                _teks(baris["country_value"]).upper() or "INDONESIA"
            ),
            "periode": periode,
            "jenis_periode": "tahun",
            "rincian": RINCIAN_KOSONG,
            "nilai": float(baris["value"]),
            "satuan": satuan_katalog(WDI_SERI),
            "_berkas_raw": _teks(baris["_berkas_raw"]),
            "_sha256_raw": _teks(baris["_sha256_raw"]),
        })

    return hasil


def _beri_penanda_patahan(silver):
    """Tandai patahan metodologi hunian layak berdasarkan keputusan K-010.

    Nilai asli tidak diubah. Hanya observasi var1241 tahun 2019 yang diberi
    penanda patahan metodologi.
    """
    silver["penanda_patahan"] = ""

    mask_patahan = (
        (silver["seri_kode"] == "var1241")
        & (silver["periode"].astype(str) == "2019")
    )

    if not mask_patahan.any():
        raise ValueError(
            "Baris patahan metodologi var1241 tahun 2019 tidak ditemukan"
        )

    silver.loc[mask_patahan, "penanda_patahan"] = "patahan_metodologi"

    return silver


def bangun_silver(mentah=None):
    """Terima keluaran ekstraksi, tulis Silver, dan kembalikan DataFrame."""
    if mentah is None:
        from src.ekstraksi import jalankan as jalankan_ekstraksi
        mentah = jalankan_ekstraksi()

    bps = mentah.get("bps")
    wdi = mentah.get("wdi")

    if bps is None or wdi is None:
        raise KeyError(
            "keluaran ekstraksi harus memuat tabel 'bps' dan 'wdi'"
        )

    hasil = []

    for seri, nama_file in DATASETS.items():
        berkas = f"bps/{SNAPSHOT}/{nama_file}"
        hasil.extend(_baris_bps(bps, seri, berkas))

    hasil.extend(_baris_wdi(wdi))

    silver = pd.DataFrame(hasil, columns=KOLOM)

    # Penanda patahan metodologi K-010.
    silver = _beri_penanda_patahan(silver)

    # Periksa keunikan kunci Silver.
    kembar = silver.duplicated(KUNCI, keep=False)

    if kembar.any():
        contoh = silver.loc[kembar, KUNCI].head(3).to_dict("records")
        raise ValueError(
            f"{int(kembar.sum())} baris kembar pada kunci Silver, "
            f"mis. {contoh}"
        )

    silver = silver.sort_values(
        KUNCI, kind="stable"
    ).reset_index(drop=True)

    salah = periksa_silver(silver, baca_manifest())

    if salah:
        raise ValueError(
            "Silver tidak lolos skema minimal: " + "; ".join(salah)
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    silver.to_parquet(OUTPUT, index=False)

    print("Silver berhasil dibuat!")
    print(f"Lokasi: {OUTPUT}")
    print(f"Jumlah baris: {len(silver)}")
    print(f"Jumlah kolom: {len(silver.columns)}")
    print(
        f"Seri: {silver['seri_kode'].nunique()}; "
        f"rincian: {silver['rincian'].nunique()}"
    )
    print(
        "Baris dengan penanda patahan metodologi: "
        f"{int((silver['penanda_patahan'] == 'patahan_metodologi').sum())}"
    )

    return silver


if __name__ == "__main__":
    bangun_silver()
