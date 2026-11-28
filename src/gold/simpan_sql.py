"""Tahap 5 — muat tabel Silver ke SQLite sesuai `sql/silver_sqlite.sql`.

Skema memakai tabel STRICT dan kunci asing gabungan, sehingga basis data sendiri
menolak baris yang satuannya tidak cocok dengan seri, nama wilayah yang tidak
cocok dengan kodenya, atau sha256 yang tidak cocok dengan `MANIFEST.csv`.

    python -m src.gold.simpan_sql
    python -m src.gold.simpan_sql --silver data/silver/silver.parquet --keluaran data/silver/silver.sqlite

Berkas basis data tidak di-commit; bangkitkan ulang dengan perintah di atas atau
lewat `python pipeline.py`.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from src.common.manifest import baca
from src.common.skema import KOLOM
from src.silver.katalog import KATALOG

ROOT = Path(__file__).resolve().parents[2]
SILVER = ROOT / "data" / "silver" / "silver.parquet"
DDL = ROOT / "sql" / "silver_sqlite.sql"
KELUARAN = ROOT / "data" / "silver" / "silver.sqlite"
RAW = ROOT / "data" / "raw"


def sambung(path=KELUARAN):
    """Buka SQLite dan aktifkan kunci asing (tidak aktif secara bawaan)."""
    con = sqlite3.connect(Path(path))
    con.execute("PRAGMA foreign_keys = ON")
    return con


def _periksa_versi():
    versi = tuple(int(bagian) for bagian in sqlite3.sqlite_version.split("."))
    if versi < (3, 37):
        raise RuntimeError(
            f"SQLite {sqlite3.sqlite_version} terlalu lama; tabel STRICT butuh 3.37 ke atas"
        )


def _baris_seri():
    return [
        (kode, info["sumber"], info["nama"], info["kode_sdg"], info["satuan"])
        for kode, info in sorted(KATALOG.items())
    ]


def _baris_wilayah(silver):
    wilayah = (
        silver[["wilayah_kode", "nama_wilayah"]]
        .drop_duplicates()
        .sort_values("wilayah_kode")
    )
    ganda = wilayah["wilayah_kode"].duplicated().any()
    if ganda:
        raise ValueError("satu wilayah_kode memiliki lebih dari satu nama_wilayah")

    return [
        (
            int(baris.wilayah_kode),
            str(baris.nama_wilayah),
            "nasional" if int(baris.wilayah_kode) == 9999 else "provinsi",
        )
        for baris in wilayah.itertuples(index=False)
    ]


def _baris_berkas():
    berkas = []
    for nama, sha256 in sorted(baca().items()):
        jalur = RAW / nama
        if not jalur.exists():
            raise FileNotFoundError(f"berkas mentah tidak ditemukan: {jalur}")
        berkas.append((nama, jalur.stat().st_size, sha256))
    return berkas


def muat(silver, path=KELUARAN, ddl=DDL):
    """Bangun ulang basis data SQLite dari DataFrame Silver."""
    _periksa_versi()

    kurang = [kolom for kolom in KOLOM if kolom not in silver.columns]
    if kurang:
        raise ValueError(f"kolom Silver tidak lengkap: {kurang}")

    path = Path(path)
    if path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)

    con = sambung(path)
    try:
        con.executescript(Path(ddl).read_text(encoding="utf-8"))
        con.executemany(
            "INSERT INTO seri (seri_kode, sumber, nama, kode_sdg, satuan) "
            "VALUES (?, ?, ?, ?, ?)",
            _baris_seri(),
        )
        con.executemany(
            "INSERT INTO wilayah (wilayah_kode, nama_wilayah, tingkat) "
            "VALUES (?, ?, ?)",
            _baris_wilayah(silver),
        )
        con.executemany(
            "INSERT INTO berkas_raw (berkas, bait, sha256) VALUES (?, ?, ?)",
            _baris_berkas(),
        )

        data = silver[KOLOM].copy()
        data["wilayah_kode"] = data["wilayah_kode"].astype(int)
        data["nilai"] = data["nilai"].astype(float)
        con.executemany(
            "INSERT INTO silver ("
            + ", ".join(KOLOM)
            + ") VALUES ("
            + ", ".join("?" for _ in KOLOM)
            + ")",
            list(data.itertuples(index=False, name=None)),
        )
        con.commit()

        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError(f"integrity_check gagal: {integrity}")
        pelanggaran = con.execute("PRAGMA foreign_key_check").fetchall()
        if pelanggaran:
            raise ValueError(f"foreign_key_check menemukan {len(pelanggaran)} pelanggaran")

        jumlah = {
            tabel: con.execute(f"SELECT COUNT(*) FROM {tabel}").fetchone()[0]
            for tabel in ("silver", "seri", "wilayah", "berkas_raw")
        }
    finally:
        con.close()

    return {"path": path, **jumlah}


def jalankan(silver=None, path=KELUARAN):
    """Tahap pipeline: muat Silver lalu laporkan jumlah baris tiap tabel."""
    if silver is None:
        silver = pd.read_parquet(SILVER)

    hasil = muat(silver, path)
    print(
        "SQLite Silver: {silver:,} baris, {seri} seri, {wilayah} wilayah, "
        "{berkas_raw} berkas mentah".format(**hasil)
    )
    print(f"Lokasi: {hasil['path']}")
    return hasil


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--silver", type=Path, default=SILVER)
    parser.add_argument("--keluaran", type=Path, default=KELUARAN)
    args = parser.parse_args(argv)

    jalankan(pd.read_parquet(args.silver), args.keluaran)


if __name__ == "__main__":
    main()
