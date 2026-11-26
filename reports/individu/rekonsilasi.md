# Rekonsiliasi nasional — persiapan Tahap 6

Tabel nasional lebar (periode x seri) tersedia di `table_nasional.csv`. Baris Indonesia seri BPS diambil dari hasil
ekstraksi (CSV snapshot 2026-10-20); WDI dari Silver. Skrip pembangkit khusus belum di-commit, dan versi panjang
(`nasional_long.csv` dengan `_berkas_raw`/`_sha256_raw`) belum dibuat; keduanya dikerjakan pada Sprint 2.
Satuan var2753 ton dan var2754 kilogram (K-013, K-014): nilai kedua seri tidak sebanding langsung.

## Daftar pasangan

5 pasangan direkonsiliasi (P1–P5); 3 seri persentase tidak berlaku (T).

| id | seri_a | seri_b | kategori | periode_beririsan | metode |
|---|---|---|---|---|---|
| P1 | var1241 (Indonesia) | EN.POP.SLUM.UR.ZS | definisi berbeda | 4 | arah perubahan antar-periode beririsan; tanpa selisih nilai |
| P2 | var2753 Bongkar (jumlah 36 provinsi) | var2753 Bongkar (Indonesia) | rekonsiliasi internal | 5 | jumlah provinsi vs baris Indonesia; selisih dan persen |
| P3 | var2753 Muat (jumlah 36 provinsi) | var2753 Muat (Indonesia) | rekonsiliasi internal | 5 | jumlah provinsi vs baris Indonesia; selisih dan persen |
| P4 | var2754 Bongkar (jumlah 38 provinsi) | var2754 Bongkar (Indonesia) | rekonsiliasi internal | 5 | jumlah provinsi vs baris Indonesia; selisih dan persen |
| P5 | var2754 Muat (jumlah 38 provinsi) | var2754 Muat (Indonesia) | rekonsiliasi internal | 5 | jumlah provinsi vs baris Indonesia; selisih dan persen |
| T1241 | var1241 (provinsi) | var1241 (Indonesia) | tidak berlaku | 0 | tidak direkonsiliasi |
| T2012 | var2012 (provinsi) | var2012 (Indonesia) | tidak berlaku | 0 | tidak direkonsiliasi |
| T2013 | var2013 (provinsi) | var2013 (Indonesia) | tidak berlaku | 0 | tidak direkonsiliasi |

## P1 — var1241 Indonesia vs WDI `EN.POP.SLUM.UR.ZS`: definisi berbeda

Periode beririsan: 2016, 2018, 2020, 2022 (4 periode; WDI hanya tahun genap 2000–2022).
Dilaporkan arah perubahan, bukan selisih nilai.

| dari | ke | var1241_awal | var1241_akhir | var1241_arah | wdi_awal | wdi_akhir | wdi_arah | simpulan |
|---|---|---|---|---|---|---|---|---|
| 2016 | 2018 | 94,00 | 95,70 | naik | 21,89 | 20,24 | turun | searah membaik (hunian layak naik, penduduk kumuh turun) |
| 2018 | 2020 | 95,70 | 59,54 | turun | 20,24 | 19,41 | turun | tidak dapat dinilai: interval melintasi patahan metodologi var1241 2019 |
| 2020 | 2022 | 59,54 | 60,66 | naik | 19,41 | 19,41 | tetap | WDI tetap; tidak ada arah pembanding |

- Interval 2018 ke 2020 tidak dapat dinilai: var1241 turun dari 95,70 ke 59,54 karena perubahan metodologi 2019 (K-010),
  bukan perubahan kondisi hunian.
- WDI bergerak turun dengan selisih antar-periode konstan (1,6542 per dua tahun hingga 2018), lalu separuhnya, lalu nol
  (2020 = 2022 = 19,41083). Pola ini tampak interpolasi atau model; sebab pastinya belum diverifikasi ke WDI.
- Kedua seri tidak boleh dikurangkan: konsep berlawanan arah dan populasi berbeda.

## P2–P5 — rekonsiliasi internal bongkar muat (jumlah provinsi vs Indonesia)

20 pasangan nilai (2 seri x Bongkar/Muat x 5 tahun). Selisih terbesar
0,227%.
6 pasangan melebihi galat pembulatan ke jutaan (0,5 juta); selisihnya tetap di bawah 0,23% dan
penyebabnya belum diketahui (tidak ada bukti galat ekstraksi). var2753 hanya mencakup 36 provinsi (K-006). Pada 2023
angka nasional var2754 sama persis dengan jumlah provinsi (tidak dibulatkan).

| seri_kode | rincian | periode | jumlah_provinsi | nasional | selisih_persen | dalam_pembulatan |
|---|---|---|---|---|---|---|
| var2753 | Bongkar | 2021 | 399.325.458 | 399.000.000 | 0,082 | True |
| var2753 | Bongkar | 2022 | 392.927.647 | 393.000.000 | -0,018 | True |
| var2753 | Bongkar | 2023 | 358.100.371 | 358.000.000 | 0,028 | True |
| var2753 | Bongkar | 2024 | 396.389.965 | 396.000.000 | 0,098 | True |
| var2753 | Bongkar | 2025 | 451.664.125 | 452.000.000 | -0,074 | True |
| var2753 | Muat | 2021 | 384.784.258 | 384.000.000 | 0,204 | False |
| var2753 | Muat | 2022 | 398.095.203 | 399.000.000 | -0,227 | False |
| var2753 | Muat | 2023 | 385.612.407 | 386.000.000 | -0,100 | True |
| var2753 | Muat | 2024 | 433.733.968 | 434.000.000 | -0,061 | True |
| var2753 | Muat | 2025 | 508.550.340 | 508.000.000 | 0,108 | False |
| var2754 | Bongkar | 2021 | 622.546.815 | 622.000.000 | 0,088 | False |
| var2754 | Bongkar | 2022 | 577.765.577 | 577.000.000 | 0,133 | False |
| var2754 | Bongkar | 2023 | 580.939.961 | 580.939.961 | 0,000 | True |
| var2754 | Bongkar | 2024 | 689.283.176 | 689.000.000 | 0,041 | True |
| var2754 | Bongkar | 2025 | 674.547.332 | 675.000.000 | -0,067 | True |
| var2754 | Muat | 2021 | 602.068.213 | 602.000.000 | 0,011 | True |
| var2754 | Muat | 2022 | 642.439.246 | 643.000.000 | -0,087 | False |
| var2754 | Muat | 2023 | 601.762.588 | 601.762.588 | 0,000 | True |
| var2754 | Muat | 2024 | 674.735.003 | 675.000.000 | -0,039 | True |
| var2754 | Muat | 2025 | 670.710.328 | 671.000.000 | -0,043 | True |

## Tidak berlaku

var1241, var2012, var2013 adalah persentase: jumlah atau rata-rata provinsi tidak sama dengan angka Indonesia tanpa
bobot rumah tangga atau penduduk, yang tidak ada di paket. Seri bongkar muat dan transportasi tidak punya pembanding
eksternal di paket.
