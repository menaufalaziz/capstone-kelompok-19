"""Pembantu kecil untuk menulis laporan Markdown dan angka terukur.

Semua angka di reports/ dihitung ulang setiap `python pipeline.py`, jadi laporan tidak pernah
tertinggal dari data. reports/angka.json mengumpulkan angka yang dirujuk README dan laporan tim.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
GAMBAR = REPORTS / "gambar"
_ANGKA = {}


def catat(**angka):
    """Simpan angka terukur (int/float/str) untuk reports/angka.json."""
    _ANGKA.update(angka)


def angka():
    return dict(_ANGKA)


def simpan_angka():
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "angka.json").write_text(
        json.dumps(_ANGKA, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8"
    )


def tulis(nama, teks):
    jalur = REPORTS / nama
    jalur.parent.mkdir(parents=True, exist_ok=True)
    jalur.write_text(teks.rstrip() + "\n", encoding="utf-8")
    return jalur


def tabel_md(df, angka_desimal=2):
    """DataFrame -> tabel Markdown sederhana (tanpa dependensi tabulate)."""
    if df.empty:
        return "_(kosong)_"
    kolom = [str(k) for k in df.columns]

    def sel(v):
        if isinstance(v, (float, np_float if 'np_float' in globals() else float)):
            return "" if v != v else f"{v:,.{angka_desimal}f}"
        return str(v).replace("|", "\\|").replace("\n", " ")

    baris = ["| " + " | ".join(kolom) + " |", "|" + "|".join("---" for _ in kolom) + "|"]
    baris += ["| " + " | ".join(sel(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(baris)
