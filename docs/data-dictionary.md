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

Koreksi satuan pada katalog hanya mengubah label satuan, bukan nilai mentah. Konversi satuan, apabila diperlukan, dilakukan pada tahap Gold. Satuan final diambil dari `src/silver/katalog.py`.

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

## Struktur Tabel Gold

Kolom pada tabel Gold akan didokumentasikan setelah proses pembentukan tabel Gold pada Sprint 2–3 selesai. Dokumentasi akan dilengkapi berdasarkan struktur dan hasil data aktual.