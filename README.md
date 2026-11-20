# Portal Prediksi Nilai Mahasiswa

Proyek individu Mata Kuliah Sistem Cerdas. Website Django ini berfokus pada prediksi nilai ujian berdasarkan faktor kebiasaan belajar menggunakan Machine Learning (regresi linear), visualisasi data, dan penjelasan hasil melalui Groq AI.

## Fitur
- Dashboard ringkasan proyek, dataset, algoritma, dan metrik model.
- Form prediksi dengan empat fitur: `Hours_Studied`, `Attendance`, `Previous_Scores`, dan `Tutoring_Sessions`.
- Hasil prediksi nilai 0-100 beserta predikat.
- Grafik rata-rata `Exam_Score` berdasarkan kelompok jam belajar per minggu.
- Penjelasan AI Groq untuk hasil prediksi, arah koefisien, metrik evaluasi, dan grafik.
- Validasi rentang input berdasarkan rentang data yang digunakan saat training.

## Teknologi
Python, Django, Pandas, scikit-learn, Joblib, HTML, CSS, JavaScript, dan Groq API.

## Cara menjalankan di Windows
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m portal.ml.latih_model
python manage.py test
python manage.py runserver
```
Buka `http://127.0.0.1:8000/`.

## Mengaktifkan Groq AI
1. Buat API key melalui `https://console.groq.com/`.
2. Salin `.env.example` menjadi `.env` pada folder yang sama dengan `manage.py`.
3. Isi `GROQ_API_KEY=...` pada `.env` (jangan gunakan tanda kurung sudut).
4. Pastikan `.env` berada tepat di folder yang berisi `manage.py`.
5. Instal dependensi dengan `pip install -r requirements.txt`.
6. Hentikan server dengan `Ctrl+C`, lalu jalankan ulang `python manage.py runserver`.
7. Buka halaman Prediksi Nilai, masukkan data, tekan **Prediksi**, lalu klik **Jelaskan hasil ini dengan AI**.

API key hanya dibaca oleh backend. Jangan menaruh API key di HTML, JavaScript, atau repository publik. Tanpa API key, fitur prediksi dan grafik tetap dapat digunakan, sedangkan penjelasan AI tidak aktif.

Model default `llama-3.3-70b-versatile` dan dapat diganti melalui `GROQ_MODEL` pada `.env` jika model tersebut tidak tersedia pada akunmu.

## Deploy ke Vercel
Lihat panduan lengkap di [DEPLOY_VERCEL.md](DEPLOY_VERCEL.md).

## Struktur utama
```text
config/
  settings.py
  urls.py
portal/
  forms.py
  views.py
  urls.py
  ml/
    data/StudentPerformanceFactors.csv
    latih_model.py
    model_nilai.joblib       # dibuat saat training
    metrik.json              # dibuat saat training
  services/
    ai.py
    prediksi.py
  templates/portal/
    base.html
    beranda.html
    prediksi.html
    _ai.html
  static/portal/style.css
  tests.py
manage.py
requirements.txt
```

## Dataset dan model
- Dataset: **Student Performance Factors** dari Kaggle.
- Target: `Exam_Score`.
- Fitur: `Hours_Studied` (jam per minggu), `Attendance` (persentase), `Previous_Scores`, dan `Tutoring_Sessions`.
- Algoritma: `LinearRegression` dari scikit-learn.
- Pembagian data: 80% training dan 20% testing dengan `random_state=42`.
- Evaluasi yang tersimpan pada paket saat ini: MAE 1,25 dan R² 0,68. Jalankan ulang training untuk menghasilkan metrik sesuai versi library dan file dataset di komputermu.
- Pembersihan data membuang satu baris dengan target di luar rentang 0-100; data tersisa 6.606 baris.
- `Sleep_Hours` tidak digunakan karena korelasinya dengan target pada analisis awal sangat kecil. Model menunjukkan hubungan statistik, bukan sebab-akibat.

### Sumber dan lisensi dataset — lengkapi sebelum pengumpulan
- URL dataset Kaggle: **isi URL halaman dataset**.
- Pembuat dataset: **isi sesuai halaman Kaggle**.
- Lisensi: **isi sesuai bagian License/Data Card Kaggle**.
- Status sintetis: **periksa dan tulis sesuai keterangan pembuat dataset**.

## Keamanan dan batasan
- File `.env` dikecualikan melalui `.gitignore`.
- Endpoint AI hanya menerima POST dan menyusun prompt di server dari form yang tervalidasi.
- Hasil prediksi adalah estimasi edukatif, bukan jaminan nilai aktual.
- Kinerja model bergantung pada kualitas dan keterwakilan dataset.

## Identitas dan penggunaan AI
- Nama: **isi nama**
- NIM: **isi NIM**
- Proyek dikerjakan secara individu.
- Catatan penggunaan AI: **sesuaikan dengan aturan dosen dan jelaskan bagian yang dibantu AI secara transparan**.
