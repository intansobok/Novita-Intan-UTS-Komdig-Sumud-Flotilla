import streamlit as st
import pandas as pd

from src.preprocess import load_static_data, get_top_words
from src.indobert_sentiment import (
    DEFAULT_TRANSFORMER_MODEL,
    add_indobert_sentiment_columns,
)
from src.charts import (
    sentiment_pie,
    platform_bar,
    sentiment_by_platform,
    trend_chart,
    reaction_chart,
    top_authors_chart,
    top_words_chart,
)

st.set_page_config(
    page_title="Dashboard Sentimen Sumud Flotilla",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
<style>
.block-container {padding-top: 1.5rem;}
.metric-card {
    background: #ffffff;
    border: 1px solid #e6eaf0;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}
.small-note {color: #667085; font-size: 0.9rem;}
</style>
""",
    unsafe_allow_html=True,
)

st.title("📊 Dashboard Analitik Sentimen Percakapan Sumud Flotilla")
st.caption(
    "Sumber data statis: komentar YouTube dan Facebook dari file CSV yang dilampirkan. "
    "Sentimen diklasifikasikan menjadi Positif, Negatif, dan Netral."
)

with st.sidebar:
    st.header("Metode Analisis")
    use_transformer = st.toggle(
        "Gunakan model Transformers/IndoBERT",
        value=True,
        help=(
            "Aktifkan untuk memakai model sentiment-analysis Bahasa Indonesia dari Hugging Face. "
            "Jika model gagal dimuat, dashboard otomatis memakai fallback lexicon."
        ),
    )
    model_name = st.text_input(
        "Nama model Hugging Face",
        value=DEFAULT_TRANSFORMER_MODEL,
        help=(
            "Bisa diganti dengan checkpoint IndoBERT lain yang sudah fine-tuned untuk sentimen Bahasa Indonesia."
        ),
        disabled=not use_transformer,
    )
    batch_size = st.slider("Batch size prediksi", 4, 64, 16, 4, disabled=not use_transformer)


@st.cache_data(show_spinner=False)
def load_base_data():
    return load_static_data("data/processed/sumud_comments_combined.csv")


@st.cache_data(show_spinner="Menganalisis sentimen komentar...")
def prepare_data(use_transformer: bool, model_name: str, batch_size: int):
    df = load_base_data()
    if use_transformer:
        df, method_used, warning = add_indobert_sentiment_columns(
            df,
            text_col="Content",
            model_name=model_name,
            batch_size=batch_size,
            fallback_to_lexicon=True,
        )
    else:
        from src.sentiment import add_sentiment_columns

        df = add_sentiment_columns(df, text_col="Content")
        df["SentimentConfidence"] = None
        df["SentimentMethod"] = "Lexicon Bahasa Indonesia"
        method_used = "Lexicon Bahasa Indonesia"
        warning = None
    return df, method_used, warning


df, method_used, warning = prepare_data(use_transformer, model_name, batch_size)

with st.sidebar:
    st.markdown("---")
    st.header("Filter Data")
    platform_options = sorted(df["Platform"].dropna().unique().tolist())
    selected_platform = st.multiselect("Platform", platform_options, default=platform_options)

    sentiment_options = ["Positif", "Netral", "Negatif"]
    selected_sentiment = st.multiselect("Sentimen", sentiment_options, default=sentiment_options)

    keyword = st.text_input("Cari kata/isu dalam komentar", placeholder="contoh: flotilla, israel, bantuan")

    min_reactions = int(df["ReactionsCount"].fillna(0).min()) if len(df) else 0
    max_reactions = int(df["ReactionsCount"].fillna(0).max()) if len(df) else 0
    reaction_range = st.slider(
        "Rentang jumlah reaksi/like",
        min_value=min_reactions,
        max_value=max_reactions,
        value=(min_reactions, max_reactions),
    )

    st.markdown("---")
    st.markdown("**Catatan Metode**")
    st.write(
        "Dashboard menggunakan klasifikasi tiga kelas: Positif, Negatif, dan Netral. "
        "Mode utama memakai model Transformers/IndoBERT yang cocok untuk Bahasa Indonesia; "
        "fallback lexicon tersedia agar dashboard tetap berjalan bila model belum terunduh."
    )

if warning:
    st.warning(warning)
else:
    st.success(f"Metode sentimen aktif: {method_used}")

filtered = df.copy()
filtered = filtered[filtered["Platform"].isin(selected_platform)]
filtered = filtered[filtered["Sentiment"].isin(selected_sentiment)]
filtered = filtered[
    (filtered["ReactionsCount"].fillna(0) >= reaction_range[0])
    & (filtered["ReactionsCount"].fillna(0) <= reaction_range[1])
]

if keyword.strip():
    kw = keyword.strip().lower()
    filtered = filtered[filtered["Content"].fillna("").str.lower().str.contains(kw, na=False)]

total_comments = len(filtered)
total_authors = filtered["Author"].nunique() if total_comments else 0
total_reactions = int(filtered["ReactionsCount"].fillna(0).sum()) if total_comments else 0
avg_words = round(filtered["word_count"].fillna(0).mean(), 2) if total_comments else 0

sentiment_counts = filtered["Sentiment"].value_counts() if total_comments else pd.Series(dtype=int)
pos_count = int(sentiment_counts.get("Positif", 0))
neu_count = int(sentiment_counts.get("Netral", 0))
neg_count = int(sentiment_counts.get("Negatif", 0))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Komentar", f"{total_comments:,}")
c2.metric("Positif", f"{pos_count:,}")
c3.metric("Netral", f"{neu_count:,}")
c4.metric("Negatif", f"{neg_count:,}")

c5, c6, c7 = st.columns(3)
c5.metric("Akun/Author Unik", f"{total_authors:,}")
c6.metric("Total Reaksi/Like", f"{total_reactions:,}")
c7.metric("Rata-rata Kata", avg_words)

st.markdown("### Distribusi Sentimen")
left, right = st.columns([1, 1.3])
with left:
    st.plotly_chart(sentiment_pie(filtered), use_container_width=True)
with right:
    st.markdown("#### Tabel Ringkasan Sentimen")
    if total_comments:
        summary = (
            filtered["Sentiment"]
            .value_counts()
            .reindex(["Positif", "Netral", "Negatif"], fill_value=0)
            .reset_index()
        )
        summary.columns = ["Sentimen", "Jumlah Komentar"]
        summary["Persentase"] = (summary["Jumlah Komentar"] / total_comments * 100).round(2)
        st.dataframe(summary, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada data untuk ditampilkan.")

st.markdown("### Ringkasan Platform dan Engagement")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.plotly_chart(platform_bar(filtered), use_container_width=True)
with col2:
    st.plotly_chart(sentiment_by_platform(filtered), use_container_width=True)
with col3:
    st.plotly_chart(reaction_chart(filtered), use_container_width=True)

st.markdown("### Tren dan Kata Kunci Percakapan")
col4, col5 = st.columns([1.2, 1])
with col4:
    st.plotly_chart(trend_chart(filtered), use_container_width=True)
with col5:
    words = get_top_words(filtered["clean_content"], top_n=20)
    st.plotly_chart(top_words_chart(words), use_container_width=True)

st.markdown("### Akun Paling Aktif")
st.plotly_chart(top_authors_chart(filtered), use_container_width=True)

st.markdown("### Interpretasi Otomatis Sementara")
if total_comments == 0:
    st.warning("Tidak ada data yang sesuai dengan filter.")
else:
    dominant = sentiment_counts.idxmax()
    dominant_count = int(sentiment_counts.max())
    dominant_pct = round(dominant_count / total_comments * 100, 2)
    st.info(
        f"Dari {total_comments:,} komentar yang tampil, sentimen dominan adalah "
        f"**{dominant}** sebanyak **{dominant_count:,} komentar** atau **{dominant_pct}%**. "
        "Hasil ini dapat digunakan sebagai pemetaan awal percakapan publik tentang Sumud Flotilla. "
        "Untuk kebutuhan akademik, kutipan komentar penting tetap perlu divalidasi manual, terutama pada "
        "komentar yang mengandung sarkasme, ironi, singkatan, atau konteks politik-keagamaan."
    )

st.markdown("### Tabel Sentimen Setiap Komentar")
show_cols = [
    "Platform",
    "Author",
    "Content",
    "Sentiment",
    "SentimentConfidence",
    "SentimentScore",
    "SentimentMethod",
    "ReactionsCount",
    "Depth",
    "SubCommentsCount",
    "CommentAt",
    "Url",
]
existing_cols = [col for col in show_cols if col in filtered.columns]
st.dataframe(filtered[existing_cols], use_container_width=True, height=460)

csv = filtered[existing_cols].to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="⬇️ Unduh tabel sentimen komentar sebagai CSV",
    data=csv,
    file_name="hasil_sentimen_per_komentar_sumud_flotilla.csv",
    mime="text/csv",
)
