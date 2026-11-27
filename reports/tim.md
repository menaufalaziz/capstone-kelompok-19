# Laporan tim — <Nama tim>, kasus <NN> <judul kasus>

Satu dokumen bersama, enam bagian. Angka harus dapat ditarik ulang dari `data/silver`, `data/gold`,
dan `log-keputusan.csv` yang sudah di-*commit*.

## Ringkasan
Kasus, seri yang ditangani, dan satu kalimat temuan utama tentang kualitas datanya.

## Data dan lineage
Sumber dan format mentah, jumlah berkas, cara `_berkas_raw`/`_sha256_raw` dibentuk, dan hasil tarik
ulang API (bila dilakukan): apa yang berubah sejak snapshot 17–20 Oktober 2026.

## Masalah data dan penanganannya

Berbagai masalah kualitas data ditemukan selama proses profiling, pemeriksaan cakupan, dan pembersihan. Setiap masalah ditangani berdasarkan hasil pemeriksaan terhadap data sumber, metadata, serta perbandingan antarwilayah dan antarperiode. Keputusan penanganan beserta alternatif yang ditolak dicatat dalam `log-keputusan.csv`.

| Masalah | Jumlah baris/sel terdampak | Keputusan penanganan | Alternatif yang ditolak | ID log |
|---|---:|---|---|---|
| Missing atau kekosongan cakupan panel | 72 sel kosong pada 7 panel grid | Mempertahankan sel kosong sebagai `NaN` tanpa melakukan imputasi atau mengisinya dengan nol | Mengisi seluruh sel kosong dengan nol atau nilai estimasi | K-005 |
| Perbedaan cakupan wilayah | 20 sel kosong pada 2 panel var2753 (Bongkar dan Muat) | Memisahkan panel Bongkar dan Muat karena cakupan wilayahnya tidak mencakup seluruh 38 provinsi | Menggabungkan Bongkar dan Muat atau menyamakan cakupannya dengan var2754 | K-006 |
| Outlier atau calon anomali | 85 calon anomali (4 var2013, 33 var2753, dan 48 var2754) | Mempertahankan seluruh nilai ekstrem karena hasil pencocokan menunjukkan 85 nilai sesuai dengan data sumber BPS dan tidak ditemukan bukti kesalahan input. Seluruh kandidat dicatat dengan kategori `outlier asli` pada hasil klasifikasi | Mengoreksi nilai ekstrem tanpa bukti kesalahan sumber | K-009 |
| Patahan seri indikator hunian layak (var1241) | 34 provinsi terdampak | Mengategorikan penurunan serentak dari 2018 ke 2019 sebagai patahan seri. Rata-rata sederhana antarprovinsi turun dari 93,90% menjadi 54,14%, atau sebesar 39,77 poin persentase. Metadata BPS menyatakan bahwa sejak 2019 pengukuran menggunakan empat kriteria hunian layak. Nilai asli tetap dipertahankan tanpa koreksi | Menganggap penurunan serentak sebagai galat input dan mengubah nilai | K-010 |
| Pemeriksaan revisi atau kesamaan snapshot | 3 seri identik pada snapshot 17 dan 20 Oktober 2026 | Membandingkan kedua snapshot berdasarkan SHA-256. Tidak ditemukan perubahan atau revisi pada tiga seri yang tersedia di kedua snapshot. var2012 dan var2013 tidak dapat dibandingkan karena tidak tersedia pada snapshot 17 Oktober. Kedua snapshot tetap dipertahankan | Menghapus salah satu snapshot hanya karena isi datanya sama | K-008 |
| Format dan tipe data nilai | 10 baris pada var2753 | Mengonversi kolom `nilai` menjadi tipe numerik integer agar dapat diolah secara konsisten | Membiarkan kolom `nilai` bertipe teks atau object | K-003 |
| Penetapan satuan var2012 dan var2013 | 140 baris (masing-masing 70 baris) | Awalnya menggunakan placeholder karena satuan tidak tercantum pada metadata dan CSV BPS. Selanjutnya satuan kedua seri ditetapkan menjadi persen berdasarkan judul indikator dan pemeriksaan sumber; nilai tidak diubah | Mengarang satuan tanpa pemeriksaan sumber atau mempertahankan placeholder setelah bukti mendukung satuan persen | K-007, K-011, K-012 |
| Koreksi satuan var2753 | 370 baris | Menggunakan satuan `ton` berdasarkan pemeriksaan besaran nilai dan pembandingan dengan publikasi BPS. Nilai tidak dikonversi | Menggunakan satuan kilogram atau mengonversi seluruh nilai ke kilogram | K-013 |
| Identifikasi seri var2754 | 390 baris | Menetapkan bahwa var2754 merupakan seri bongkar muat barang moda transportasi pesawat terbang, bukan kapal. Satuan tetap kilogram | Menganggap var2753 dan var2754 sama-sama merupakan seri bongkar muat kapal | K-014 |
| Metadata seri pembanding WDI | 22 observasi | Menetapkan kode SDG 11.1.1 dan satuan persen untuk seri `EN.POP.SLUM.UR.ZS` berdasarkan metadata WDI | Membiarkan kode SDG kosong atau menggunakan satuan orang | K-015 |
| Konsistensi jenis periode | 0 baris yang memerlukan agregasi periode | Mempertahankan jenis periode tahunan sebagaimana tersedia pada sumber | Merata-ratakan data semester atau bulanan menjadi tahunan tanpa dasar | K-016 |
| Pemisahan rincian dan observasi Silver | 1.295 baris Silver | Mempertahankan rincian sesuai sumber dan memasukkan enam seri (lima seri BPS dan satu seri WDI). Observasi WDI tanpa nilai tidak dimasukkan ke Silver | Memilih hanya rincian Bongkar/Muat atau mengisi nilai WDI yang kosong di Silver | K-017 |

