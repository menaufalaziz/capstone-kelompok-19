# Data Dictionary — Dokumentasi Silver dan Gold

Dokumen ini menjelaskan struktur kolom, tipe data, satuan, arti, dan asal data pada tabel Silver. Informasi diambil dari hasil pipeline, katalog seri, berkas mentah, dan keputusan yang tercatat dalam `log-keputusan.csv`.

## Katalog Seri

| Seri | Sumber | Nama di Berkas Mentah | Satuan Katalog | Satuan Final | Kode SDG | Dasar Penetapan |
|---|---|---|---|---|---|---|
| `var1241` | BPS | 11.1.1.(a) Persentase Rumah Tangga yang Memiliki Akses Terhadap Hunian Yang Layak Menurut Provinsi | persen | persen | 11.1.1 | JSON `var[0].unit` dan `var[0].label`; CSV kolom `satuan` |
| `var2012` | BPS | Persentase rumah tangga yang memiliki akses nyaman (jarak 0.5 km) ke transportasi umum menurut provinsi | tidak tersedia | persen | 11.2.1 | Judul tabel dan nama berkas `sdg11_11_2_1_a_v2012`; keputusan K-011 |
| `var2013` | BPS | Persentase penduduk berumur 10 tahun ke atas yang menggunakan kendaraan bermotor umum dengan rute tertentu menurut provinsi | tidak tersedia | persen | 11.2.1 | Judul tabel dan nama berkas `sdg11_11_2_1_b_v2013`; keputusan K-012 |
| `var2753` | BPS | 9.1.2* Jumlah Bongkar Muat Barang Moda Transportasi Kapal | kilogram | ton | 9.1.2 | Metadata KG dibandingkan dengan besaran publikasi BPS; keputusan K-013 |
| `var2754` | BPS | 9.1.2*. Jumlah Bongkar Muat Barang Moda Transportasi Pesawat Terbang | kilogram | kilogram | 9.1.2 | `var[0].unit = KG`; keputusan K-014 |
| `EN.POP.SLUM.UR.ZS` | WDI | Population living in slums (% of urban population) | tidak tersedia | persen | 11.1.1 | Judul indikator dan `sourceNote` WDI |

Koreksi satuan pada katalog hanya mengubah label satuan, bukan nilai mentah. Konversi satuan dilakukan di Gold (K-025: var2754 kilogram menjadi ton) dengan nilai asli tetap disimpan. Satuan final diambil dari `src/silver/katalog.py`, bukan dari kolom mentah. Semua seri tahunan; Silver tidak merata-ratakan periode semester/bulan ke tahunan. Keputusan K-007 (placeholder satuan 2012/2013) dan label KG pada K-003 disempurnakan oleh K-011, K-012, dan K-013 di `log-keputusan.csv`.

Seluruh seri menggunakan periode tahunan. Data semester atau bulanan tidak dirata-ratakan menjadi tahunan. Keputusan mengenai satuan dan periode tercatat dalam `log-keputusan.csv`, termasuk K-011 sampai K-016.

## Struktur Tabel Silver

Lokasi keluaran: `data/silver/silver.parquet`.

| Kolom | Tipe Data | Satuan/Format | Arti | Asal Data atau Aturan |
|---|---|---|---|---|
| `sumber` | string | `bps` atau `wdi` | Menunjukkan sumber data | Nama folder sumber pada `data/raw/` |
| `seri_kode` | string | Kode seri | Identitas indikator atau seri data | `var_id` BPS atau `indicator.id` WDI |
| `wilayah_kode` | integer | Kode wilayah | Kode identitas wilayah | `wilayah_id` BPS; WDI menggunakan kode `9999` untuk Indonesia |
| `nama_wilayah` | string | Nama wilayah | Nama provinsi atau wilayah pengamatan | `wilayah` BPS atau `country.value` WDI |
| `periode` | string | `YYYY` | Tahun pengamatan data | `tahun` BPS atau `date` WDI |
| `jenis_periode` | string | `tahun` | Jenis periode pengamatan | Kolom periode pada sumber BPS dan keputusan K-016 |
| `rincian` | string | Kategori sumber | Rincian kategori data, seperti Bongkar dan Muat | `turvar` BPS; WDI tidak memiliki rincian |
| `nilai` | float | Mengikuti satuan seri | Nilai hasil pengamatan indikator | `nilai` BPS atau `value` WDI |
| `satuan` | string | `persen`, `ton`, atau `kilogram` | Satuan pengukuran nilai | `src/silver/katalog.py` dan keputusan K-011 sampai K-015 |
| `_berkas_raw` | string | Path relatif `data/raw/` | Lokasi berkas mentah yang menjadi sumber baris Silver | Tahap ekstraksi |
| `_sha256_raw` | string | SHA-256, 64 karakter heksadesimal | Hash berkas mentah untuk memeriksa integritas dan keterlacakan sumber | `MANIFEST.csv` dan `src.common.manifest.sha256_raw` |
| `penanda_patahan` | string | Kosong atau `patahan_metodologi` | Menandai observasi yang mengalami patahan akibat perubahan metodologi pengukuran | Keputusan K-010 dalam `log-keputusan.csv`; diterapkan pada seri `var1241` tahun 2019 |

