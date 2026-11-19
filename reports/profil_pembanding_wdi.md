# Profil Seri Pembanding WDI: EN.POP.SLUM.UR.ZS

## 1. Tujuan Analisis

Analisis ini dilakukan untuk memeriksa ketersediaan seri pembanding World Development Indicators (WDI) dengan kode `EN.POP.SLUM.UR.ZS`.

Pemeriksaan mencakup periode data, rincian wilayah, satuan, jumlah observasi yang tersedia, serta tahun yang beririsan dengan seri utama BPS. Hasilnya digunakan untuk menentukan rincian yang berpotensi dibandingkan pada tahap 6.

## 2. Sumber Data

Data diperiksa dari arsip berikut:

- Data WDI: `data/raw/wdi/2026-10-20/data/kelompok-01-hal-01.json`
- Metadata WDI: `data/raw/wdi/2026-10-20/metadata/sumber2_indikator.json`
- Metadata SDG: `data/raw/wdi/2026-10-20/metadata/sumber46_indikator.json`

Tanggal pembaruan data yang tercantum dalam arsip WDI adalah 8 Oktober 2026.

## 3. Identitas Seri Pembanding

| Atribut | Keterangan |
|---|---|
| Kode indikator | EN.POP.SLUM.UR.ZS |
| Nama indikator | Population living in slums (% of urban population) |
| Sumber | World Development Indicators |
| Organisasi sumber | UN-Habitat |
| Topik | Poverty, Urban Development, Environment |
| Satuan | Persentase (%) berdasarkan definisi indikator |
| Cakupan wilayah yang ditemukan | Indonesia |
| Dimensi data | Wilayah negara dan tahun |

Catatan: Kolom `unit` pada metadata dan data mentah tidak terisi. Namun, nama indikator secara eksplisit menyatakan bahwa pengukurannya berupa persentase dari populasi perkotaan.

## 4. Ketersediaan Periode dan Rincian Data

Hasil pemeriksaan arsip menunjukkan bahwa terdapat 66 baris data untuk indikator ini, dengan rentang tahun 1960–2025. Akan tetapi, tidak semua baris memiliki nilai.

| Seri | Periode baris tersedia | Tahun dengan nilai | Rincian wilayah | Satuan |
|---|---|---|---|---|
| WDI EN.POP.SLUM.UR.ZS | 1960–2025 | 2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022 | Indonesia | Persentase (%) dari populasi perkotaan |
| BPS var1241 (SDG 11.1.1) | 2015–2025 | Periode seri utama | Indonesia dan 37 provinsi | Persentase (%) |

Pada seri WDI terdapat 12 observasi yang memiliki nilai, sedangkan baris tahun lainnya tidak memiliki nilai. Observasi yang tersedia muncul setiap dua tahun, yaitu dari 2000 sampai 2022.

Berdasarkan data yang diperiksa, rincian WDI hanya tersedia pada tingkat negara. Tidak ditemukan pemisahan berdasarkan jenis kelamin, kelompok umur, atau provinsi.

## 5. Tahun yang Beririsan dengan Seri Utama

Seri utama BPS var1241 memiliki periode 2015–2025. Sementara itu, nilai WDI yang tersedia pada rentang tersebut adalah:

- 2016
- 2018
- 2020
- 2022

Dengan demikian, terdapat empat tahun yang menjadi kandidat irisan antara seri WDI dan seri utama BPS var1241.

Tahun-tahun tersebut dapat digunakan sebagai titik awal pemeriksaan perbandingan pada tahap 6. Perlu dipastikan kembali bahwa nilai seri BPS pada tingkat Indonesia tersedia pada masing-masing tahun tersebut sebelum perbandingan dilakukan.

## 6. Kandidat Rincian yang Sebanding

| Rincian | Status | Alasan |
|---|---|---|
| Indonesia (WDI) dengan Indonesia (BPS var1241) | Kandidat sebanding secara wilayah | Kedua seri memiliki cakupan wilayah nasional Indonesia. |
| Tahun 2016, 2018, 2020, dan 2022 | Kandidat tahun perbandingan | Tahun tersebut memiliki nilai pada seri WDI dan berada dalam periode seri utama BPS. |
| Data WDI dengan rincian provinsi BPS | Tidak sebanding secara langsung | Arsip WDI yang diperiksa hanya menyediakan data Indonesia, bukan data per provinsi. |
| Rincian jenis kelamin dan kelompok umur | Tidak tersedia untuk dicocokkan | Tidak ditemukan pemisahan berdasarkan jenis kelamin maupun kelompok umur pada data WDI. |

### Alasan dan Batasan Perbandingan

Walaupun kedua indikator sama-sama berkaitan dengan kondisi hunian, keduanya tidak mengukur hal yang persis sama.

- WDI mengukur proporsi penduduk perkotaan yang tinggal di rumah tangga kumuh (*slum households*).
- BPS var1241 mengukur indikator SDG 11.1.1 yang berkaitan dengan akses rumah tangga terhadap hunian layak.
- Penyebut kedua indikator berbeda. WDI menggunakan populasi perkotaan, sedangkan seri BPS menggunakan rumah tangga.
- Arah interpretasinya juga berbeda. Nilai WDI yang lebih tinggi menunjukkan proporsi penduduk perkotaan yang tinggal di kawasan kumuh lebih besar. Sebaliknya, nilai BPS yang lebih tinggi menunjukkan proporsi rumah tangga yang memiliki akses terhadap hunian layak lebih besar.

Oleh karena itu, kedua seri dapat digunakan sebagai pembanding konseptual untuk melihat arah perubahan kondisi hunian, tetapi tidak dapat dianggap sebagai ukuran yang identik. Perbedaan nilai keduanya tidak boleh langsung ditafsirkan sebagai selisih dari dua pengukuran yang setara.

## 7. Kesimpulan

Seri WDI `EN.POP.SLUM.UR.ZS` memiliki 66 baris dalam arsip dengan rentang tahun 1960–2025. Namun, hanya terdapat 12 observasi bernilai, yaitu pada tahun 2000 hingga 2022 dengan interval dua tahun.

Rincian wilayah yang ditemukan hanya mencakup Indonesia. Tidak ditemukan rincian berdasarkan provinsi, jenis kelamin, maupun kelompok umur. Satuan pada kolom metadata tidak terisi, tetapi nama indikator menunjukkan pengukuran dalam persentase populasi perkotaan.

Terdapat empat tahun kandidat irisan dengan periode seri utama BPS var1241, yaitu 2016, 2018, 2020, dan 2022.

Rincian Indonesia pada kedua seri menjadi kandidat perbandingan untuk tahap 6. Namun, perbandingan perlu dilakukan secara hati-hati karena definisi indikator, penyebut, dan arah interpretasinya berbeda. Oleh sebab itu, perbandingan lebih tepat difokuskan pada arah perubahan dan pola tren, bukan kesetaraan nilai secara langsung.