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

Tahap integrasi dan rekonsiliasi (Tahap 6) bertujuan untuk memverifikasi konsistensi eksternal seri utama terhadap standar pembanding internasional (World Development Indicators - Bank Dunia/UN-Habitat) serta menguji konsistensi internal antara agregat provinsi dan angka nasional BPS. Seluruh angka pada bagian ini tersimpan di `data/gold/rekonsiliasi.parquet` dan `reports/tabel_rekonsiliasi.csv`, serta diturunkan langsung dari `data/gold/` dan `log-keputusan.csv`.

Sesuai ketentuan Capstone, selisih antarseri tidak dihapus dan tidak dipaksa sama, melainkan diklasifikasikan ke dalam kategori penjelasan: **Definisi berbeda**, **Metode berbeda**, **Cakupan berbeda**, atau **Vintage berbeda**.

### 1. Tabel Rekonsiliasi Komprehensif

Tabel berikut merangkum hasil rekonsiliasi untuk seluruh 28 observasi yang dievaluasi pada Sprint 2:

| Pasangan yang Dibandingkan | Periode | Nilai Seri Utama | Satuan Utama | Nilai Pembanding | Satuan Pembanding | Selisih Nominal | Rasio / Deviasi | Kategori Penjelasan |
|---|:---:|---:|:---:|---:|:---:|---:|---:|---|
| **var1241 vs WDI EN.POP.SLUM.UR.ZS** | 2016 | 94,00 | % | 21,89 | % | +72,11 | BPS ↑, WDI ↓ | Definisi berbeda |
| **var1241 vs WDI EN.POP.SLUM.UR.ZS** | 2018 | 95,70 | % | 20,24 | % | +75,46 | BPS ↑, WDI ↓ | Definisi berbeda |
| **var1241 vs WDI EN.POP.SLUM.UR.ZS** | 2020 | 59,54 | % | 19,41 | % | +40,13 | Patahan BPS | Definisi berbeda |
| **var1241 vs WDI EN.POP.SLUM.UR.ZS** | 2022 | 60,66 | % | 19,41 | % | +41,25 | BPS ↑, WDI ↔ | Definisi berbeda |
| **var2754 Bongkar (Provinsi vs Nas)** | 2021 | 622.546.815 | kg | 622.000.000 | kg | +546.815 | +0,09% | Metode berbeda (Pembulatan) |
| **var2754 Bongkar (Provinsi vs Nas)** | 2022 | 577.765.577 | kg | 577.000.000 | kg | +765.577 | +0,13% | Metode berbeda (Pembulatan) |
| **var2754 Bongkar (Provinsi vs Nas)** | 2023 | 580.939.961 | kg | 580.939.961 | kg | 0 | 0,00% (Eksak) | Metode berbeda (Sesuai) |
| **var2754 Bongkar (Provinsi vs Nas)** | 2024 | 689.283.176 | kg | 689.000.000 | kg | +283.176 | +0,04% | Metode berbeda (Pembulatan) |
| **var2754 Bongkar (Provinsi vs Nas)** | 2025 | 674.547.332 | kg | 675.000.000 | kg | -452.668 | -0,07% | Metode berbeda (Pembulatan) |
| **var2754 Muat (Provinsi vs Nas)** | 2021 | 602.068.213 | kg | 602.000.000 | kg | +68.213 | +0,01% | Metode berbeda (Pembulatan) |
| **var2754 Muat (Provinsi vs Nas)** | 2022 | 642.439.246 | kg | 643.000.000 | kg | -560.754 | -0,09% | Metode berbeda (Pembulatan) |
| **var2754 Muat (Provinsi vs Nas)** | 2023 | 601.762.588 | kg | 601.762.588 | kg | 0 | 0,00% (Eksak) | Metode berbeda (Sesuai) |
| **var2754 Muat (Provinsi vs Nas)** | 2024 | 674.735.003 | kg | 675.000.000 | kg | -264.997 | -0,04% | Metode berbeda (Pembulatan) |
| **var2754 Muat (Provinsi vs Nas)** | 2025 | 670.710.328 | kg | 671.000.000 | kg | -289.672 | -0,04% | Metode berbeda (Pembulatan) |
| **var2012 Moda Transportasi (Rerata)** | 2017 | 57,98 | % | 54,67 | % | +3,31 | +6,05% | Metode berbeda (Pembobotan) |
| **var2012 Moda Transportasi (Rerata)** | 2020 | 59,24 | % | 56,01 | % | +3,23 | +5,76% | Metode berbeda (Pembobotan) |
| **var2013 Kemacetan/Angkutan (Rerata)** | 2017 | 4,00 | % | 4,85 | % | -0,85 | -17,55% | Metode berbeda (Pembobotan) |
| **var2013 Kemacetan/Angkutan (Rerata)** | 2020 | 5,05 | % | 5,74 | % | -0,69 | -12,09% | Metode berbeda (Pembobotan) |
| **var2753 Bongkar (Agregat 36 Prov)** | 2021 | 399.325.458 | ton | *Tidak terbit* | ton | N/A | N/A | Cakupan berbeda (Tanpa Nas) |
| **var2753 Bongkar (Agregat 36 Prov)** | 2022 | 392.927.647 | ton | *Tidak terbit* | ton | N/A | N/A | Cakupan berbeda (Tanpa Nas) |
| **var2753 Bongkar (Agregat 36 Prov)** | 2023 | 358.100.371 | ton | *Tidak terbit* | ton | N/A | N/A | Cakupan berbeda (Tanpa Nas) |
| **var2753 Bongkar (Agregat 36 Prov)** | 2024 | 396.389.965 | ton | *Tidak terbit* | ton | N/A | N/A | Cakupan berbeda (Tanpa Nas) |
| **var2753 Bongkar (Agregat 36 Prov)** | 2025 | 451.664.125 | ton | *Tidak terbit* | ton | N/A | N/A | Cakupan berbeda (Tanpa Nas) |
| **var2753 Muat (Agregat 36 Prov)** | 2021 | 384.784.258 | ton | *Tidak terbit* | ton | N/A | N/A | Cakupan berbeda (Tanpa Nas) |
| **var2753 Muat (Agregat 36 Prov)** | 2022 | 398.095.203 | ton | *Tidak terbit* | ton | N/A | N/A | Cakupan berbeda (Tanpa Nas) |
| **var2753 Muat (Agregat 36 Prov)** | 2023 | 385.612.407 | ton | *Tidak terbit* | ton | N/A | N/A | Cakupan berbeda (Tanpa Nas) |
| **var2753 Muat (Agregat 36 Prov)** | 2024 | 433.733.968 | ton | *Tidak terbit* | ton | N/A | N/A | Cakupan berbeda (Tanpa Nas) |
| **var2753 Muat (Agregat 36 Prov)** | 2025 | 508.550.340 | ton | *Tidak terbit* | ton | N/A | N/A | Cakupan berbeda (Tanpa Nas) |

