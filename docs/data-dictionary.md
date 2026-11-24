# Data dictionary — <Kelompok 19>

Satu tabel per keluaran (Silver dan setiap tabel Gold). Isi dari data nyata, bukan dari ingatan:
tipe, satuan, rentang, dan jumlah kosong dihitung ulang setiap kali pipeline berjalan.

## Katalog seri (satuan dan kode SDG)

Hasil audit terhadap judul tabel dan metadata berkas mentah. Sumber kebenaran kode:
`src/silver/katalog.py`; periksa ulang dengan `python -m src.silver.katalog`.
`data/KASUS.md` tidak diubah karena berkas unduhan (akan tertimpa `unduh_data.py`).

| Seri | Sumber | Nama di berkas mentah | Satuan katalog | Satuan final | Kode SDG | Dasar (berkas/field) |
|---|---|---|---|---|---|---|
| `var1241` | bps | 11.1.1.(a) Persentase Rumah Tangga yang Memiliki Akses Terhadap Hunian Yang Layak Menurut Provinsi | persen | persen | 11.1.1 | JSON `var[0].unit` dan `var[0].label`; CSV kolom `satuan`; nilai 4,44–99,49 |
| `var2012` | bps | Persentase rumah tangga yang memiliki akses nyaman (jarak 0.5 km) ke transportasi umum menurut provinsi | tidak_ada | persen | 11.2.1 | judul "Persentase", `var[0].unit` kosong, kolom `satuan` kosong, nilai 33,58–84,87; kode dari nama berkas `sdg11_11_2_1_a_v2012` |
| `var2013` | bps | Persentase penduduk berumur 10 tahun ke atas yang menggunakan kendaraan bermotor umum dengan rute tertentu menurut provinsi | tidak_ada | persen | 11.2.1 | judul "Persentase", `var[0].unit` kosong, kolom `satuan` kosong, nilai 0,52–15,83; kode dari nama berkas `sdg11_11_2_1_b_v2013` |
| `var2753` | bps | 9.1.2* Jumlah Bongkar Muat Barang Moda Transportasi Kapal | kilogram | ton | 9.1.2 | metadata dan kolom `satuan` sama-sama `KG`, tetapi besaran menunjukkan ton: nasional 2022 = 393.000.000; bongkar Kaltara 2022 = 2.932.021 vs publikasi BPS 2.841.459 ton; `var[0].label` diawali `9.1.2*` |
| `var2754` | bps | 9.1.2*. Jumlah Bongkar Muat Barang Moda Transportasi Pesawat Terbang | kilogram | kilogram | 9.1.2 | `var[0].unit = KG`; nilai nasional 2022 = 577 juta kg atau sekitar 577 ribu ton, sejalan kargo udara nasional; nama katalog dikoreksi: pesawat, bukan kapal |
| `EN.POP.SLUM.UR.ZS` | wdi | Population living in slums (% of urban population) | — | persen | 11.1.1 | judul "% of urban population", `unit` kosong, nilai 19,41–35,13; `sourceNote` WDI menyebut Sustainable Development Goal 11.1.1 |

Koreksi satuan hanya mengubah label, bukan nilai mentah. Konversi (mis. ton ke kg) dilakukan di Gold
bila diperlukan. `src/silver/bangun.py` mengambil `satuan` dari katalog ini, bukan dari kolom mentah.
Semua seri tahunan; Silver tidak merata-ratakan periode semester/bulan ke tahunan.
Keputusan K-007 (placeholder satuan 2012/2013) dan label KG pada K-003 disempurnakan oleh K-011,
K-012, dan K-013 di `log-keputusan.csv`.

## data/silver/silver.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | `bps`, `wdi` | nama folder data/raw | |
| seri_kode | string | kode seri sumber | tidak | `1241`, `2012`, `2013`, `2753`, `2754`, `EN.POP.SLUM.UR.ZS` | `var_id` BPS; `indicator.id` WDI | |
| wilayah_kode | int | kode BPS x 100 | tidak | 9999 atau 1100–9700 | `wilayah_id`; WDI = 9999 | 9999 = Indonesia |
| nama_wilayah | string | huruf kapital | tidak | nama wilayah sumber | `wilayah` BPS; `country.value` WDI | |
| periode | string | `YYYY` | tidak | 2000–2025 | `tahun` BPS; `date` WDI | semua seri tahunan |
| jenis_periode | string | — | tidak | `tahun` | kolom `periode` BPS | tidak ada periode semester/bulan (K-016) |
| rincian | string | kategori sumber | tidak | `Tidak ada`, `Bongkar`, `Muat` | `turvar` BPS; WDI tidak punya rincian | disimpan apa adanya untuk dipilih di Gold |
| nilai | float | sesuai `satuan` | tidak | ≥ 0; persen 0–100 | `nilai` BPS; `value` WDI | observasi kosong tidak dimasukkan |
| satuan | string | — | tidak | `persen`, `ton`, `kilogram` | `src/silver/katalog.py` | koreksi label K-011 s.d. K-015 |
| _berkas_raw | string | path relatif `data/raw/` | tidak | 6 berkas | tahap ekstraksi | satu seri memakai satu berkas CSV/WDI |
| _sha256_raw | string | hex 64 karakter | tidak | sha256 berkas | `src.common.manifest.sha256_raw` | lineage ke MANIFEST.csv |
| penanda_patahan | string | label keputusan | tidak (string kosong) | `""`, `patahan_metodologi` | aturan K-010 di `src/silver/bangun.py` | 35 baris var1241 tahun 2019; nilai asli tidak diubah |

