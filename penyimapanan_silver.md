# Penyimpanan Silver (Tahap 5) — draf untuk laporan tim

DDL: `sql/silver_sqlite.sql`. Pemuat dan pengujian: `python -m src.gold.simpan_sql` (menghasilkan
`data/silver/silver.sqlite`, tidak di-commit). Diuji pada SQLite 3.53.1 (Linux); belum diuji di Windows.
Tabel STRICT butuh SQLite 3.37 ke atas; pemuat memberi pesan jelas bila versinya lebih lama.

## Skema

| Tabel | Isi | Kunci primer |
|---|---|---|
| `silver` | 1.295 baris, 11 kolom sesuai skema minimal tim | `(seri_kode, wilayah_kode, periode, rincian, _berkas_raw, sumber)` |
| `seri` | 6 seri: nama, kode SDG, satuan (dari `src/silver/katalog.py`) | `seri_kode` |
| `wilayah` | 39 wilayah: 38 provinsi dan Indonesia (9999), dengan kolom `tingkat` | `wilayah_kode` |
| `berkas_raw` | 22 berkas di `MANIFEST.csv` dengan sha256 | `berkas` |

Kunci primer `silver` sama dengan `KUNCI` di `src/common/skema.py`; `sumber` diletakkan di akhir karena `seri_kode`
sudah menentukannya. Dengan urutan awal (`sumber` di depan), pencarian per seri memindai seluruh tabel; setelah diubah,
rencana kueri memakai kunci primer (`SEARCH ... USING PRIMARY KEY`).

Tipe: `wilayah_kode` INTEGER, `nilai` REAL (bolak-balik terhadap parquet identik persis), sisanya TEXT. `periode`
tetap TEXT karena Silver mengizinkan `2020-S1`, `2020-Q1`, dan `2020-03`.

Kunci asing gabungan membuat basis data sendiri menolak data yang tidak konsisten:
- `(seri_kode, sumber, satuan)` ke `seri`: satuan harus sesuai seri.
- `(wilayah_kode, nama_wilayah)` ke `wilayah`: nama harus sesuai kode.
- `(_berkas_raw, _sha256_raw)` ke `berkas_raw`: sha256 harus sesuai berkasnya di MANIFEST (lineage tidak bisa diisi sembarang).

Batasan nilai: persen harus 0–100, satuan lain tidak negatif, format `periode` harus cocok `jenis_periode`.
Baris Indonesia dipisah lewat `v_nasional` (37 baris) dan `v_provinsi` (1.258 baris), tanpa menyalin data.

## Bukti

- 1.295 baris termuat; `integrity_check` dan `foreign_key_check` bersih; hasil baca-balik sama persis dengan `silver.parquet`.
- 12 dari 12 pelanggaran ditolak (kunci ganda, NULL, persen 100,5, persen negatif, format periode salah, jenis periode
  tak dikenal, seri/wilayah tak terdaftar, satuan atau nama tak cocok, sha256 tak cocok, berkas di luar MANIFEST).
- Kunci asing tidak aktif secara bawaan di SQLite; `sambung()` menjalankan `PRAGMA foreign_keys = ON` di tiap koneksi.
  Koneksi lain (DBeaver, skrip lain) harus melakukannya sendiri.

## Alasan memilih SQLite

| | SQLite | DuckDB | PostgreSQL |
|---|---|---|---|
| Pemasangan | sudah ada di Python | `pip install duckdb` (sudah di requirements) | server, akun, port |
| Bentuk | satu berkas | satu berkas | layanan terpisah |
| Batasan (PK, FK, CHECK) | ada; tabel STRICT | ada | ada, paling lengkap |
| Kecocokan beban | transaksional, data kecil | analitik kolom, data besar | banyak pengguna, data besar |

1. Silver hanya 1.295 baris dan sekitar 0,4 MB; tidak ada kebutuhan server, banyak pengguna, atau skala yang membenarkan PostgreSQL.
2. Lima anggota memakai komputer berbeda (kebanyakan Windows). SQLite ikut Python sehingga `python -m src.gold.simpan_sql`
   berjalan tanpa pemasangan atau konfigurasi, dan berkas basis datanya bisa dibangkitkan ulang.
3. Pemeriksaan integritas (kunci asing gabungan, CHECK) ditegakkan basis data sendiri, bukan hanya skrip.
4. DuckDB tetap dipakai di Tahap 7 (membandingkan pandas vs DuckDB pada arsip WDI 142 rilis), tempat keunggulan
   analitiknya relevan. Memilihnya untuk Silver tidak memberi keuntungan pada ukuran data sekecil ini.

Keterbatasan SQLite yang perlu dicatat: tidak ada tipe DECIMAL (REAL berpresisi ganda; uji bolak-balik tidak menemukan
selisih), kunci asing harus diaktifkan per koneksi, dan satu penulis pada satu waktu.

## Dibandingkan dengan menyimpan JSON mentah sebagai dokumen

Percobaan: seluruh 14 berkas JSON mentah dimuat apa adanya sebagai satu dokumen per berkas (tabel `dokumen_raw`,
sha256 diperiksa dulu), lalu kueri yang sama dijalankan di kedua bentuk: nilai Indonesia var1241 tahun 2022.
Keduanya mengembalikan 60,66.

| | Relasional (`silver`) | Dokumen JSON mentah |
|---|---|---|
| Kueri | 137 karakter: `SELECT nilai FROM v_nasional WHERE seri_kode='var1241' AND periode='2022' AND ...` | 319 karakter: harus memecah halaman, mencari kode tahun, lalu merangkai kunci `9999`+`1241`+`0`+kode tahun+`0` |
| Median waktu kueri (1.000 ulangan) | 0,021 ms | 0,098 ms |
| Ukuran | 364.544 bait setelah VACUUM (1.295 baris, 4 tabel) | seri BPS saja 134.980 bait mentah; seluruh 14 berkas 3.051.158 bait (sebagian besar metadata WDI) |
| Batasan | PK, FK, CHECK ditegakkan | hanya `json_valid` |
| Tipe nilai | REAL | angka di dalam JSON; tiap kueri harus mengurainya |
| Kesetiaan pada sumber | hanya 11 kolom Silver | seluruh metadata terjaga (`last_update`, judul, unit, halaman) |
| Tahun terbit sebagian | satu baris per observasi | var1241 terpecah 4 halaman (tiga tahun per halaman) |

Catatan pembacaan: selisih waktu sub-milidetik pada 1.295 baris bukan bukti performa yang berarti. Ukuran kedua bentuk
tidak sebanding langsung karena yang relasional hanya memuat observasi, sedangkan dokumen memuat seluruh respons dan
dua snapshot yang isinya identik.

Kesimpulan: untuk analisis, Silver dan Gold disimpan relasional karena batasan dan kuerinya lebih sederhana. Respons mentah
tetap dipertahankan sebagai berkas di `data/raw/` (tidak diubah, sha256 di MANIFEST) sebagai sumber kebenaran dan untuk
metadata yang tidak masuk Silver. Tabel `dokumen_raw` hanya dibuat dalam percobaan perbandingan dan tidak ada di `silver.sqlite`.
