# Dashboard Analitik Sentimen Sumud Flotilla

Repository ini berisi dashboard analitik untuk menganalisis sentimen percakapan **YouTube Comment** dan **Facebook Comment** tentang isu **Sumud Flotilla**. Data yang digunakan bersifat statis dari file CSV yang telah disiapkan dalam folder `data` dan `public/data`.

## Tujuan Riset

Dashboard ini dibuat untuk mendukung analisis awal terhadap respons publik digital di media sosial mengenai Sumud Flotilla. Fokus risetnya adalah memetakan kecenderungan sentimen komentar publik, membandingkan percakapan lintas platform, serta melihat pola engagement dan kata kunci dominan yang muncul dalam percakapan YouTube dan Facebook.

Secara akademik, dashboard ini dapat digunakan sebagai alat bantu eksplorasi data dalam kajian komunikasi digital, opini publik, analisis percakapan media sosial, dan konstruksi isu kemanusiaan di ruang digital.

## Sumber Data

Kolom data utama:

- `Id`
- `UserId`
- `Avatar`
- `Author`
- `Content`
- `Url`
- `ReactionsCount`
- `Depth`
- `SubCommentsCount`
- `CommentAt`

Data yang telah digabung dan diproses tersedia pada:

```text
public/data/sumud_comments_sentiment.csv
streamlit_app/data/processed/sumud_comments_with_sentiment.csv
```

## Ringkasan Data

- Total komentar: **320**
- YouTube: **93** komentar
- Facebook: **227** komentar
- Positif: **34** komentar
- Netral: **211** komentar
- Negatif: **75** komentar

## Struktur Folder

```text
.
├── index.html
├── package.json
├── vercel.json
├── public/
│   └── data/
│       ├── sumud_comments_sentiment.csv
│       └── raw/
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   └── styles.css
├── streamlit_app/
│   ├── app.py
│   ├── requirements.txt
│   ├── data/
│   └── src/
├── requirements.txt
└── README.md
```

## Catatan Penting tentang Vercel dan Streamlit

Vercel mendukung deployment frontend seperti Vite/React dan juga Python Serverless Functions. Namun, aplikasi Streamlit membutuhkan proses server interaktif yang berjalan terus-menerus dan WebSocket, sehingga **Streamlit tidak ideal untuk dijalankan langsung sebagai aplikasi native di Vercel**.

Karena itu repository ini menyediakan dua versi:

1. **Versi Vercel**: dashboard web statis berbasis React/Vite di root repository.
2. **Versi Streamlit**: dashboard Python di folder `streamlit_app/`, cocok dijalankan lokal atau di Streamlit Community Cloud.

## Menjalankan Dashboard Vercel/React secara Lokal

```bash
npm install
npm run dev
```

Buka alamat lokal yang muncul, biasanya:

```text
http://localhost:5173
```

## Deploy ke Vercel

1. Push repository ini ke GitHub.
2. Buka Vercel.
3. Pilih **Add New Project**.
4. Import repository GitHub ini.
5. Gunakan konfigurasi berikut:

```text
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
```

File `vercel.json` sudah disiapkan agar Vercel membaca konfigurasi build dengan benar.

## Menjalankan Dashboard Streamlit secara Lokal

Masuk ke folder Streamlit:

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

## Analisis Sentimen

Pada versi Streamlit, modul `src/indobert_sentiment.py` disiapkan untuk menggunakan model Transformers/IndoBERT-compatible Bahasa Indonesia. Model default:

```text
w11wo/indonesian-roberta-base-sentiment-classifier
```

Jika model tidak dapat dimuat karena koneksi internet atau keterbatasan runtime, aplikasi memakai fallback **lexicon Bahasa Indonesia**.

Pada versi Vercel, sentimen sudah diproses lebih dahulu ke dalam CSV statis agar dashboard dapat berjalan cepat tanpa backend Python.

## Fitur Dashboard

- Filter platform: YouTube/Facebook.
- Filter sentimen: positif, negatif, netral.
- Filter kata kunci dan minimum reaksi.
- Pie chart distribusi sentimen.
- Grafik distribusi platform.
- Tren komentar berdasarkan tanggal.
- Kata kunci dominan.
- Tabel hasil sentimen per komentar.
- Export hasil filter ke CSV.

## Keterbatasan Metodologis

Analisis sentimen media sosial memiliki keterbatasan karena komentar dapat mengandung sarkasme, ironi, singkatan, campuran bahasa, emoji, dan konteks politik-kemanusiaan yang kompleks. Oleh karena itu, hasil dashboard ini sebaiknya dipahami sebagai pemetaan awal dan dapat dilanjutkan dengan validasi manual atau coding kualitatif.

## Lisensi dan Etika Data

Data komentar digunakan untuk kepentingan akademik dan analitik. Hindari penyalahgunaan data personal pengguna, dan gunakan hasil analisis secara proporsional sesuai prinsip etika riset komunikasi digital.
