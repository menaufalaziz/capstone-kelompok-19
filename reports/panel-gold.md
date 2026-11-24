# Panel Gold provinsi × periode × indikator

Dihasilkan otomatis oleh `python pipeline.py` (`src/gold/panel.py`) untuk Sprint 2 (Tahap 4).
Penanggung jawab komponen: **Riska Erlis (NIM: 124450022)** — Profil dan Pembersihan / Persiapan Gold.

## Aturan satu nilai per sel

1. **Snapshot**: seri yang tersedia di dua snapshot memakai snapshot terbaru (2026-10-20); data snapshot 17 Oktober 2026 byte-identik.
2. **Rincian**: panel memuat 7 indikator tingkat provinsi terpilih (var1241, var2012, var2013, var2753 Bongkar/Muat, var2754 Bongkar/Muat). Baris agregat nasional (wilayah_kode 9999) dan pembanding WDI dialokasikan ke tabel nasional Gold.
   - Baris Silver yang tidak masuk panel provinsi: **37 baris** (seluruh 37 baris nasional/WDI).
   - Baris Silver provinsi yang tidak terpilih: **0 baris** (100% dari 1.258 baris provinsi di Silver terpilih masuk ke panel).
3. **Periode**: seluruh indikator bertipe tahunan; periode 4 digit disimpan apa adanya (`jenis_periode = 'tahun'`); tidak ada interpolasi pada tahun kosong.
4. **Penanda**: penanda patahan metodologi (var1241 tahun 2019), patahan wilayah (Papua 2024), dan outlier asli (85 calon anomali terkonfirmasi) dari Sprint 1 dibawa ke kolom `penanda`; nilai asli tidak diubah.
5. **Skala dan Transformasi**: nilai asli kargo dipertahankan pada kolom `nilai` (var2753 bersatuan ton, var2754 bersatuan kg). Kolom turunan `nilai_log` ditambahkan dengan transformasi natural logaritma `log1p(nilai)` untuk memudahkan pemodelan seri bermagnitudo besar.
6. **Sel Kosong**: 72 sel kosong dipertahankan dengan kategori eksplisit (`belum_ada`, `tidak_diterbitkan`, `batas_lama`) untuk transparansi kelengkapan data.

## Ringkasan Indikator Panel

| indikator | satuan | periode | jumlah_periode | total_sel | terisi | ditandai |
|---|---|---|---|---|---|---|
| var1241 | persen | 2015–2025 | 11 | 418 | 382 | 35 |
| var2012 | persen | 2017–2020 | 2 | 76 | 68 | 0 |
| var2013 | persen | 2017–2020 | 2 | 76 | 68 | 4 |
| var2753 [Bongkar] | ton | 2021–2025 | 5 | 190 | 180 | 18 |
| var2753 [Muat] | ton | 2021–2025 | 5 | 190 | 180 | 15 |
| var2754 [Bongkar] | kilogram | 2021–2025 | 5 | 190 | 190 | 25 |
| var2754 [Muat] | kilogram | 2021–2025 | 5 | 190 | 190 | 23 |

## Distribusi Status Sel

| indikator | batas_lama | belum_ada | terisi | tidak_diterbitkan |
|---|---|---|---|---|
| var1241 | 4 | 32 | 382 | 0 |
| var2012 | 0 | 8 | 68 | 0 |
| var2013 | 0 | 8 | 68 | 0 |
| var2753 [Bongkar] | 0 | 2 | 180 | 8 |
| var2753 [Muat] | 0 | 2 | 180 | 8 |
| var2754 [Bongkar] | 0 | 0 | 190 | 0 |
| var2754 [Muat] | 0 | 0 | 190 | 0 |

## Berkas Keluaran

- `data/gold/panel.parquet`: 1,330 baris (panjang, 1.258 terisi + 72 kosong).
- `data/gold/panel_lebar.parquet`: 394 baris × 11 kolom (lebar wilayah × periode).