### Bukti pemeriksaan patahan seri var1241

Pemeriksaan khusus dilakukan terhadap indikator persentase rumah tangga yang memiliki akses terhadap hunian layak (var1241). Perbandingan dilakukan pada 34 provinsi yang memiliki data pada 2018 dan 2019. Hasilnya menunjukkan bahwa seluruh 34 provinsi mengalami penurunan nilai pada 2019 dibandingkan 2018.

Rata-rata sederhana antarprovinsi turun dari 93,90% pada 2018 menjadi 54,14% pada 2019, atau turun sebesar 39,77 poin persentase. Pemeriksaan metadata BPS menemukan keterangan bahwa sejak 2019 klasifikasi hunian layak menggunakan empat kriteria, yaitu kecukupan luas tempat tinggal, akses air minum layak, akses sanitasi layak, dan ketahanan bangunan.

Penurunan yang terjadi secara serentak di seluruh provinsi, disertai keterangan kriteria pengukuran sejak 2019, menjadi bukti pendukung bahwa perubahan tersebut lebih tepat dikategorikan sebagai patahan seri daripada galat input. Nilai asli tetap dipertahankan dan tidak dilakukan koreksi.

Data perbandingan setiap provinsi tersedia pada `reports/perbandingan_var1241_2018_2019.csv`, sedangkan keputusan penanganannya tercatat pada K-010 di `log-keputusan.csv`.

## Integrasi dan rekonsiliasi

Tahap integrasi dan rekonsiliasi (Tahap 6) bertujuan untuk memeriksa konsistensi eksternal antara seri utama BPS dan data pembanding internasional World Development Indicators (WDI), serta konsistensi internal antara agregat provinsi dan angka nasional BPS. Perbandingan dilakukan dengan mempertahankan nilai asli dari masing-masing sumber. Perbedaan nilai tidak dihapus atau dipaksakan menjadi sama, tetapi dianalisis berdasarkan definisi, metode, dan cakupan data.

