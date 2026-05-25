# Dashboard Analitik Sentimen Sumud Flotilla

Dashboard web sederhana berbasis **Python + Streamlit** untuk menganalisis sentimen percakapan **YouTube Comment** dan **Facebook Comment** tentang **Sumud Flotilla**.

Data bersifat statis dan sudah diletakkan di folder `data/`. Dashboard membaca file gabungan berikut:

```text
data/processed/sumud_comments_combined.csv
```

## Struktur Folder

```text
sumud_flotilla_sentiment_dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
├── data/
│   ├── raw/
│   │   ├── youtube_comments.csv
│   │   ├── facebook_comments_post_1.csv
│   │   └── facebook_comments_post_2.csv
│   └── processed/
│       └── sumud_comments_combined.csv
└── src/
    ├── __init__.py
    ├── preprocess.py
    ├── sentiment.py
    ├── indobert_sentiment.py
    └── charts.py
```

## Fitur Dashboard

- membaca data komentar YouTube dan Facebook dari CSV statis;
- membersihkan teks komentar;
- mengklasifikasikan sentimen setiap komentar menjadi **Positif**, **Negatif**, dan **Netral**;
- mode utama menggunakan model **Transformers/IndoBERT-compatible** untuk Bahasa Indonesia;
- fallback lexicon Bahasa Indonesia agar dashboard tetap berjalan jika model belum dapat dimuat;
- menampilkan **pie chart distribusi sentimen**;
- menampilkan **tabel sentimen per komentar**;
- filter berdasarkan platform, sentimen, kata kunci, dan jumlah reaksi;
- visualisasi sentimen per platform, tren komentar, engagement, kata kunci dominan, dan akun paling aktif;
- export tabel hasil analisis ke CSV.

## Model Sentimen

Secara default dashboard memakai model Hugging Face berikut:

```text
w11wo/indonesian-roberta-base-sentiment-classifier
```

Model ini cocok untuk klasifikasi sentimen Bahasa Indonesia tiga kelas. Bila ingin memakai checkpoint IndoBERT lain, ubah nama model melalui sidebar dashboard atau environment variable:

```bash
export SENTIMENT_MODEL_NAME="nama-model-anda"
```

Catatan akademik: model otomatis perlu tetap divalidasi secara manual, terutama untuk komentar yang mengandung sarkasme, ironi, campuran bahasa, istilah politik-keagamaan, atau konteks konflik internasional.

## Cara Menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Saat pertama kali dijalankan dengan mode Transformers/IndoBERT, aplikasi akan mengunduh model dari Hugging Face. Proses ini membutuhkan koneksi internet dan bisa memerlukan waktu beberapa menit.

## Deploy ke Streamlit Community Cloud

1. Push folder proyek ini ke GitHub.
2. Buka Streamlit Community Cloud.
3. Pilih repository.
4. Main file path: `app.py`.
5. Deploy.

## Kolom Data

Dashboard mendukung kolom berikut:

```text
Id, UserId, Avatar, Author, Content, Url, ReactionsCount, Depth, SubCommentsCount, CommentAt
```

Selain kolom asli, dashboard menambahkan:

```text
Platform, clean_content, word_count, CommentAt_parsed, Sentiment, SentimentConfidence, SentimentScore, SentimentMethod
```
