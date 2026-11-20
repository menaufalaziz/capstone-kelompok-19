import csv, hashlib
from pathlib import Path

akar = Path("data/raw")
manifest = akar / "MANIFEST.csv"   # sesuaikan jika letaknya berbeda

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()

terdaftar, masalah = set(), 0
with open(manifest, newline="", encoding="utf-8") as f:
    for baris in csv.DictReader(f):
        p = akar / baris["berkas"]
        terdaftar.add(p.resolve())
        if not p.exists():
            print("HILANG  ", baris["berkas"]); masalah += 1
        elif p.stat().st_size != int(baris["bait"]):
            print("UKURAN  ", baris["berkas"]); masalah += 1
        elif sha256_file(p) != baris["sha256"]:
            print("BERBEDA ", baris["berkas"]); masalah += 1

for p in akar.rglob("*"):
    if p.is_file() and p.resolve() not in terdaftar and p.name != "MANIFEST.csv":
        print("EKSTRA  ", p.relative_to(akar)); masalah += 1

print("Semua cocok." if masalah == 0 else f"{masalah} masalah ditemukan.")