Hasil rekonsiliasi disimpan dalam `data/gold/rekonsiliasi.parquet` dan `reports/tabel_rekonsiliasi.csv`. Tabel CSV memuat 28 baris hasil perbandingan yang terdiri atas 4 baris kategori Definisi berbeda, 14 baris Metode berbeda, dan 10 baris Cakupan berbeda. Pemeriksaan perbedaan vintage atau waktu rilis data dibahas secara terpisah karena tidak menjadi kategori pada 28 baris tabel tersebut.

### 1. Tabel Rekonsiliasi

Tabel berikut menyajikan pasangan data, periode, nilai utama, nilai pembanding, selisih nominal, persentase selisih, serta kategori penjelasan. Persentase selisih merupakan perbandingan aritmetis terhadap nilai pembanding. Khusus pasangan dengan definisi indikator berbeda, angka persentase hanya menunjukkan besarnya perbedaan secara numerik dan tidak dapat ditafsirkan sebagai ukuran kesenjangan substantif yang setara.

| Pasangan yang Dibandingkan | Periode | Nilai Seri Utama | Satuan Utama | Nilai Pembanding | Satuan Pembanding | Selisih Nominal | Persentase Selisih | Kategori |
|---|:---:|---:|:---:|---:|:---:|---:|---:|---|
| **var1241 (BPS Nasional) vs WDI EN.POP.SLUM.UR.ZS** | 2016 | 94,00 | % | 21,89 | % | +72,11 | +329,38% | Definisi berbeda |
| **var1241 (BPS Nasional) vs WDI EN.POP.SLUM.UR.ZS** | 2018 | 95,70 | % | 20,24 | % | +75,46 | +372,87% | Definisi berbeda |
| **var1241 (BPS Nasional) vs WDI EN.POP.SLUM.UR.ZS** | 2020 | 59,54 | % | 19,41 | % | +40,13 | +206,74% | Definisi berbeda |
| **var1241 (BPS Nasional) vs WDI EN.POP.SLUM.UR.ZS** | 2022 | 60,66 | % | 19,41 | % | +41,25 | +212,51% | Definisi berbeda |
| **var2754 Bongkar (Jumlah Provinsi vs BPS Nasional)** | 2021 | 622.546.815 | kg | 622.000.000 | kg | +546.815 | +0,09% | Metode berbeda |
| **var2754 Bongkar (Jumlah Provinsi vs BPS Nasional)** | 2022 | 577.765.577 | kg | 577.000.000 | kg | +765.577 | +0,13% | Metode berbeda |
| **var2754 Bongkar (Jumlah Provinsi vs BPS Nasional)** | 2023 | 580.939.961 | kg | 580.939.961 | kg | 0 | 0,00% | Metode berbeda |
| **var2754 Bongkar (Jumlah Provinsi vs BPS Nasional)** | 2024 | 689.283.176 | kg | 689.000.000 | kg | +283.176 | +0,04% | Metode berbeda |
| **var2754 Bongkar (Jumlah Provinsi vs BPS Nasional)** | 2025 | 674.547.332 | kg | 675.000.000 | kg | -452.668 | -0,07% | Metode berbeda |
| **var2754 Muat (Jumlah Provinsi vs BPS Nasional)** | 2021 | 602.068.213 | kg | 602.000.000 | kg | +68.213 | +0,01% | Metode berbeda |
| **var2754 Muat (Jumlah Provinsi vs BPS Nasional)** | 2022 | 642.439.246 | kg | 643.000.000 | kg | -560.754 | -0,09% | Metode berbeda |
| **var2754 Muat (Jumlah Provinsi vs BPS Nasional)** | 2023 | 601.762.588 | kg | 601.762.588 | kg | 0 | 0,00% | Metode berbeda |
| **var2754 Muat (Jumlah Provinsi vs BPS Nasional)** | 2024 | 674.735.003 | kg | 675.000.000 | kg | -264.997 | -0,04% | Metode berbeda |
| **var2754 Muat (Jumlah Provinsi vs BPS Nasional)** | 2025 | 670.710.328 | kg | 671.000.000 | kg | -289.672 | -0,04% | Metode berbeda |
| **var2012 Moda Transportasi (Rerata Provinsi vs BPS Nasional)** | 2017 | 57,98 | % | 54,67 | % | +3,31 | +6,05% | Metode berbeda |
| **var2012 Moda Transportasi (Rerata Provinsi vs BPS Nasional)** | 2020 | 59,24 | % | 56,01 | % | +3,23 | +5,76% | Metode berbeda |
| **var2013 Kemacetan/Angkutan (Rerata Provinsi vs BPS Nasional)** | 2017 | 4,00 | % | 4,85 | % | -0,85 | -17,55% | Metode berbeda |
| **var2013 Kemacetan/Angkutan (Rerata Provinsi vs BPS Nasional)** | 2020 | 5,05 | % | 5,74 | % | -0,69 | -12,09% | Metode berbeda |
| **var2753 Bongkar (Agregat 36 Provinsi)** | 2021 | 399.325.458 | ton | Tidak tersedia | ton | N/A | N/A | Cakupan berbeda |
| **var2753 Bongkar (Agregat 36 Provinsi)** | 2022 | 392.927.647 | ton | Tidak tersedia | ton | N/A | N/A | Cakupan berbeda |
| **var2753 Bongkar (Agregat 36 Provinsi)** | 2023 | 358.100.371 | ton | Tidak tersedia | ton | N/A | N/A | Cakupan berbeda |
| **var2753 Bongkar (Agregat 36 Provinsi)** | 2024 | 396.389.965 | ton | Tidak tersedia | ton | N/A | N/A | Cakupan berbeda |
| **var2753 Bongkar (Agregat 36 Provinsi)** | 2025 | 451.664.125 | ton | Tidak tersedia | ton | N/A | N/A | Cakupan berbeda |
| **var2753 Muat (Agregat 36 Provinsi)** | 2021 | 384.784.258 | ton | Tidak tersedia | ton | N/A | N/A | Cakupan berbeda |
| **var2753 Muat (Agregat 36 Provinsi)** | 2022 | 398.095.203 | ton | Tidak tersedia | ton | N/A | N/A | Cakupan berbeda |
| **var2753 Muat (Agregat 36 Provinsi)** | 2023 | 385.612.407 | ton | Tidak tersedia | ton | N/A | N/A | Cakupan berbeda |
| **var2753 Muat (Agregat 36 Provinsi)** | 2024 | 433.733.968 | ton | Tidak tersedia | ton | N/A | N/A | Cakupan berbeda |
| **var2753 Muat (Agregat 36 Provinsi)** | 2025 | 508.550.340 | ton | Tidak tersedia | ton | N/A | N/A | Cakupan berbeda |

