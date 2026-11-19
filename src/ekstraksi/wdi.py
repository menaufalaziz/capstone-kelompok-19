"""Tahap 1 — pembaca JSON data dan metadata WDI. Tidak membersihkan apa pun.

Struktur berkas WDI (API World Bank): daftar dua elemen, [info halaman, daftar baris].
  - data/*.json              : baris observasi, bersarang (indicator.id, country.id, ...). Disaring menurut
                               indicator.id; nilai null tetap menjadi baris (NaN), tidak dibuang.
  - metadata/sumber.json     : daftar sumber data (tanpa indicator.id, dibaca utuh).
  - metadata/sumber*_indikator.json : daftar indikator (kunci `id`). Disaring menurut id.
Kolom bersarang diratakan dengan "_" (indicator.id -> indicator_id); daftar (mis. topics) disimpan
sebagai teks JSON. Kolom lineage: _format, _berkas_raw, _sha256_raw.
"""
import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw

SERI = "EN.POP.SLUM.UR.ZS"


def _muat(berkas, raw=RAW, encoding="utf-8-sig"):
    with open(Path(raw) / berkas, encoding=encoding) as f:
        d = json.load(f)
    if not (isinstance(d, list) and len(d) == 2 and isinstance(d[1], list)):
        raise ValueError(f"{berkas}: bentuk tidak dikenal (harap [info, daftar baris])")
    return d[1]


def _tabel(baris, berkas):
    df = pd.json_normalize(baris, sep="_")
    for k in df.columns:                                   # daftar/dict sisa -> teks JSON
        if df[k].map(lambda v: isinstance(v, (list, dict))).any():
            df[k] = df[k].map(lambda v: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v)
    df["_format"] = "json"
    df["_berkas_raw"] = str(berkas)
    df["_sha256_raw"] = sha256_raw(berkas, RAW)
    return df


def baca_data(berkas, raw=RAW, seri=SERI):
    """Berkas data WDI -> baris untuk indicator.id == seri."""
    baris = [b for b in _muat(berkas, raw) if b.get("indicator", {}).get("id") == seri]
    df = _tabel(baris, berkas)
    df["value"] = pd.to_numeric(df["value"], errors="raise")   # null -> NaN, tidak dibuang
    return df


def baca_metadata(berkas, raw=RAW, seri=SERI):
    """Metadata indikator -> baris dengan id == seri."""
    return _tabel([b for b in _muat(berkas, raw) if b.get("id") == seri], berkas)


def baca_sumber(berkas, raw=RAW):
    """sumber.json -> semua baris (tidak ada indicator.id untuk disaring)."""
    return _tabel(_muat(berkas, raw), berkas)


def baca_wdi(raw=RAW, seri=SERI):
    """Baca semua berkas WDI. Mengembalikan ({"wdi", "wdi_metadata", "wdi_sumber": DataFrame}, {berkas: jumlah_baris})."""
    raw = Path(raw)
    rel = lambda ps: [p.relative_to(raw).as_posix() for p in sorted(ps)]
    data = rel(raw.glob("wdi/*/data/*.json"))
    meta = [b for b in rel(raw.glob("wdi/*/metadata/*.json")) if not b.endswith("/sumber.json")]
    sumber = [b for b in rel(raw.glob("wdi/*/metadata/*.json")) if b.endswith("/sumber.json")]
    jumlah, hasil = {}, {"wdi": [], "wdi_metadata": [], "wdi_sumber": []}
    for kunci, berkas, baca in [("wdi", data, lambda b: baca_data(b, raw, seri)),
                                ("wdi_metadata", meta, lambda b: baca_metadata(b, raw, seri)),
                                ("wdi_sumber", sumber, lambda b: baca_sumber(b, raw))]:
        for b in berkas:
            df = baca(b)
            hasil[kunci].append(df)
            jumlah[b] = len(df)
    return {k: pd.concat(v, ignore_index=True) for k, v in hasil.items()}, jumlah


if __name__ == "__main__":
    tabel, jumlah = baca_wdi()
    for b, n in jumlah.items():
        print(f"{n:>5}  {b}")
    print(f"{sum(jumlah.values()):>5}  total ({len(jumlah)} berkas)")