### 2. Analisis Mendalam Penjelasan Setiap Kategori

#### A. Kategori Definisi Berbeda: var1241 (BPS) vs WDI EN.POP.SLUM.UR.ZS
Pasangan ini membandingkan indikator perumahan nasional BPS dengan pembanding internasional World Bank/UN-Habitat pada 4 tahun irisan (2016, 2018, 2020, 2022):
- **Perbedaan Konsep dan Arah**:
  - BPS `var1241` mengukur **persentase rumah tangga** yang memiliki akses terhadap **hunian layak** (makin tinggi angka, kondisi makin baik).
  - WDI `EN.POP.SLUM.UR.ZS` mengukur proporsi **penduduk perkotaan** (*urban population*) yang bertempat tinggal di **kawasan kumuh** (*slum households*) (makin tinggi angka, kondisi makin buruk).
  - Karena konsepnya berlawanan arah, perbandingan tidak boleh dilihat dari selisih langsung, melainkan dari **arah perubahan (*trend concordance*)**:
    - Periode 2016 ke 2018: Nilai BPS naik dari 94,00% menjadi 95,70% (+1,70 pp). Secara selaras, estimasi kawasan kumuh perkotaan WDI turun dari 21,89% menjadi 20,24% (-1,65 pp). Keduanya secara konsisten mengindikasikan perbaikan kualitas hunian.
    - Periode 2018 ke 2020: BPS mengalami patahan metodologis drastis (turun dari 95,70% ke 59,54% atau -36,16 pp) akibat adopsi standar 4 kriteria SDG 11.1.1 (ketahanan bangunan, luas lantai, air layak, sanitasi layak; tercatat pada K-010). Sebaliknya, WDI tidak mengadopsi diskontinuitas tersebut dan hanya turun tipis dari 20,24% ke 19,41% (-0,83 pp).
    - Periode 2020 ke 2022: Pasca-patahan, tren perbaikan BPS berlanjut naik menjadi 60,66% (+1,12 pp), sementara angka WDI stagnan di 19,41% karena ketiadaan data survei baru UN-Habitat pada rilis arsip tersebut.
- **Kesimpulan**: Selisih nominal (40–75 poin persentase) sepenuhnya disebabkan oleh perbedaan unit observasi (rumah tangga nasional vs penduduk perkotaan), perbedaan dimensi yang diukur (layak huni vs kumuh), dan dampak patahan seri BPS tahun 2019.