### 2. Analisis dan Penjelasan Setiap Kategori

#### A. Definisi Berbeda: var1241 (BPS) vs WDI EN.POP.SLUM.UR.ZS

Pasangan ini membandingkan indikator hunian layak BPS dengan indikator kawasan kumuh perkotaan dari WDI pada empat tahun irisan, yaitu 2016, 2018, 2020, dan 2022.

- BPS `var1241` mengukur persentase rumah tangga yang memiliki akses terhadap hunian layak. Nilai yang lebih tinggi menunjukkan proporsi rumah tangga dengan hunian layak yang lebih besar.
- WDI `EN.POP.SLUM.UR.ZS` mengukur persentase penduduk perkotaan yang tinggal di kawasan kumuh. Nilai yang lebih tinggi menunjukkan proporsi penduduk perkotaan yang tinggal di kawasan kumuh lebih besar.
- Kedua indikator memiliki konsep, unit observasi, dan arah interpretasi yang berbeda. Oleh karena itu, selisih nominal maupun persentase selisih pada tabel tidak dapat dianggap sebagai perbandingan langsung atas ukuran kondisi yang sama.

Berdasarkan perubahan antarperiode:

- **2016–2018:** Nilai BPS naik dari 94,00% menjadi 95,70%, atau meningkat 1,70 poin persentase. Pada periode yang sama, nilai WDI turun dari 21,89% menjadi 20,24%, atau turun 1,65 poin persentase. Arah perubahan kedua indikator tersebut sejalan dengan indikasi perbaikan kondisi hunian.
- **2018–2020:** Nilai BPS turun dari 95,70% menjadi 59,54%, sedangkan WDI turun dari 20,24% menjadi 19,41%. Penurunan BPS perlu dibaca dengan mempertimbangkan patahan seri metodologi var1241 yang didokumentasikan pada keputusan K-010. Sejak 2019, pengukuran hunian layak menggunakan empat kriteria, yaitu kecukupan luas tempat tinggal, akses air minum layak, akses sanitasi layak, dan ketahanan bangunan.
- **2020–2022:** Nilai BPS naik dari 59,54% menjadi 60,66%, sedangkan nilai WDI tetap sebesar 19,41% pada data yang digunakan.

