-- Tahap 5: skema Silver Kasus 19 untuk SQLite (>= 3.37, tabel STRICT).
--
-- Satu baris `silver` = satu seri x wilayah x periode x rincian x berkas sumber,
-- sama dengan KUNCI di src/common/skema.py. Kolom `silver` mengikuti skema minimal tim (11 kolom).
-- Tabel dimensi (seri, wilayah, berkas_raw) menjaga konsistensi lewat kunci asing gabungan:
-- satuan harus sesuai seri, nama harus sesuai kode wilayah, dan sha256 harus sesuai berkasnya.
--
-- PENTING: SQLite tidak menegakkan kunci asing kecuali tiap koneksi menjalankan
--   PRAGMA foreign_keys = ON;
-- (src/gold/simpan_sql.py melakukannya).
CREATE TABLE berkas_raw (
  berkas TEXT NOT NULL PRIMARY KEY, -- relatif terhadap data/raw/
  bait INTEGER NOT NULL CHECK (bait > 0),
  sha256 TEXT NOT NULL CHECK (
    length (sha256) = 64
    AND sha256 NOT GLOB '*[^0-9a-f]*'
  ),
  UNIQUE (berkas, sha256)
) STRICT;

CREATE TABLE seri (
  seri_kode TEXT NOT NULL PRIMARY KEY, -- var_id BPS atau indicator.id WDI
  sumber TEXT NOT NULL CHECK (sumber IN ('bps', 'wdi')),
  nama TEXT NOT NULL,
  kode_sdg TEXT,
  satuan TEXT NOT NULL CHECK (satuan IN ('persen', 'ton', 'kilogram')),
  UNIQUE (seri_kode, sumber, satuan)
) STRICT;

CREATE TABLE wilayah (
  wilayah_kode INTEGER NOT NULL PRIMARY KEY, -- kode BPS x 100; 9999 = Indonesia
  nama_wilayah TEXT NOT NULL,
  tingkat TEXT NOT NULL CHECK (tingkat IN ('provinsi', 'nasional')),
  CHECK ((wilayah_kode = 9999) = (tingkat = 'nasional')),
  UNIQUE (wilayah_kode, nama_wilayah)
) STRICT;

CREATE TABLE silver (
  sumber TEXT NOT NULL,
  seri_kode TEXT NOT NULL,
  wilayah_kode INTEGER NOT NULL,
  nama_wilayah TEXT NOT NULL,
  periode TEXT NOT NULL,
  jenis_periode TEXT NOT NULL CHECK (
    jenis_periode IN ('tahun', 'semester', 'triwulan', 'bulan')
  ),
  rincian TEXT NOT NULL,
  nilai REAL NOT NULL CHECK (nilai BETWEEN -1e300 AND 1e300),
  satuan TEXT NOT NULL,
  _berkas_raw TEXT NOT NULL,
  _sha256_raw TEXT NOT NULL,
  -- Sama dengan KUNCI di skema.py; `sumber` di akhir karena seri_kode sudah menentukannya (FK ke seri),
  -- sehingga pencarian per seri_kode/wilayah/periode memakai indeks kunci primer.
  PRIMARY KEY (
    seri_kode,
    wilayah_kode,
    periode,
    rincian,
    _berkas_raw,
    sumber
  ),
  CHECK (
    (
      jenis_periode = 'tahun'
      AND periode GLOB '[0-9][0-9][0-9][0-9]'
    )
    OR (
      jenis_periode = 'semester'
      AND periode GLOB '[0-9][0-9][0-9][0-9]-S[12]'
    )
    OR (
      jenis_periode = 'triwulan'
      AND periode GLOB '[0-9][0-9][0-9][0-9]-Q[1-4]'
    )
    OR (
      jenis_periode = 'bulan'
      AND periode GLOB '[0-9][0-9][0-9][0-9]-[01][0-9]'
      AND substr (periode, 6, 2) BETWEEN '01' AND '12'
    )
  ),
  CHECK (
    satuan <> 'persen'
    OR nilai BETWEEN 0 AND 100
  ),
  CHECK (
    satuan = 'persen'
    OR nilai >= 0
  ),
  FOREIGN KEY (seri_kode, sumber, satuan) REFERENCES seri (seri_kode, sumber, satuan),
  FOREIGN KEY (wilayah_kode, nama_wilayah) REFERENCES wilayah (wilayah_kode, nama_wilayah),
  FOREIGN KEY (_berkas_raw, _sha256_raw) REFERENCES berkas_raw (berkas, sha256)
) STRICT,
WITHOUT ROWID;

CREATE INDEX silver_wilayah_periode ON silver (wilayah_kode, periode);

-- Baris Indonesia dipisahkan dari baris provinsi (agar tidak dijumlahkan dua kali).
CREATE VIEW v_provinsi AS
SELECT
  s.*
FROM
  silver s
  JOIN wilayah w USING (wilayah_kode)
WHERE
  w.tingkat = 'provinsi';

CREATE VIEW v_nasional AS
SELECT
  s.*
FROM
  silver s
  JOIN wilayah w USING (wilayah_kode)
WHERE
  w.tingkat = 'nasional';