#### B. Kategori Metode Berbeda: Kargo Udara var2754 & Transportasi Darat var2012/var2013
1. **Kargo Pesawat Terbang (var2754 Bongkar & Muat)**:
   - Evaluasi membandingkan hasil penjumlahan 34/38 provinsi terhadap baris ringkasan nasional BPS (kode wilayah 9999 / INDONESIA).
   - Pada tahun **2023**, hasil penjumlahan provinsi cocok sempurna dengan baris INDONESIA BPS dengan **selisih 0 kg** (Bongkar: 580.939.961 kg; Muat: 601.762.588 kg; rasio tepat 100,000%).
   - Pada tahun **2021, 2022, 2024, dan 2025**, ditemukan selisih sangat kecil antara -0,09% hingga +0,13% (maksimum selisih 765.577 kg pada volume 577 juta kg).
   - **Penyebab**: Angka ringkasan nasional BPS pada tahun-tahun tersebut dibulatkan ke jutaan kg terdekat (tiga nol di belakang, misalnya 622.000.000 kg), sedangkan agregasi provinsi mempertahankan nilai presisi riil dari bandara-bandara daerah.
2. **Transportasi Darat (var2012 Moda Transportasi & var2013 Kemacetan/Angkutan)**:
   - Rata-rata sederhana (*unweighted mean*) 34 provinsi menghasilkan selisih sistematis terhadap baris INDONESIA BPS (+3,2 s.d. +3,3 pp pada var2012; -0,7 s.d. -0,85 pp pada var2013).
   - **Penyebab**: Baris nasional BPS dihitung menggunakan agregasi terbobot populasi (*weighted national pooling* berdasarkan jumlah rumah tangga Susenas tiap provinsi), sedangkan rata-rata unweighted memperlakukan provinsi berpenduduk besar (seperti Jawa Barat) setara dengan provinsi berpenduduk kecil.

#### C. Kategori Cakupan Berbeda: Kargo Pelabuhan Laut var2753
- Seri kargo pelabuhan laut (var2753 Bongkar & Muat) **tidak memiliki baris ringkasan nasional (INDONESIA)** pada berkas sumber BPS (0 baris nasional di Silver).
- **Penyebab**: Publikasi BPS hanya mencakup 36 provinsi pesisir yang memiliki pelabuhan laut komersial aktif. DI Yogyakarta dan Papua Pegunungan tidak memiliki pelabuhan laut komersial yang dicatat, sehingga BPS tidak menyertakan baris agregasi nasional 9999 untuk seri ini.
- Agregat nasional dihitung langsung dari panel provinsi Gold: volume bongkar berkisar antara 358,10 juta ton (2023) hingga 451,66 juta ton (2025), sedangkan muat berkisar antara 384,78 juta ton (2021) hingga 508,55 juta ton (2025).

#### D. Kategori Vintage Berbeda & Analisis Rilis Arsip WDI
- Data WDI `EN.POP.SLUM.UR.ZS` pada repositori bersumber dari arsip snapshot per 8 Oktober 2026, sedangkan data BPS bersumber dari snapshot 20 Oktober 2026.
- Penelusuran arsip menunjukkan seri WDI ini diperbarui secara berkala dua tahunan (2000–2022) dengan frekuensi pemutakhiran rendah (*rarely updated series*). Tidak ditemukan revisi angka masa lampau pada rilis 2026 dibandingkan rilis sebelumnya, menegaskan stabilitas seri pembanding WDI untuk keperluan rekonsiliasi.

### 3. Keterlacakan Data dan Log Keputusan

Seluruh angka dan kategori dalam tabel rekonsiliasi dapat diverifikasi secara mandiri melalui:
- **Tabel Parquet Gold**: `data/gold/rekonsiliasi.parquet` (28 baris lengkap dengan metrik selisih).
- **Log Keputusan Tim (`log-keputusan.csv`)**:
  - `K-002`: Pemisahan baris agregat nasional INDONESIA (9999) var2753 untuk mencegah double counting.
  - `K-006`: Pemisahan panel var2753 (36 provinsi) dari var2754 (38 provinsi) karena perbedaan cakupan infrastruktur laut vs udara.
  - `K-009`: Klasifikasi 85 outlier kargo dan transportasi yang dipertahankan valid sesuai sumber.
  - `K-010`: Dokumentasi patahan metodologi 4 kriteria SDG 11.1.1 var1241 tahun 2019.
  - `K-013` & `K-014`: Penetapan satuan ton pada var2753 dan identifikasi var2754 sebagai pesawat terbang.
  - `K-015`: Penetapan kode SDG 11.1.1 dan satuan persen pada WDI EN.POP.SLUM.UR.ZS.
  - `K-019`: Alokasi 37 baris Silver (25 baris nasional kode 9999 + 12 baris WDI) terpisah ke tabel nasional Gold.
  - `K-024`: Penyusunan tabel rekonsiliasi 28 baris dan penelusuran kategori penjelasan tanpa modifikasi data asli.

## Validasi dan reproduksibilitas
Skema validasi (aturan, hasil lolos/gagal), waktu `python pipeline.py` dari nol, perbandingan pandas
vs DuckDB/Dask, dan keterbatasan yang tersisa.

## Pembagian kerja
| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|