Kunci unik: `sumber + seri_kode + wilayah_kode + periode + rincian + _berkas_raw`.
Silver Sprint 1 berisi 1.295 baris: 1.283 baris BPS dan 12 observasi WDI bernilai.
Sebanyak 35 baris var1241 tahun 2019 diberi `penanda_patahan = patahan_metodologi` (K-010);
kolom ini hanya penanda, bukan perubahan nilai.
Rincian Bongkar/Muat tetap menjadi baris terpisah; pemilihan rincian yang sebanding,
grid 38 provinsi, dan rekonsiliasi pembanding dikerjakan di Gold (Sprint 2).

## data/gold/panel.parquet

Panel panjang Gold tingkat provinsi x periode x indikator (1.330 baris: 1.258 terisi, 72 sel kosong berkategori).

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| indikator | string | nama indikator panel | tidak | 7 indikator panel | `src/gold/panel.py` | `var1241`, `var2012`, `var2013`, `var2753 [Bongkar]`, `var2753 [Muat]`, `var2754 [Bongkar]`, `var2754 [Muat]` |
| seri_kode | string | kode seri sumber | tidak | `var1241`, `var2012`, `var2013`, `var2753`, `var2754` | Silver `seri_kode` | Seri dasar BPS |
| rincian | string | kategori arus / placeholder | tidak | `Tidak ada`, `Bongkar`, `Muat` | Silver `rincian` | Rincian terpilih |
| wilayah_kode | int | kode provinsi BPS x 100 | tidak | 1100–9700 (38 provinsi) | Silver `wilayah_kode` | Susunan 38 provinsi standar 2025 |
| nama_wilayah | string | teks baku | tidak | 38 nama provinsi | Kamus wilayah | Nama resmi provinsi |
| periode | string | `YYYY` | tidak | 2015–2025 | Silver `periode` | Periode tahunan empat digit |
| jenis_periode | string | — | tidak | `tahun` | Silver `jenis_periode` | Seluruh seri tahunan |
| nilai | float | sesuai `satuan` | ya (hanya sel kosong) | ≥ 0; persen 0–100 | Silver `nilai` | Nilai asli tidak diubah; NaN bila sel kosong |
| satuan | string | — | tidak | `persen`, `ton`, `kilogram` | Silver `satuan` | Satuan baku indikator |
| status_sel | string | kategori status sel | tidak | `terisi`, `belum_ada`, `tidak_diterbitkan`, `batas_lama` | `src/gold/panel.py` | Transparansi kelengkapan grid |
| penanda | string | label anomali/patahan | ya | `patahan_seri`, `patahan_wilayah`, `outlier` | Sprint 1 profil & anomali | Penanda anomali tanpa mengubah nilai |
| nilai_log | float | logaritma natural | ya | ≥ 0 | `np.log1p(nilai)` | Transformasi ln(1 + nilai) untuk kargo besar |
| _berkas_raw | string | path relatif `data/raw/` | ya (hanya sel terisi) | 5 berkas BPS | Silver `_berkas_raw` | Lineage berkas mentah |
| _sha256_raw | string | hex 64 karakter | ya (hanya sel terisi) | sha256 berkas | Silver `_sha256_raw` | Lineage integritas data |

Kunci unik: `indikator + wilayah_kode + periode`.

## data/gold/panel_lebar.parquet

Panel lebar Gold tingkat provinsi x periode (394 baris x 11 kolom). Hanya memuat baris terisi (`status_sel == 'terisi'`).

| Kolom | Tipe | Keterangan |
|---|---|---|
| wilayah_kode | int | Kode provinsi BPS (1100–9700) |
| nama_wilayah | string | Nama resmi 38 provinsi |
| jenis_periode | string | Jenis periode (`tahun`) |
| periode | string | Tahun observasi (`YYYY`) |
| var1241 | float | Persentase rumah tangga hunian layak (persen) |
| var2012 | float | Akses transportasi umum nyaman jarak 0,5 km (persen) |
| var2013 | float | Penduduk 10+ pengguna kendaraan umum rute tetap (persen) |
| var2753 [Bongkar] | float | Bongkar kargo moda kapal laut (ton) |
| var2753 [Muat] | float | Muat kargo moda kapal laut (ton) |
| var2754 [Bongkar] | float | Bongkar kargo moda pesawat terbang (kilogram) |
| var2754 [Muat] | float | Muat kargo moda pesawat terbang (kilogram) |

Kunci unik: `wilayah_kode + periode`.