Dengan demikian, perbedaan nilai BPS dan WDI terutama perlu dijelaskan melalui perbedaan definisi, unit observasi, dan patahan seri BPS. Selisih numerik pada tabel tidak boleh ditafsirkan sebagai besarnya perbedaan kondisi hunian secara langsung.

#### B. Metode Berbeda: var2754, var2012, dan var2013

**1. Kargo udara var2754 (Bongkar dan Muat)**

Rekonsiliasi var2754 membandingkan penjumlahan nilai provinsi dengan nilai nasional BPS pada periode 2021–2025.

- Pada 2023, hasil penjumlahan provinsi sama dengan angka nasional BPS. Selisih untuk Bongkar dan Muat masing-masing sebesar 0 kg.
- Pada 2021, 2022, 2024, dan 2025 terdapat selisih antara agregat provinsi dan angka nasional BPS. Selisih relatifnya berkisar antara -0,07% hingga +0,13%.
- Selisih tersebut relatif kecil dibandingkan nilai total kargo yang mencapai ratusan juta kilogram.
- Salah satu kemungkinan penjelasan adalah pembulatan pada angka nasional dalam berkas sumber, sedangkan agregat provinsi dihitung dari penjumlahan nilai provinsi. Namun, pembulatan sebagai penyebab selisih masih merupakan dugaan dan tidak dinyatakan sebagai kepastian tanpa dokumentasi metode sumber.

**2. Indikator var2012 dan var2013**

Pada var2012 dan var2013, nilai pembanding dihitung dari rata-rata sederhana (*unweighted mean*) antarprovinsi, kemudian dibandingkan dengan angka nasional BPS.

- Pada var2012, rata-rata provinsi lebih tinggi daripada angka nasional BPS. Selisihnya sebesar 3,31 poin persentase pada 2017 dan 3,23 poin persentase pada 2020.
- Pada var2013, rata-rata provinsi lebih rendah daripada angka nasional BPS. Selisihnya sebesar -0,85 poin persentase pada 2017 dan -0,69 poin persentase pada 2020.
- Rata-rata sederhana memberikan bobot yang sama kepada setiap provinsi, sedangkan angka nasional BPS berasal dari metode agregasi nasional. Perbedaan pendekatan agregasi tersebut dapat menghasilkan nilai yang berbeda.
- Dasar pembobotan atau rincian metode agregasi nasional tidak disimpulkan lebih jauh tanpa dokumentasi sumber yang mendukung.

#### C. Cakupan Berbeda: Kargo laut var2753

Seri kargo laut var2753 (Bongkar dan Muat) memiliki data dari 36 provinsi pada periode 2021–2025. Berkas sumber BPS yang digunakan tidak menyediakan baris ringkasan nasional `INDONESIA` untuk seri ini.

Oleh karena itu:

