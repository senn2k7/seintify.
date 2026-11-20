"""Melatih model regresi nilai ujian dan menyimpannya (P9-P10).

Dataset: Student Performance Factors (Kaggle), file StudentPerformanceFactors.csv.
Jalankan dari folder proyek:
    python -m portal.ml.latih_model
Keluaran: model_nilai.joblib dan metrik.json di folder portal/ml/.
"""
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

FOLDER = Path(__file__).resolve().parent
DATA = FOLDER / 'data' / 'StudentPerformanceFactors.csv'
MODEL = FOLDER / 'model_nilai.joblib'
METRIK = FOLDER / 'metrik.json'

# URUTAN kolom ini harus sama persis dengan urutan saat prediksi di web.
# Hours_Studied = jam belajar per MINGGU. Sleep_Hours sengaja tidak dipakai:
# korelasinya dengan nilai ~0 (-0,017) sehingga koefisiennya hanya noise.
FITUR = ['Hours_Studied', 'Attendance', 'Previous_Scores', 'Tutoring_Sessions']
TARGET = 'Exam_Score'


def muat_data():
    """Baca CSV lalu bersihkan: buang baris kosong di kolom terpakai dan
    baris dengan nilai di luar 0-100 (ada 1 baris bernilai 101)."""
    df = pd.read_csv(DATA)
    df = df.dropna(subset=FITUR + [TARGET])
    df = df[(df[TARGET] >= 0) & (df[TARGET] <= 100)]
    return df.reset_index(drop=True)


def latih():
    df = muat_data()
    X, y = df[FITUR], df[TARGET]
    X_latih, X_uji, y_latih, y_uji = train_test_split(
        X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_latih, y_latih)

    pred = model.predict(X_uji)
    metrik = {
        'n_data': int(len(df)), 'n_latih': int(len(X_latih)),
        'n_uji': int(len(X_uji)),
        'mae': round(float(mean_absolute_error(y_uji, pred)), 2),
        'r2': round(float(r2_score(y_uji, pred)), 3),
        'intercept': round(float(model.intercept_), 2),
        'koefisien': {f: round(float(c), 3)
                      for f, c in zip(FITUR, model.coef_)},
        'rentang': {f: [float(df[f].min()), float(df[f].max())]
                    for f in FITUR},
    }
    joblib.dump(model, MODEL)
    METRIK.write_text(json.dumps(metrik, indent=2), encoding='utf-8')
    return metrik


if __name__ == '__main__':
    print(json.dumps(latih(), indent=2))
