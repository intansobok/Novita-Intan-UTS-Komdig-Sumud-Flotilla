import pandas as pd
import plotly.express as px

COLOR_MAP = {
    "Positif": "#16a34a",
    "Netral": "#64748b",
    "Negatif": "#dc2626",
    "YouTube": "#ef4444",
    "Facebook": "#2563eb"
}

def empty_fig(title):
    fig = px.scatter(title=title)
    fig.update_layout(height=350)
    return fig

def sentiment_pie(df):
    if df.empty:
        return empty_fig("Distribusi Sentimen")
    counts = df["Sentiment"].value_counts().reset_index()
    counts.columns = ["Sentiment", "count"]
    fig = px.pie(
        counts, names="Sentiment", values="count",
        title="Distribusi Sentimen",
        color="Sentiment", color_discrete_map=COLOR_MAP,
        hole=0.45
    )
    fig.update_layout(height=360)
    return fig

def platform_bar(df):
    if df.empty:
        return empty_fig("Volume Komentar per Platform")
    counts = df["Platform"].value_counts().reset_index()
    counts.columns = ["Platform", "count"]
    fig = px.bar(
        counts, x="Platform", y="count", text="count",
        title="Volume Komentar per Platform",
        color="Platform", color_discrete_map=COLOR_MAP
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=360, yaxis_title="Jumlah Komentar", xaxis_title="")
    return fig

def sentiment_by_platform(df):
    if df.empty:
        return empty_fig("Sentimen per Platform")
    pivot = df.groupby(["Platform", "Sentiment"]).size().reset_index(name="count")
    fig = px.bar(
        pivot, x="Platform", y="count", color="Sentiment",
        title="Sentimen per Platform",
        barmode="group", color_discrete_map=COLOR_MAP
    )
    fig.update_layout(height=360, yaxis_title="Jumlah Komentar", xaxis_title="")
    return fig

def trend_chart(df):
    if df.empty or df["CommentAt_parsed"].isna().all():
        return empty_fig("Tren Komentar Berdasarkan Waktu")
    temp = df.dropna(subset=["CommentAt_parsed"]).copy()
    temp["date"] = temp["CommentAt_parsed"].dt.date
    trend = temp.groupby(["date", "Sentiment"]).size().reset_index(name="count")
    fig = px.line(
        trend, x="date", y="count", color="Sentiment",
        markers=True, title="Tren Komentar Berdasarkan Waktu",
        color_discrete_map=COLOR_MAP
    )
    fig.update_layout(height=380, xaxis_title="Tanggal", yaxis_title="Jumlah Komentar")
    return fig

def reaction_chart(df):
    if df.empty:
        return empty_fig("Rata-rata Reaksi per Sentimen")
    temp = df.groupby("Sentiment")["ReactionsCount"].mean().reset_index()
    fig = px.bar(
        temp, x="Sentiment", y="ReactionsCount",
        color="Sentiment", text_auto=".2f",
        title="Rata-rata Reaksi/Like per Sentimen",
        color_discrete_map=COLOR_MAP
    )
    fig.update_layout(height=380, xaxis_title="", yaxis_title="Rata-rata Reaksi/Like")
    return fig

def top_authors_chart(df):
    if df.empty:
        return empty_fig("Akun Paling Aktif")
    top = df["Author"].fillna("Tanpa Nama").value_counts().head(10).reset_index()
    top.columns = ["Author", "count"]
    fig = px.bar(top, x="count", y="Author", orientation="h", text="count", title="10 Akun Paling Aktif")
    fig.update_layout(height=420, xaxis_title="Jumlah Komentar", yaxis_title="")
    return fig

def top_words_chart(words_df):
    if words_df.empty:
        return empty_fig("Kata Kunci Dominan")
    fig = px.bar(
        words_df.sort_values("count", ascending=True),
        x="count", y="word", orientation="h",
        text="count", title="20 Kata Kunci Dominan"
    )
    fig.update_layout(height=420, xaxis_title="Frekuensi", yaxis_title="")
    return fig
