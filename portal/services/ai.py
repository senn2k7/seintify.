"""Layanan penjelasan hasil prediksi menggunakan Groq Chat Completions."""
import os
import time

from groq import Groq
from groq import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

MODEL_BAWAAN = 'llama-3.3-70b-versatile'
BATAS_PER_MENIT = 15

SISTEM = (
    'Kamu adalah asisten belajar untuk mahasiswa mata kuliah Sistem Cerdas. '
    'Jawab dalam bahasa Indonesia yang mudah dipahami, terstruktur, dan '
    'maksimal sekitar 250 kata. Gunakan hanya angka dan fakta dari konteks '
    'yang diberikan. Jangan mengarang data. Jelaskan bahwa korelasi bukan '
    'sebab-akibat dan prediksi bukan nilai ujian yang pasti. '
    'Gunakan poin-poin singkat jika membantu.'
)


class AIError(Exception):
    """Galat AI dengan pesan yang aman ditampilkan kepada pengguna."""


_waktu_panggilan = []


def tersedia():
    return bool(os.environ.get('GROQ_API_KEY', '').strip())


def _batasi():
    sekarang = time.time()
    _waktu_panggilan[:] = [t for t in _waktu_panggilan if sekarang - t < 60]
    if len(_waktu_panggilan) >= BATAS_PER_MENIT:
        raise AIError('Terlalu banyak permintaan. Coba lagi sebentar lagi.')
    _waktu_panggilan.append(sekarang)


def tanya(pesan_pengguna):
    """Kirim prompt tervalidasi ke Groq dan kembalikan teks jawaban."""
    kunci = os.environ.get('GROQ_API_KEY', '').strip()
    if not kunci:
        raise AIError('GROQ_API_KEY belum diatur. Periksa file .env di folder yang sama dengan manage.py.')

    _batasi()
    try:
        client = Groq(api_key=kunci, timeout=30.0, max_retries=1)
        hasil = client.chat.completions.create(
            model=os.environ.get('GROQ_MODEL', MODEL_BAWAAN).strip(),
            messages=[
                {'role': 'system', 'content': SISTEM},
                {'role': 'user', 'content': pesan_pengguna},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        teks = hasil.choices[0].message.content
        if not teks:
            raise AIError('Groq tidak memberikan teks jawaban. Silakan coba lagi.')
        return teks.strip()
    except RateLimitError:
        raise AIError('Batas penggunaan Groq tercapai. Coba lagi nanti.')
    except (APIConnectionError, APITimeoutError):
        raise AIError('Tidak bisa terhubung ke Groq. Periksa koneksi internet.')
    except APIStatusError as e:
        if e.status_code in (401, 403):
            raise AIError('API key Groq ditolak. Periksa GROQ_API_KEY di file .env.')
        if e.status_code == 404:
            raise AIError('Model Groq tidak ditemukan. Periksa nilai GROQ_MODEL di file .env.')
        if e.status_code == 429:
            raise AIError('Batas penggunaan Groq tercapai. Coba lagi nanti.')
        raise AIError(f'Groq mengembalikan galat {e.status_code}.')
    except AIError:
        raise
    except Exception:
        raise AIError('Terjadi kesalahan saat meminta penjelasan ke Groq. Periksa konfigurasi dan coba lagi.')


def prompt_prediksi(masukan, nilai, predikat, metrik, grafik):
    kelompok = '; '.join(f"{b['label']} jam: rata-rata {b['rata']}" for b in grafik)
    koef = ', '.join(f'{n} = {k}' for n, k in metrik['koefisien'].items())
    return (
        'Jelaskan hasil prediksi nilai ujian mahasiswa berikut.\n'
        f"Input: jam belajar {masukan['Hours_Studied']} jam/minggu, kehadiran "
        f"{masukan['Attendance']}%, nilai sebelumnya {masukan['Previous_Scores']}, "
        f"sesi bimbingan {masukan['Tutoring_Sessions']} per bulan.\n"
        f'Hasil prediksi: {nilai} (predikat {predikat}).\n'
        f"Model: regresi linear, intercept {metrik['intercept']}, koefisien {koef}. "
        f"MAE {metrik['mae']} poin, R2 {metrik['r2']}.\n"
        f'Diagram batang rata-rata nilai ujian per kelompok jam belajar pada data latih: {kelompok}.\n'
        'Dataset: Student Performance Factors (Kaggle). Nilai ujian dalam data berada pada rentang 55-100.\n'
        'Buat penjelasan dengan empat bagian: (1) arti hasil prediksi dan predikat, '
        '(2) interpretasi pengaruh setiap faktor berdasarkan tanda dan besar koefisien, '
        '(3) cara membaca diagram dan kelompok jam belajar, serta '
        '(4) arti MAE dan R2 beserta keterbatasan model. Jangan menyebut faktor paling '
        'berpengaruh jika angka koefisien tidak mendukung kesimpulan tersebut.'
    )
