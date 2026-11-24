"""Pengujian otomatis kualitas dan integritas Gold Panel (Tahap 4).

Komponen: Profil dan Pembersihan / Persiapan Gold (Riska Erlis / NIM 124450022).

Dapat dijalankan dengan:
    python -m unittest tests/test_gold.py
atau
    python -m pytest tests/test_gold.py (bila pytest terpasang)
"""
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GOLD_DIR = ROOT / "data" / "gold"
SILVER_FILE = ROOT / "data" / "silver" / "silver.parquet"


class TestGoldPanel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel_file = GOLD_DIR / "panel.parquet"
        cls.panel_lebar_file = GOLD_DIR / "panel_lebar.parquet"
        
        if not cls.panel_file.exists() or not cls.panel_lebar_file.exists():
            raise FileNotFoundError("Berkas Gold belum terbentuk. Jalankan `python pipeline.py` terlebih dahulu.")
        
        cls.panel = pd.read_parquet(cls.panel_file)
        cls.lebar = pd.read_parquet(cls.panel_lebar_file)
        cls.silver = pd.read_parquet(SILVER_FILE)

    def test_kunci_panel_unik(self):
        """Kunci (indikator, wilayah_kode, periode) harus unik di seluruh panel."""
        kunci = ["indikator", "wilayah_kode", "periode"]
        kembar = self.panel.duplicated(subset=kunci, keep=False)
        self.assertFalse(kembar.any(), f"Ditemukan {int(kembar.sum())} sel kembar pada kunci panel!")

    def test_jumlah_sel_panel(self):
        """Total panel = 1.330 sel: 1.258 terisi, 72 sel kosong."""
        self.assertEqual(len(self.panel), 1330, "Total baris panel harus 1.330 sel")
        terisi = (self.panel["status_sel"] == "terisi").sum()
        kosong = (self.panel["status_sel"] != "terisi").sum()
        self.assertEqual(terisi, 1258, "Sel terisi harus 1.258")
        self.assertEqual(kosong, 72, "Sel kosong harus 72")

    def test_indikator_terpilih(self):
        """Panel memuat tepat 7 indikator tingkat provinsi."""
        indikator_unik = set(self.panel["indikator"].unique())
        indikator_harapan = {
            "var1241", "var2012", "var2013",
            "var2753 [Bongkar]", "var2753 [Muat]",
            "var2754 [Bongkar]", "var2754 [Muat]",
        }
        self.assertEqual(indikator_unik, indikator_harapan)

    def test_wilayah_38_provinsi(self):
        """Panel hanya memuat 38 provinsi resmi (kode 1100–9700), tanpa agregat 9999."""
        wilayah_unik = set(self.panel["wilayah_kode"].unique())
        self.assertEqual(len(wilayah_unik), 38, "Harus tepat 38 provinsi")
        self.assertNotIn(9999, wilayah_unik, "Agregat nasional 9999 tidak boleh masuk panel provinsi")
        for kode in wilayah_unik:
            self.assertTrue(1100 <= kode <= 9700, f"Kode wilayah {kode} di luar rentang provinsi BPS")

    def test_status_sel_dan_nilai(self):
        """Sel terisi wajib bernilai numerik; sel kosong wajib bernilai NaN."""
        status_sah = {"terisi", "missing", "tidak_diterbitkan", "belum_ada", "batas_lama"}
        self.assertTrue(set(self.panel["status_sel"].unique()).issubset(status_sah))

        terisi = self.panel[self.panel["status_sel"] == "terisi"]
        self.assertFalse(terisi["nilai"].isna().any(), "Sel status 'terisi' tidak boleh bernilai NaN")

        kosong = self.panel[self.panel["status_sel"] != "terisi"]
        self.assertTrue(kosong["nilai"].isna().all(), "Sel kosong wajib bernilai NaN (tidak boleh nol atau estimasi)")

    def test_nilai_asli_konsisten_dengan_silver(self):
        """Nilai terisi di Gold harus sama persis dengan nilai asalnya di Silver."""
        terisi = self.panel[self.panel["status_sel"] == "terisi"].copy()
        s_prov = self.silver[self.silver["wilayah_kode"] != 9999].copy()
        
        m = terisi.merge(
            s_prov[["seri_kode", "wilayah_kode", "periode", "rincian", "nilai"]],
            on=["seri_kode", "wilayah_kode", "periode", "rincian"],
            suffixes=("_gold", "_silver")
        )
        self.assertEqual(len(m), 1258, "Seluruh 1.258 baris terisi harus cocok dengan Silver")
        selisih_maks = (m["nilai_gold"] - m["nilai_silver"]).abs().max()
        self.assertLess(selisih_maks, 1e-9, "Nilai di Gold tidak boleh berbeda dari nilai Silver")

    def test_penanda_patahan_dan_outlier(self):
        """Penanda patahan dan outlier dari Sprint 1 harus terbawa ke Gold tanpa mengubah nilai asli."""
        # 1. Patahan metodologi var1241 tahun 2019
        patahan_2019 = self.panel[(self.panel["indikator"] == "var1241") & (self.panel["periode"] == "2019")]
        self.assertEqual((patahan_2019["penanda"] == "patahan_seri").sum(), 34,
                         "Seluruh 34 provinsi pada var1241 tahun 2019 harus ditandai patahan_seri")

        # 2. Patahan wilayah Papua 2024
        papua_2024 = self.panel[(self.panel["indikator"] == "var1241") & 
                                (self.panel["wilayah_kode"] == 9400) & 
                                (self.panel["periode"] == "2024")]
        self.assertEqual(papua_2024["penanda"].iloc[0], "patahan_wilayah")

        # 3. Outlier asli terpasang
        ditandai = self.panel["penanda"].notna().sum()
        self.assertGreaterEqual(ditandai, 85, "Jumlah sel bertanda anomali/patahan minimal 85")

    def test_transformasi_logaritma_bongkar_muat(self):
        """Seri bongkar muat kargo memiliki kolom transformasi logaritma ln(1 + nilai) yang valid."""
        kargo = self.panel[self.panel["seri_kode"].isin(["var2753", "var2754"]) & (self.panel["status_sel"] == "terisi")]
        self.assertFalse(kargo["nilai_log"].isna().any(), "Kolom nilai_log pada kargo terisi harus bernilai numerik")
        
        # Validasi rumus log1p
        log_hitung = np.log1p(kargo["nilai"].astype(float))
        selisih = (kargo["nilai_log"] - log_hitung).abs().max()
        self.assertLess(selisih, 1e-9, "Transformasi log1p harus presisi")

    def test_panel_lebar_konsisten(self):
        """Panel lebar berukuran 394 baris x 11 kolom dan konsisten dengan panel terisi."""
        self.assertEqual(self.lebar.shape, (394, 11))
        kolom_wajib = {"wilayah_kode", "nama_wilayah", "jenis_periode", "periode",
                       "var1241", "var2012", "var2013",
                       "var2753 [Bongkar]", "var2753 [Muat]",
                       "var2754 [Bongkar]", "var2754 [Muat]"}
        self.assertEqual(set(self.lebar.columns), kolom_wajib)
        self.assertFalse(self.lebar.duplicated(["wilayah_kode", "periode"]).any(), "Kunci panel lebar harus unik")

    def test_log_keputusan_tahap_gold(self):
        """Aturan pemilihan Gold tercatat di log-keputusan.csv tahap 'gold'."""
        log_path = ROOT / "log-keputusan.csv"
        self.assertTrue(log_path.exists())
        log_df = pd.read_csv(log_path)
        gold_logs = log_df[log_df["tahap"] == "gold"]
        self.assertGreaterEqual(len(gold_logs), 5, "Harus terdapat minimal 5 baris keputusan tahap gold")
        self.assertTrue(gold_logs["nim"].notna().all(), "Setiap keputusan tahap gold harus punya NIM pencatat")
        self.assertTrue((gold_logs["nim"] == 124450022).any(),
                        "Keputusan tahap gold oleh Riska Erlis (124450022) harus tercatat")
        self.assertTrue(gold_logs["dampak_baris"].astype(str).str.contains("37").any(),
                        "Pencatatan 37 baris Silver tidak terpilih harus ada di log")


if __name__ == "__main__":
    unittest.main()
