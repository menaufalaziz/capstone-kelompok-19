# AI_LOG — <Nama tim>

Satu baris per pemakaian AI yang bermakna (ChatGPT, Claude, Copilot, Bravais, dan sejenisnya).
Ringkas dan jujur; transkrip penuh tidak diminta. Yang dinilai bukan "pakai AI atau tidak",
melainkan "mengerti atau tidak" — isi kolom terakhir dengan apa yang Anda ubah dari keluarannya.

| Tanggal | Siapa (NIM) | Alat | Untuk apa | Apa yang diubah dari keluarannya |
|---|---|---|---|---|
| 2026-11-03 | 12345678 | Copilot | kerangka DataLoader | ganti normalisasi, tambah seed worker |
| 2026-11-18 | 124450047 | Claude Code | audit satuan dan kode SDG enam seri Kasus 19 | menambahkan bukti silang publikasi BPS/Kemenhub, mengoreksi var2753 ke ton dan nama var2754, lalu mencatat semuanya di log-keputusan.csv |
| 2026-11-19 | 124450047 | Claude Code | menyusun Silver dari ekstraksi CSV BPS dan JSON WDI serta menyambungkannya ke pipeline | memilih CSV snapshot 2026-10-20, menambahkan 12 observasi WDI, mempertahankan rincian Bongkar/Muat sebagai baris, dan menambah validasi dasar |
| 2026-11-21 | 124450047 | Claude Code | review dan merge PR #13 (tabel nasional) dan PR #14 (validasi lanjutan), lalu menjalankan pipeline di main | menghapus berkas `.save`, menyelaraskan provenance laporan rekonsiliasi, mencatat kolom `penanda_patahan` di kamus data, dan memverifikasi pipeline lolos dari data mentah sampai Silver |
| 2026-11-24 | 124450047 | Claude Code | membentuk panel Gold provinsi × periode × indikator dari Silver, menyeragamkan satuan bongkar muat, dan menambahkan lineage per sel | memisahkan kolom nilai menurut satuan, mengonversi var2754 kg ke ton sambil menyimpan nilai asli, menambahkan log10 ton, memperluas validasi Gold, serta mencatat K-025 s.d. K-027 |
| 2026-11-24 | 124450022 | Antigravity | persiapan panel Gold provinsi x periode x indikator dan pemilihan snapshot | menambahkan penanganan sel kosong struktural 38 provinsi, kalkulasi log1p kargo, dan validasi 10 unit test otomatis |
| 2026-11-24 | 124450022 | Antigravity | draf integrasi dan tabel rekonsiliasi seri utama vs pembanding WDI serta agregat provinsi | menambahkan formulasi tabel rekonsiliasi 28 baris, klasifikasi 4 kategori penjelasan (definisi, metode, cakupan, vintage), dan modul python src/gold/rekonsiliasi.py |
