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
| Outlier atau calon anomali | 85 calon anomali | Mempertahankan nilai ekstrem karena tidak ditemukan bukti kesalahan input; seluruh 85 calon anomali diklasifikasikan sebagai outlier asli dalam hasil klasifikasi | Mengoreksi nilai ekstrem tanpa bukti kesalahan sumber | K-009 |
| Patahan seri indikator hunian layak (var1241) | 34 provinsi terdampak | Mengategorikan penurunan serentak dari 2018 ke 2019 sebagai patahan seri. Rata-rata sederhana antarprovinsi turun dari 93,90% menjadi 54,14%, atau sebesar 39,77 poin persentase. Metadata BPS menyatakan bahwa sejak 2019 pengukuran menggunakan empat kriteria hunian layak. Nilai asli tetap dipertahankan tanpa koreksi | Menganggap penurunan serentak sebagai galat input dan mengubah nilai | K-010 |
| Kesamaan snapshot atau potensi duplikasi | 3 seri identik pada snapshot 17 dan 20 Oktober 2026 | Mempertahankan kedua snapshot karena kesamaan isi tidak otomatis menunjukkan duplikasi yang salah. var2012 dan var2013 tidak tersedia pada snapshot 17 Oktober | Menghapus salah satu snapshot hanya karena isi datanya sama | K-008 |
| Format dan tipe data nilai | 10 baris pada var2753 | Mengonversi kolom `nilai` menjadi tipe numerik integer agar dapat diolah secara konsisten | Membiarkan kolom `nilai` bertipe teks atau object | K-003 |
| Penetapan satuan var2012 dan var2013 | 140 baris | Menetapkan satuan `persen` berdasarkan judul indikator dan pemeriksaan sumber; keputusan ini memperbarui placeholder pada keputusan awal | Membiarkan placeholder atau menebak satuan tanpa pemeriksaan sumber | K-007, K-011, K-012 |
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
Seri utama vs pembanding nasional: selisih, penjelasannya (definisi, metode, vintage, granularitas),
dan hasil analisis revisi dari arsip WDI.

## Validasi dan reproduksibilitas
Skema validasi (aturan, hasil lolos/gagal), waktu `python pipeline.py` dari nol, perbandingan pandas
vs DuckDB/Dask, dan keterbatasan yang tersisa.

## Pembagian kerja
| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|