- Nilai agregat provinsi dihitung dengan menjumlahkan data dari 36 provinsi yang tersedia.
- Tidak terdapat nilai nasional BPS yang dapat digunakan sebagai pembanding langsung.
- Selisih nominal dan persentase selisih tidak dapat dihitung karena nilai pembanding nasional tidak tersedia.
- Panel Bongkar dan Muat tetap dipisahkan sesuai perbedaan cakupan data dan keputusan K-006.

Hasil agregat tersebut merupakan penjumlahan provinsi yang memiliki data, bukan angka nasional resmi yang diterbitkan BPS. Karena itu, interpretasinya harus mempertimbangkan cakupan wilayah yang tersedia.

#### D. Pemeriksaan Vintage atau Perbedaan Waktu Rilis Data

Selain tiga kategori yang muncul dalam tabel, pemeriksaan juga memperhatikan perbedaan waktu rilis (*vintage*) antara sumber data.

- Data BPS yang digunakan berasal dari snapshot 20 Oktober 2026.
- Data WDI yang digunakan berasal dari arsip snapshot 8 Oktober 2026.
- Perbedaan tanggal snapshot dicatat sebagai konteks waktu pengambilan data. Perbedaan tanggal tersebut tidak dengan sendirinya membuktikan adanya revisi nilai.
- Pemeriksaan vintage dibedakan dari 28 baris rekonsiliasi karena tidak menjadi kategori pada kolom `kategori` dalam CSV.

Dengan demikian, pembahasan vintage berfungsi sebagai informasi tambahan mengenai asal dan waktu pengambilan data, bukan sebagai kategori tambahan yang mengubah jumlah 28 baris hasil rekonsiliasi.

### 3. Keterlacakan Data dan Log Keputusan

Hasil rekonsiliasi dapat ditelusuri kembali melalui berkas Gold, tabel CSV, dan log keputusan yang berkaitan dengan proses integrasi dan pembersihan data.

Berkas utama yang digunakan:

- **Parquet Gold:** `data/gold/rekonsiliasi.parquet`, berisi 28 baris hasil rekonsiliasi.
- **Tabel CSV:** `reports/tabel_rekonsiliasi.csv`, berisi pasangan, periode, nilai utama, nilai pembanding, selisih, persentase selisih, kategori, dan penjelasan.
- **Log keputusan:** `log-keputusan.csv`, berisi dasar keputusan pengolahan dan penanganan data.

Keputusan yang berkaitan dengan hasil rekonsiliasi antara lain:

- `K-002`: Pemisahan baris agregat nasional `INDONESIA` (9999) pada var2753 untuk mencegah penghitungan ganda.
- `K-006`: Pemisahan panel var2753 dan var2754 karena perbedaan cakupan data transportasi laut dan udara.
- `K-009`: Klasifikasi 85 calon anomali yang dipertahankan karena sesuai dengan data sumber.
- `K-010`: Dokumentasi patahan seri metodologi var1241 sejak 2019.
- `K-013`: Penetapan satuan ton pada var2753.
- `K-014`: Identifikasi var2754 sebagai seri bongkar muat barang moda transportasi pesawat terbang.
- `K-015`: Penetapan kode SDG 11.1.1 dan satuan persen pada seri WDI `EN.POP.SLUM.UR.ZS`.
- `K-019`: Pengaturan alokasi data nasional Gold.
- `K-024`: Penyusunan tabel rekonsiliasi 28 baris dan penetapan kategori penjelasan tanpa mengubah data asli.

Dengan rujukan tersebut, angka pada tabel dapat ditelusuri melalui hasil pengolahan Gold dan keputusan yang mendasari proses integrasi. Nilai sumber tetap dipertahankan, sedangkan perbedaan dijelaskan berdasarkan hasil pemeriksaan dan keterbatasan data yang tersedia.

## Validasi dan reproduksibilitas
Skema validasi (aturan, hasil lolos/gagal), waktu `python pipeline.py` dari nol, perbandingan pandas
vs DuckDB/Dask, dan keterbatasan yang tersisa.

## Pembagian kerja
| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|
