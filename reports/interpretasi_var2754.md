# Interpretasi Analisis Var2754

## 1. Interpretasi Statistik Deskriptif

Dataset var2754 terdiri dari 390 data dengan periode tahun 2021–2025. Data terbagi menjadi dua kategori, yaitu Bongkar dan Muat, dengan masing-masing 195 data. Seluruh data menggunakan satuan kilogram (KG) dan tidak ditemukan nilai kosong.

Rata-rata nilai Muat sedikit lebih tinggi dibandingkan Bongkar. Standar deviasi yang besar pada kedua kategori menunjukkan adanya variasi nilai yang cukup tinggi antarwilayah.

Nilai rata-rata yang jauh lebih tinggi dibandingkan median menunjukkan distribusi data cenderung menceng ke kanan (*right-skewed*).

## 2. Interpretasi Profil Per Wilayah

Pada kategori Bongkar, Banten memiliki rata-rata tertinggi sebesar 112.839.908,2 KG, diikuti Papua Pegunungan sebesar 110.025.444,4 KG.

Pada kategori Muat, Banten memiliki rata-rata tertinggi sebesar 222.587.222,2 KG, diikuti Papua sebesar 110.884.728,4 KG.

Sementara itu, Sulawesi Barat memiliki rata-rata terendah pada kedua kategori, yaitu 61.533,6 KG untuk Bongkar dan 40.575,8 KG untuk Muat.

## 3. Interpretasi Grafik Deret Waktu

Pada kategori Bongkar, rata-rata nilai mengalami penurunan pada 2022, sedikit meningkat pada 2023, meningkat cukup besar pada 2024, kemudian sedikit menurun pada 2025.

Pada kategori Muat, rata-rata meningkat pada 2022, menurun pada 2023, meningkat kembali pada 2024, dan sedikit menurun pada 2025.

Banten dan Papua Pegunungan menjadi wilayah dengan nilai Bongkar tertinggi pada beberapa tahun pengamatan. Pada kategori Muat, Banten selalu menjadi wilayah dengan nilai tertinggi. Sulawesi Barat selalu menjadi wilayah dengan nilai terendah pada kedua kategori.

## 4. Interpretasi Deteksi Calon Anomali

Deteksi calon anomali dilakukan menggunakan metode Interquartile Range (IQR) dengan batas bawah Q1 - 1,5 × IQR dan batas atas Q3 + 1,5 × IQR. Perhitungan dilakukan secara terpisah berdasarkan kategori dan tahun.

Hasil deteksi menemukan 48 calon anomali, terdiri dari 25 data pada kategori Bongkar dan 23 data pada kategori Muat.

Pada kategori Bongkar, ditemukan 5 calon anomali pada setiap tahun 2021–2025. Wilayah yang berulang kali teridentifikasi adalah Sumatera Utara, Banten, Kalimantan Timur, Sulawesi Selatan, dan Papua Pegunungan.

Pada kategori Muat, ditemukan 4–5 calon anomali setiap tahun. Wilayah yang sering teridentifikasi adalah DKI Jakarta, Jawa Timur, Banten, Sulawesi Selatan, dan Papua.

Calon anomali tersebut menunjukkan nilai yang relatif jauh dari distribusi mayoritas data. Namun, hasil deteksi ini belum membuktikan adanya kesalahan data. Diperlukan pemeriksaan lebih lanjut terhadap sumber data dan kondisi masing-masing wilayah.

## 5. Kesimpulan

Secara umum, dataset var2754 memiliki variasi nilai yang cukup tinggi antarwilayah. Pola nilai Bongkar dan Muat mengalami perubahan selama periode 2021–2025. Metode IQR berhasil mengidentifikasi 48 calon anomali yang perlu diperiksa lebih lanjut sebelum dapat dinyatakan sebagai kesalahan data.