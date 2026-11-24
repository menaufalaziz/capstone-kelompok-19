# Laporan validasi

Dihasilkan otomatis oleh `python pipeline.py` (tahap 8).

## Ringkasan

- Baris Silver: 1,295
- Seri Silver: 6
- Wilayah Silver: 39
- Berkas sumber Silver: 6
- Baris Panel Gold: 1,330 (7 indikator, 38 provinsi)
- Hasil: LOLOS

## Pemeriksaan

| Pemeriksaan | Hasil |
|---|---|
| Skema minimal dan lineage MANIFEST | lolos |
| Kunci unik Silver sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw | lolos |
| Rentang persen 0–100 dan berat tidak negatif | lolos |
| Integritas Panel Gold (kunci unik, status sel, satuan seragam) | lolos |
