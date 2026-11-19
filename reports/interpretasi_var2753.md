# Interpretasi Analisis Variabel 2753

## 1. Interpretasi Statistik Deskriptif Keseluruhan

Berdasarkan hasil statistik deskriptif, data variabel 2753 terdiri dari dua kategori, yaitu Bongkar dan Muat. Masing-masing kategori memiliki 185 data dengan satuan kilogram (KG).

Pada kategori Bongkar, diperoleh nilai rata-rata sebesar 21.602.200 KG, median sebesar 5.315.871 KG, nilai minimum sebesar 173.347 KG, dan nilai maksimum sebesar 452.000.000 KG. Standar deviasi sebesar 65.016.650 KG menunjukkan adanya variasi nilai yang cukup tinggi.

Sementara itu, kategori Muat memiliki rata-rata sebesar 22.820.410 KG, median sebesar 3.662.034 KG, nilai minimum sebesar 208.332 KG, dan nilai maksimum sebesar 508.000.000 KG. Standar deviasi sebesar 70.609.140 KG menunjukkan bahwa variasi nilai pada kategori Muat juga cukup tinggi.

Secara umum, kategori Muat memiliki rata-rata dan nilai maksimum lebih tinggi dibandingkan kategori Bongkar. Pada kedua kategori, nilai rata-rata jauh lebih besar dibandingkan median. Hal ini mengindikasikan distribusi data yang cenderung menceng ke kanan (*right-skewed*), yaitu terdapat beberapa wilayah dengan nilai aktivitas bongkar dan muat yang jauh lebih tinggi dibandingkan sebagian besar wilayah lainnya.


## 2. Interpretasi Profil Per Provinsi

Berdasarkan hasil perhitungan profil per provinsi, terdapat perbedaan rata-rata nilai yang cukup besar antara wilayah pada kategori Bongkar maupun Muat.

Pada kategori Bongkar, wilayah dengan rata-rata tertinggi adalah Banten sebesar 64.641.018,4 KG, diikuti Jawa Timur sebesar 37.854.033,6 KG dan Kalimantan Selatan sebesar 33.531.441,6 KG. Sementara itu, wilayah dengan rata-rata terendah adalah Bengkulu sebesar 461.803,2 KG, diikuti Sulawesi Barat sebesar 815.797,8 KG dan Papua Barat Daya sebesar 765.295,8 KG.

Pada kategori Muat, wilayah dengan rata-rata tertinggi adalah Kalimantan Selatan sebesar 104.014.442 KG, diikuti Kalimantan Timur sebesar 84.730.403,8 KG dan Jawa Timur sebesar 30.572.570,6 KG. Sementara itu, wilayah dengan rata-rata terendah adalah Papua Barat Daya sebesar 477.558,4 KG, diikuti Bali sebesar 607.231,8 KG dan Papua Selatan sebesar 777.218 KG.

Secara umum, hasil tersebut menunjukkan bahwa aktivitas bongkar dan muat memiliki perbedaan nilai yang cukup besar antarwilayah. Banten memiliki rata-rata aktivitas bongkar tertinggi, sedangkan Kalimantan Selatan memiliki rata-rata aktivitas muat tertinggi. Perbedaan ini dapat menjadi perhatian dalam pemeriksaan lebih lanjut terhadap pola distribusi aktivitas bongkar dan muat antarwilayah.

## 3. Interpretasi Boxplot

Boxplot dibuat secara terpisah untuk kategori Bongkar dan Muat berdasarkan tahun 2021–2025. Pemisahan ini dilakukan agar distribusi nilai kedua kategori dapat dibandingkan tanpa mencampurkan karakteristik masing-masing aktivitas.

Boxplot digunakan untuk melihat persebaran nilai, median, rentang antarkuartil, serta kemungkinan nilai ekstrem pada setiap tahun.

Perbedaan panjang kotak dan whisker menunjukkan adanya variasi nilai antarwilayah. Apabila terdapat titik yang berada di luar whisker, titik tersebut menunjukkan pengamatan yang berpotensi menjadi nilai ekstrem.

Hasil boxplot perlu diperhatikan bersama hasil deteksi IQR karena nilai ekstrem secara statistik belum tentu menunjukkan kesalahan data.

## 4. Interpretasi Grafik Deret Waktu

Grafik deret waktu dibuat secara terpisah untuk kategori Bongkar dan Muat dengan menampilkan perubahan nilai setiap wilayah selama periode 2021–2025.

Grafik ini digunakan untuk mengamati perubahan aktivitas bongkar dan muat dari tahun ke tahun serta melihat perbedaan pola antarwilayah.

Wilayah dengan garis yang memiliki nilai relatif tinggi menunjukkan aktivitas bongkar atau muat yang lebih besar dibandingkan wilayah lainnya. Sementara itu, perubahan garis dari satu tahun ke tahun berikutnya dapat menunjukkan peningkatan maupun penurunan aktivitas.

Grafik deret waktu membantu mengidentifikasi perubahan nilai yang cukup mencolok dan wilayah yang memiliki pola berbeda dibandingkan wilayah lainnya. Perubahan tersebut perlu diperiksa lebih lanjut sebelum disimpulkan sebagai anomali.

## 5. Interpretasi Deteksi Calon Anomali

Berdasarkan metode Interquartile Range (IQR), ditemukan 33 calon anomali yang terdiri dari 18 data kategori Bongkar dan 15 data kategori Muat. Seluruh calon anomali memiliki nilai di atas batas atas IQR.

Pada kategori Bongkar, beberapa wilayah yang berulang kali terdeteksi antara lain Jawa Timur dan Banten. Sementara itu, pada kategori Muat, wilayah Kalimantan Selatan dan Kalimantan Timur berulang kali terdeteksi memiliki nilai relatif tinggi dibandingkan wilayah lainnya.

Temuan ini menunjukkan adanya perbedaan nilai aktivitas bongkar dan muat yang cukup besar antarwilayah. Data tersebut perlu diperiksa lebih lanjut menggunakan sumber data atau informasi pendukung sebelum dinyatakan sebagai anomali yang sebenarnya.