### Aturan dan Keterangan Data Silver

- Nilai dengan satuan persen berada pada rentang 0–100.
- Nilai bongkar muat tidak boleh negatif.
- Setiap seri menggunakan satuan yang konsisten dengan katalog.
- Kunci unik terdiri dari `sumber`, `seri_kode`, `wilayah_kode`, `periode`, `rincian`, dan `_berkas_raw`.
- Observasi kosong tidak dimasukkan sebagai baris bernilai.
- Penanda `patahan_metodologi` tidak mengubah nilai asli.

### Contoh Penelusuran Data (Data Lineage)

Satu baris Silver dapat ditelusuri ke berkas mentah menggunakan kolom `_berkas_raw` dan `_sha256_raw`.

Contoh data hasil pemeriksaan:

| Atribut | Nilai |
|---|---|
| `seri_kode` | `var1241` |
| `periode` | `2019` |
| `nilai` | `57.41` |
| `penanda_patahan` | `patahan_metodologi` |
| `_berkas_raw` | `bps/2026-10-20/sdg11_11_1_1_a_v1241.csv` |
| `_sha256_raw` | `d09667fcee3eaf2906cf501caef8f514ed662bb9d0040de1e2d13650d916f069` |

Berdasarkan contoh tersebut, baris Silver berasal dari berkas CSV BPS pada lokasi yang tercantum di `_berkas_raw`. Nilai `_sha256_raw` digunakan untuk mencocokkan integritas berkas dengan `MANIFEST.csv`.

Dengan demikian, sumber setiap baris Silver dapat ditelusuri tanpa mengubah data mentah.

## Ringkasan Tabel Silver

Hasil pipeline menghasilkan:

- Jumlah baris: 1.295.
- Jumlah seri: 6.
- Jumlah wilayah: 39.
- Jumlah berkas sumber: 6.
- Jumlah kolom: 12.
- Baris dengan penanda patahan metodologi: 35.

Rincian Bongkar dan Muat tetap disimpan sebagai baris terpisah. Pemilihan rincian yang sebanding, grid panel, dan rekonsiliasi pembanding dilakukan pada tahap Gold.

## data/gold/panel_<seri>.parquet

Satu tabel per seri utama (`panel_var1241`, `panel_var2012`, `panel_var2013`,
`panel_var2753`, `panel_var2754`). Satu baris = provinsi × periode × indikator.
Untuk var2753 dan var2754, Bongkar dan Muat menjadi indikator terpisah.

