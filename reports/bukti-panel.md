# Bukti hasil pipeline dan pengujian panel Gold

Dibangkitkan oleh `python bukti_panel.py` pada 2026-11-27.

## 1. Hasil `python pipeline.py`

Kode keluar: **0**

```text
data/raw: 22 berkas cocok dengan MANIFEST.csv
ekstraksi: 22 berkas, 5109 baris mentah, 2 format; wilayah_id dengan >1 ejaan: 0, ejaan dengan >1 kode: 0
ekstraksi  selesai dalam 0.4 s
Silver berhasil dibuat!
Lokasi: .\data\silver\silver.parquet
Jumlah baris: 1295
Jumlah kolom: 12
Seri: 6; rincian: 3
Baris dengan penanda patahan metodologi: 35
silver     selesai dalam 0.4 s
Panel Gold selesai: 1330 baris (1258 terisi, 72 kosong)
Panel lebar: 394 baris x 11 kolom
Baris Silver tidak terpilih ke panel provinsi: 37 baris
Gold panel unit-safe: 1,330 baris, 5 seri, 7 indikator, 72 sel kosong, 38 baris berpatahan
Lokasi: .\data\gold
gold       selesai dalam 1.4 s
Validasi: 1295 baris Silver, 1330 baris panel Gold, 5 seri, 7 indikator
Laporan: .\reports\validasi.md
validasi   selesai dalam 1.1 s
Periksa skema minimal: python -m src.common.skema data/silver/silver.parquet
```

## 2. Hasil `python -m unittest tests/test_gold.py`

Kode keluar: **0**

```text
...........
----------------------------------------------------------------------
Ran 11 tests in 0.317s

OK
```

## 3. Bukti kunci panel unik

| Berkas | Kunci | Baris | Baris kunci kembar |
|---|---|---:|---:|
| `panel_var1241.parquet` | `kode_prov + periode + indikator` | 418 | 0 |
| `panel_var2012.parquet` | `kode_prov + periode + indikator` | 76 | 0 |
| `panel_var2013.parquet` | `kode_prov + periode + indikator` | 76 | 0 |
| `panel_var2753.parquet` | `kode_prov + periode + indikator` | 380 | 0 |
| `panel_var2754.parquet` | `kode_prov + periode + indikator` | 380 | 0 |
| `panel_provinsi.parquet` | `kode_prov + periode + indikator` | 1,330 | 0 |
| `panel.parquet` | `indikator + wilayah_kode + periode` | 1,330 | 0 |
| `panel_lebar.parquet` | `wilayah_kode + periode` | 394 | 0 |

Tidak ada baris kunci kembar pada seluruh tabel panel di atas.

## 4. Bukti lineage sel Gold ke Silver

- Sel terisi di `panel_provinsi.parquet`: **1,258** dari 1,330 baris grid.
- `_baris_silver` dan `_kunci_silver` terisi pada seluruh sel terisi: **1,258** baris.
- `_kunci_silver` yang tidak sama dengan kunci baris Silver acuan: **0**.
- Nilai Gold yang tidak sama dengan nilai Silver setelah konversi satuan (var2754 kg -> ton): **0**.

| Kolom yang dicocokkan dengan baris Silver | Jumlah ketidakcocokan |
|---|---:|
| `seri_kode` | 0 |
| `wilayah_kode` | 0 |
| `periode` | 0 |
| `rincian` | 0 |
| `_berkas_raw` | 0 |
| `_sha256_raw` | 0 |

Contoh lima sel terisi beserta baris Silver asalnya:

| kode_prov | periode | indikator | _baris_silver | nilai Gold | nilai Silver | satuan Gold |
|---:|---|---|---:|---:|---:|---|
| 11 | 2015 | `var1241` | 0 | 88.96 | 88.96 | persen |
| 11 | 2016 | `var1241` | 1 | 90.91 | 90.91 | persen |
| 11 | 2017 | `var1241` | 2 | 92.01 | 92.01 | persen |
| 11 | 2017 | `var2012` | 393 | 52.7 | 52.7 | persen |
| 11 | 2017 | `var2013` | 463 | 2.02 | 2.02 | persen |

Kunci lineage lengkap tiga baris pertama:

```text
bps|var1241|1100|2015|Tidak ada|bps/2026-10-20/sdg11_11_1_1_a_v1241.csv
bps|var1241|1100|2016|Tidak ada|bps/2026-10-20/sdg11_11_1_1_a_v1241.csv
bps|var1241|1100|2017|Tidak ada|bps/2026-10-20/sdg11_11_1_1_a_v1241.csv
```

## 5. Kategori tabel rekonsiliasi

- Baris rekonsiliasi: **28**; berpasangan: **28**.
- Pasangan tanpa kategori: **0**.

| Kategori | Baris |
|---|---:|
| Metode berbeda | 14 |
| Cakupan berbeda | 10 |
| Definisi berbeda | 4 |
