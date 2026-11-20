# Deploy ke Vercel

Folder `sistemcerdas` (yang berisi `manage.py`) harus menjadi **root** proyek Vercel.
File yang sudah disiapkan: `vercel.json`, `api/index.py`, `.python-version`, `.vercelignore`,
serta pengaturan produksi di `config/settings.py` (WhiteNoise untuk CSS/JS).

## 0. Persiapan lokal (sekali saja)
```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python -m portal.ml.latih_model      # latih ulang agar model cocok dengan versi scikit-learn
pip show scikit-learn                # catat Version-nya, mis. 1.5.2
```
1. Buka `requirements.txt`, ubah `scikit-learn` menjadi `scikit-learn==<versi tadi>`
   (menghindari galat saat memuat `model_nilai.joblib` karena beda versi).
2. File `portal/ml/model_nilai.joblib` **harus ikut ter-upload** (sudah tidak di-ignore lagi).

## Cara A — lewat GitHub (disarankan)
1. Buat repository GitHub baru, lalu dorong **isi folder `sistemcerdas`** sebagai root repo:
   ```powershell
   cd sistemcerdas
   git init
   git add .
   git commit -m "Portal prediksi nilai"
   git branch -M main
   git remote add origin https://github.com/USERNAME/NAMA-REPO.git
   git push -u origin main
   ```
   Pastikan `.env` TIDAK ikut (sudah ada di `.gitignore`).
2. Buka https://vercel.com/new → **Import** repository tersebut.
3. **Framework Preset**: Other. **Root Directory**: biarkan `./` (atau pilih `sistemcerdas`
   jika repo-mu berisi folder induk). Biarkan Build/Output command kosong.
4. Buka **Environment Variables**, tambahkan:

   | Nama | Nilai |
   |---|---|
   | `DJANGO_SECRET_KEY` | string acak panjang (buat dengan `python -c "import secrets;print(secrets.token_urlsafe(50))"`) |
   | `GROQ_API_KEY` | API key dari console.groq.com |
   | `GROQ_MODEL` | (opsional) `llama-3.3-70b-versatile` |

5. Klik **Deploy**. Setelah selesai, buka URL `https://nama-proyek.vercel.app`.

## Cara B — lewat Vercel CLI
```powershell
npm i -g vercel
cd sistemcerdas
vercel login
vercel            # ikuti pertanyaan (Framework: Other)
vercel env add DJANGO_SECRET_KEY
vercel env add GROQ_API_KEY
vercel --prod
```

## Jika memakai domain sendiri
Tambahkan environment variable `ALLOWED_HOSTS=domainmu.com` dan
`CSRF_TRUSTED_ORIGINS=https://domainmu.com`, lalu redeploy.

## Pemecahan masalah
| Gejala | Penyebab & solusi |
|---|---|
| Halaman tanpa gaya (polos) | Pastikan `whitenoise` ada di `requirements.txt` lalu redeploy; cek `/static/portal/style.css` terbuka. |
| "Model belum dilatih" | `model_nilai.joblib` tidak ter-commit. Jalankan `git add -f portal/ml/model_nilai.joblib`, commit, push. |
| Galat saat memuat model / `InconsistentVersionWarning` | Versi scikit-learn beda. Latih ulang model lokal dan pin versinya (langkah 0). |
| `DisallowedHost` / 400 | Tambahkan domain ke `ALLOWED_HOSTS` (lihat di atas). |
| 403 CSRF saat tombol AI ditekan | Tambahkan domain ke `CSRF_TRUSTED_ORIGINS`. |
| "Fitur AI belum aktif" | `GROQ_API_KEY` belum diisi di Vercel → tambahkan lalu **Redeploy** (env baru hanya berlaku di deploy berikutnya). |
| Build gagal: ukuran melebihi 250 MB | pandas + scikit-learn + scipy cukup besar. Coba hapus paket tak terpakai; jika tetap besar, deploy di Render/Railway/PythonAnywhere. |
| 500 Error | Buka Vercel → Project → **Logs** untuk melihat traceback. |

## Catatan
- Vercel bersifat serverless: filesystem hanya-baca, jadi jangan menyimpan data ke `db.sqlite3` (aplikasi ini tidak membutuhkannya).
- Batas permintaan AI (15/menit) disimpan di memori per instance, jadi tidak sepenuhnya akurat di serverless.