| Tabel | Baris | Indikator | Sel kosong | Satuan Gold | Satuan asli Silver |
|---|---:|---:|---:|---|---|
| `panel_var1241` | 418 | `var1241` | 36 | persen | persen |
| `panel_var2012` | 76 | `var2012` | 8 | persen | persen |
| `panel_var2013` | 76 | `var2013` | 8 | persen | persen |
| `panel_var2753` | 380 | `var2753_Bongkar`, `var2753_Muat` | 20 | ton | ton |
| `panel_var2754` | 380 | `var2754_Bongkar`, `var2754_Muat` | 0 | ton | kilogram |

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| kode_prov | int | kode BPS dua digit | tidak | 11–97 | `wilayah_kode // 100` | kunci provinsi |
| wilayah_kode | int | kode BPS × 100 | tidak | 1100–9700 | Silver | tidak memuat 9999 |
| nama_wilayah | string | huruf kapital | tidak | 38 nama provinsi | Silver | |
| periode | string | `YYYY` | tidak | 2015–2025 sesuai seri | Silver | semua tahunan |
| indikator | string | kunci indikator | tidak | `var1241`, `var2753_Bongkar`, dst. | aturan Gold | bagian kunci panel |
| nama_indikator | string | label sumber | tidak | nama katalog + rincian | `src/silver/katalog.py` | memudahkan pembacaan |
| rincian | string | kategori sumber | tidak | `Tidak ada`, `Bongkar`, `Muat` | Silver | |
| tingkat | string | — | tidak | `provinsi` | aturan Gold | agregat nasional tidak ada di tabel ini |
| sumber | string | — | tidak | `bps` | Silver | |
| seri_kode | string | kode seri sumber | tidak | `var1241` s.d. `var2754` | Silver | |
| satuan | string | satuan Gold | tidak | `persen`, `ton` | K-025 | satu satuan per tabel |
| satuan_asli | string | satuan Silver | tidak | `persen`, `ton`, `kilogram` | Silver | var2754 = kilogram |
| nilai | float | sesuai `satuan` | ya | persen 0–100; ton ≥ 0 | Silver + K-025 | nilai setelah konversi satuan |
| nilai_asli | float | sesuai `satuan_asli` | ya | ≥ 0 | Silver | nilai sebelum konversi |
| nilai_log10 | float | log10(nilai ton) | ya | hingga | K-026 | hanya terisi untuk indikator ton |
| penanda_patahan | string | label keputusan | tidak | `""`, `patahan_metodologi` | K-010 | seluruh grid var1241 2019 |
| _berkas_raw | string | path relatif `data/raw/` | ya | 5 berkas BPS | Silver | kosong pada sel grid |
| _sha256_raw | string | hex 64 karakter | ya | sha256 berkas | Silver | kosong pada sel grid |
| _baris_silver | int | indeks baris Silver 0-based | ya | 0–1.294 | aturan Gold | lineage sel terisi |
| _kunci_silver | string | kunci Silver dipisah `|` | ya | `sumber|seri|wilayah|periode|rincian|berkas` | aturan Gold | lineage sel terisi |

Kunci unik: `kode_prov + periode + indikator`. Sel tanpa observasi tetap ada
dengan `nilai`, `nilai_asli`, dan kolom lineage bernilai kosong (`NaN`); tidak
ada imputasi atau pengisian nol (K-005). Nilai ekstrem yang valid dipertahankan
(K-009). Agregat nasional 9999 tidak masuk panel provinsi (K-004) dan tetap
tersedia di Silver. Tabel ini adalah varian unit-safe; panel panjang
`panel.parquet` tetap mempertahankan satuan sumber per indikator.

## data/gold/panel_provinsi.parquet

Gabungan long kelima panel seri: 1.330 baris, 7 indikator, 38 provinsi,
72 sel kosong, dan 38 baris grid berpatahan (34 di antaranya terisi).
Kunci unik: `kode_prov + periode + indikator`.

Agar satu kolom nilai tidak mencampur satuan, nilai dipisah menjadi tiga kolom:

| Kolom | Tipe | Satuan | Keterangan |
|---|---|---|---|
| nilai_persen | float | persen | hanya terisi untuk indikator persen |
| nilai_ton | float | ton | hanya terisi untuk indikator bongkar muat |
| nilai_log10_ton | float | log10(ton) | hanya terisi untuk indikator bongkar muat |

Kolom lain sama dengan tabel per seri, kecuali `nilai`, `nilai_asli`,
`satuan_asli`, dan `nilai_log10` yang tidak diikutkan. Nilai asli tetap dapat
dibaca dari tabel per seri melalui `_baris_silver` atau `_kunci_silver`.
Dengan demikian setiap sel terisi dapat ditelusuri ke baris Silver asalnya,
sedangkan sel kosong tidak memiliki lineage.

## data/gold/panel.parquet

Panel panjang Gold tingkat provinsi x periode x indikator (1.330 baris: 1.258 terisi, 72 sel kosong berkategori).
Panel ini mempertahankan satuan sumber per indikator (var2754 kilogram) dan
menyediakan kolom `nilai_log`; untuk analisis yang tidak boleh mencampur satuan,
gunakan `panel_provinsi.parquet` yang sudah diseragamkan ke persen/ton.

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
