"""Pengujian pemuatan Silver ke SQLite (Tahap 5).

    python -m unittest tests/test_sql.py

Membutuhkan `data/silver/silver.parquet` (jalankan `python pipeline.py` lebih dulu).
Basis data uji dibuat di direktori sementara, bukan di `data/`.
"""
from __future__ import annotations

import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.common.skema import KOLOM, KUNCI
from src.gold.simpan_sql import muat, sambung
from src.silver.katalog import KATALOG as KATALOG_SERI

ROOT = Path(__file__).resolve().parents[1]
SILVER = ROOT / "data" / "silver" / "silver.parquet"


class TestSimpanSql(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SILVER.exists():
            raise FileNotFoundError(
                "data/silver/silver.parquet belum ada. Jalankan `python pipeline.py`."
            )
        cls.silver = pd.read_parquet(SILVER)
        cls.folder = Path(tempfile.mkdtemp(prefix="sql-silver-"))
        cls.path = cls.folder / "silver.sqlite"
        cls.hasil = muat(cls.silver, cls.path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.folder, ignore_errors=True)

    def test_jumlah_tabel(self):
        self.assertEqual(self.hasil["silver"], len(self.silver))
        self.assertEqual(self.hasil["seri"], 6)
        self.assertEqual(self.hasil["wilayah"], 39)
        self.assertEqual(self.hasil["berkas_raw"], 22)

    def test_bolak_balik_sama_dengan_parquet(self):
        with sambung(self.path) as con:
            db = pd.read_sql_query(
                "SELECT " + ", ".join(KOLOM) + " FROM silver", con
            )

        a = self.silver[KOLOM].sort_values(KUNCI).reset_index(drop=True)
        b = db[KOLOM].sort_values(KUNCI).reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b)

    def test_integritas_dan_kunci_asing(self):
        with sambung(self.path) as con:
            self.assertEqual(
                con.execute("PRAGMA integrity_check").fetchone()[0], "ok"
            )
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_pandangan_provinsi_dan_nasional(self):
        with sambung(self.path) as con:
            provinsi = con.execute("SELECT COUNT(*) FROM v_provinsi").fetchone()[0]
            nasional = con.execute("SELECT COUNT(*) FROM v_nasional").fetchone()[0]
        self.assertEqual(provinsi, 1258)
        self.assertEqual(nasional, 37)

    def test_satuan_seri_sesuai_katalog(self):
        with sambung(self.path) as con:
            baris = dict(
                con.execute("SELECT seri_kode, satuan FROM seri").fetchall()
            )
        for kode, info in KATALOG_SERI.items():
            self.assertEqual(baris[kode], info["satuan"])

    def test_menolak_pelanggaran(self):
        with sambung(self.path) as con:
            acuan = con.execute(
                "SELECT " + ", ".join(KOLOM) + " FROM silver LIMIT 1"
            ).fetchone()
            tempat = ", ".join("?" for _ in KOLOM)
            sql = f"INSERT INTO silver ({', '.join(KOLOM)}) VALUES ({tempat})"

            kasus = {
                "kunci ganda": acuan,
                "persen di luar 0-100": acuan[:7] + (100.5,) + acuan[8:],
                "seri tidak terdaftar": acuan[:1] + ("var9999",) + acuan[2:],
                "sha256 tidak cocok": acuan[:-1] + ("0" * 64,),
                "nama wilayah tidak cocok": acuan[:3] + ("BUKAN NAMA",) + acuan[4:],
            }

            for nama, nilai in kasus.items():
                with self.subTest(kasus=nama):
                    con.execute("SAVEPOINT uji")
                    with self.assertRaises(sqlite3.IntegrityError):
                        con.execute(sql, nilai)
                    con.execute("ROLLBACK TO uji")
                    con.execute("RELEASE uji")


if __name__ == "__main__":
    unittest.main()
