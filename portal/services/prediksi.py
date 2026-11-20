"""Layanan Prediksi ML: memuat model, memprediksi, dan menyiapkan grafik."""
import json
from functools import lru_cache

import joblib
import pandas as pd

from ..ml.latih_model import FITUR, METRIK, MODEL, TARGET, muat_data


class ModelBelumAda(Exception):
    pass


@lru_cache(maxsize=1)
def muat_model():
    """Model dimuat sekali saja, bukan di setiap request."""
    if not MODEL.exists():
        raise ModelBelumAda('Model belum dilatih.')
    return joblib.load(MODEL)


def muat_metrik():
    if not METRIK.exists():
        raise ModelBelumAda('Metrik belum ada.')
    return json.loads(METRIK.read_text(encoding='utf-8'))


def prediksi(masukan):
    """masukan: dict {nama_fitur: nilai}. Mengembalikan nilai (dibatasi 0-100)."""
    # DataFrame dengan nama & urutan kolom yang sama seperti saat training
    x = pd.DataFrame([[masukan[f] for f in FITUR]], columns=FITUR)
    hasil = float(muat_model().predict(x)[0])
    return round(min(max(hasil, 0), 100), 1)


def predikat(nilai):
    if nilai >= 85:
        return 'A'
    if nilai >= 70:
        return 'B'
    if nilai >= 55:
        return 'C'
    if nilai >= 40:
        return 'D'
    return 'E'


# Kelompok jam belajar per minggu (bawah <= jam < atas)
KELOMPOK = [(0, 10, '<10'), (10, 15, '10-14'), (15, 20, '15-19'),
            (20, 25, '20-24'), (25, 30, '25-29'), (30, 100, '30+')]


def data_grafik(jam_belajar=None):
    """Rata-rata nilai ujian per kelompok jam belajar per minggu."""
    df = muat_data()
    batang = []
    for bawah, atas, label in KELOMPOK:
        sub = df[(df['Hours_Studied'] >= bawah) & (df['Hours_Studied'] < atas)]
        rata = round(float(sub[TARGET].mean()), 1) if len(sub) else 0
        aktif = (jam_belajar is not None and bawah <= jam_belajar < atas)
        batang.append({'label': label, 'rata': rata, 'n': int(len(sub)),
                       'aktif': aktif})
    return batang
