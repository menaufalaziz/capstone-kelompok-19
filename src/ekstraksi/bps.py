import json 
from itertools import product
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw


KOLOM_ASAL = ["var_id", "wilayah_id", "wilayah", "turvar_id", "turvar",
              "tahun_id", "tahun", "periode_id", "periode", "nilai", "satuan"]
KOLOM_JSON = ["var_judul", "last_update", "halaman_json"]
KOLOM_LINEAGE = ["_format", "_berkas_raw", "_sha256_raw"]
KOLOM = KOLOM_ASAL + KOLOM_JSON + KOLOM_LINEAGE

def _angka(seri, desimal="."):
    """Ubah teks ke float. desimal='.' (default, sesuai berkas BPS ini) atau ','. Galat bila bukan angka."""
    s = seri.astype(str).str.strip()
    if desimal == ",":
        s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    hasil = pd.to_numeric(s, errors="coerce")
    rusak = hasil.isna() & (s != "")
    if rusak.any():
        raise ValueError(f"nilai bukan angka: {s[rusak].unique()[:5].tolist()}")
    return hasil


def _lengkapi(df, berkas, format_):
    for k in KOLOM_JSON:
        if k not in df:
            df[k] = None
    df["_format"] = format_
    df["_berkas_raw"] = str(berkas)
    df["_sha256_raw"] = sha256_raw(berkas, RAW)
    return df[KOLOM]


def baca_csv(berkas, raw=RAW, desimal=".", encoding="utf-8-sig"):
    """CSV BPS -> DataFrame. Semua kolom dibaca sebagai teks (tanpa NA otomatis), lalu nilai -> float."""
    p = Path(raw) / berkas
    with open(p, newline="", encoding=encoding) as f:
        df = pd.read_csv(f, dtype=str, keep_default_na=False)
    kurang = [k for k in KOLOM_ASAL if k not in df.columns]
    if kurang:
        raise ValueError(f"{berkas}: kolom tidak ada {kurang}")
    df["nilai"] = _angka(df["nilai"], desimal)
    return _lengkapi(df, berkas, "csv")


def baca_json(berkas, raw=RAW, desimal=".", encoding="utf-8-sig"):
    """JSON WebAPI BPS (daftar halaman) -> DataFrame panjang."""
    p = Path(raw) / berkas
    with open(p, encoding=encoding) as f:
        halaman = json.load(f)
    if isinstance(halaman, dict):
        halaman = [halaman]
    baris = []
    for i, h in enumerate(halaman):
        if h.get("status") != "OK" or h.get("data-availability") != "available":
            raise ValueError(f"{berkas} halaman {i}: status {h.get('status')!r}, {h.get('data-availability')!r}")
        if len(h["var"]) != 1:
            raise ValueError(f"{berkas} halaman {i}: harap tepat satu var, ada {len(h['var'])}")
        var = h["var"][0]
        dc = h["datacontent"]
        terpakai = 0
        for v, t, th, tt in product(h["vervar"], h["turvar"], h["tahun"], h["turtahun"]):
            kunci = f"{v['val']}{var['val']}{t['val']}{th['val']}{tt['val']}"
            if kunci not in dc:
                continue          # kombinasi tanpa observasi: tidak ada baris (tidak diisi)
            terpakai += 1
            baris.append({"var_id": str(var["val"]), "wilayah_id": str(v["val"]), "wilayah": v["label"],
                          "turvar_id": str(t["val"]), "turvar": t["label"],
                          "tahun_id": str(th["val"]), "tahun": th["label"],
                          "periode_id": str(tt["val"]), "periode": tt["label"],
                          "nilai": dc[kunci], "satuan": var.get("unit", ""),
                          "var_judul": var["label"], "last_update": h.get("last_update"),
                          "halaman_json": i})
        if terpakai != len(dc):
            raise ValueError(f"{berkas} halaman {i}: {len(dc) - terpakai} kunci datacontent tidak terurai")
    df = pd.DataFrame(baris)
    df["nilai"] = _angka(df["nilai"], desimal)
    return _lengkapi(df, berkas, "json")


def berkas_bps(raw=RAW):
    """Daftar berkas seri BPS (relatif data/raw): bps/<snapshot>/*.csv dan bps/<snapshot>/json/*.json.
    manifest_asal.json adalah metadata unduhan, bukan seri, jadi tidak ikut."""
    raw = Path(raw)
    csv_ = sorted(raw.glob("bps/*/*.csv"))
    json_ = sorted(raw.glob("bps/*/json/*.json"))
    return [p.relative_to(raw).as_posix() for p in csv_ + json_]


def baca_bps(raw=RAW, desimal="."):
    """Baca semua berkas BPS. Mengembalikan (DataFrame gabungan, {berkas: jumlah_baris})."""
    bagian, jumlah = [], {}
    for b in berkas_bps(raw):
        df = baca_json(b, raw, desimal) if b.endswith(".json") else baca_csv(b, raw, desimal)
        bagian.append(df)
        jumlah[b] = len(df)
    return pd.concat(bagian, ignore_index=True), jumlah


if __name__ == "__main__":
    df, jumlah = baca_bps()
    for b, n in jumlah.items():
        print(f"{n:>5}  {b}")
    print(f"{len(df):>5}  total ({len(jumlah)} berkas)")


