# Laporan Pembentukan Grid 38 Provinsi

## 1. Tujuan

Membentuk grid panel lengkap berdasarkan 38 provinsi Indonesia dan seluruh periode yang tersedia pada masing-masing seri data BPS. Pembentukan grid dilakukan untuk mengidentifikasi cakupan data dan sel kosong secara sistematis.

## 2. Metode

1. Menggunakan acuan standar 38 provinsi.
2. Membentuk kode provinsi dengan rumus `kode_prov = wilayah_id // 100`.
3. Membentuk kombinasi seluruh provinsi dan periode pada setiap seri.
4. Menggabungkan data observasi ke grid berdasarkan kode provinsi dan periode.
5. Mempertahankan sel tanpa observasi sebagai kosong (`NaN`), bukan mengubahnya menjadi nol.
6. Memisahkan baris agregasi nasional `INDONESIA` dengan kode wilayah `9999` dari panel provinsi. Data agregasi nasional tetap dipertahankan terpisah.
7. Memperlakukan kategori Bongkar dan Muat sebagai panel yang berbeda.

## 3.1 Kelengkapan Panel per Tahun

Persentase kelengkapan dihitung berdasarkan jumlah sel terisi dibandingkan dengan 38 provinsi pada setiap tahun.

| Seri | Periode | Sel Terisi per Tahun | Kelengkapan per Tahun |
|:---|:---|:---|:---|
| var1241 | 2015–2023 | 34/38 | 89,47% |
| var1241 | 2024–2025 | 38/38 | 100% |
| var2012 | 2017 dan 2020 | 34/38 | 89,47% |
| var2013 | 2017 dan 2020 | 34/38 | 89,47% |
| var2753 Bongkar | 2021–2025 | 36/38 | 94,74% |
| var2753 Muat | 2021–2025 | 36/38 | 94,74% |
| var2754 Bongkar | 2021–2025 | 38/38 | 100% |
| var2754 Muat | 2021–2025 | 38/38 | 100% |

Hasil tersebut menunjukkan bahwa sel kosong pada beberapa seri berkaitan dengan cakupan wilayah dan periode penerbitan data. Sel kosong tidak otomatis dianggap sebagai data hilang dari observasi yang seharusnya tersedia.

## 4. Interpretasi Sel Kosong

### var1241

Terdapat 36 sel kosong. Seluruhnya berasal dari provinsi dengan kode 92, 95, 96, dan 97 pada periode 2015–2023. Keempat provinsi tersebut belum tercakup dalam observasi seri pada periode tersebut.

### var2012

Terdapat 8 sel kosong, yaitu provinsi berkode 92, 95, 96, dan 97 pada tahun 2017 dan 2020.

### var2013

Terdapat 8 sel kosong, yaitu provinsi berkode 92, 95, 96, dan 97 pada tahun 2017 dan 2020.

### var2753

Kategori Bongkar memiliki 10 sel kosong dan kategori Muat memiliki 10 sel kosong. Keduanya tidak memiliki observasi untuk DI Yogyakarta (kode 34) dan Papua Pegunungan (kode 97) pada periode 2021–2025.

### var2754

Kategori Bongkar dan Muat masing-masing memiliki kelengkapan 100% untuk seluruh 38 provinsi pada periode 2021–2025.

## 5. Penanganan Sel Kosong

Sel kosong tidak otomatis dianggap sebagai nilai nol. Sel kosong pada grid menunjukkan bahwa tidak ditemukan observasi untuk kombinasi provinsi dan periode tersebut pada data sumber.

Tidak dilakukan imputasi atau pengisian nol karena tidak terdapat dasar untuk menyimpulkan bahwa nilai yang tidak tersedia sama dengan nol. Perbedaan cakupan antarseri juga harus diperhatikan dalam analisis lanjutan.

## 6. Catatan Perbedaan Cakupan

Seri var2753 dan var2754 memiliki cakupan wilayah yang berbeda. var2753 mencakup 36 provinsi, sedangkan var2754 mencakup 38 provinsi. Oleh karena itu, perbandingan Bongkar dan Muat antarseri harus mempertimbangkan perbedaan cakupan tersebut.

Kategori Bongkar dan Muat tetap disimpan sebagai panel terpisah agar perbedaan cakupan dan kelengkapan dapat diperiksa secara jelas.

## 7. Daftar File Grid

Seluruh file hasil pembentukan grid disimpan di folder `reports/`:

- `grid_var1241.csv`
- `grid_var2012.csv`
- `grid_var2013.csv`
- `grid_var2753_bongkar.csv`
- `grid_var2753_muat.csv`
- `grid_var2754_bongkar.csv`
- `grid_var2754_muat.csv`

## 8. Kesimpulan

Pembentukan grid 38 provinsi berhasil dilakukan untuk tujuh panel data dengan total 1.330 baris. Sebanyak 1.258 sel terisi dan 72 sel kosong, sehingga kelengkapan keseluruhan mencapai 94,59%.

Seluruh nama provinsi pada ketujuh grid telah terisi. Sel kosong dipertahankan sebagai nilai kosong dan dijelaskan berdasarkan cakupan seri dan periode. Data observasi yang tersedia juga telah diproses ke tahap Silver dalam file `data/silver/silver.parquet` dengan 1.283 baris dan 11 kolom, serta berhasil melewati validasi skema. Grid tetap disimpan terpisah sebagai dasar analisis kelengkapan panel oleh tim.
