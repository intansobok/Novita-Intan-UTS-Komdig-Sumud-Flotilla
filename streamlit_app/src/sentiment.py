import pandas as pd
from src.preprocess import clean_text

POSITIVE_WORDS = {
    "baik","bagus","benar","setuju","dukung","mendukung","bantu","bantuan",
    "selamat","semangat","hebat","kuat","berani","adil","damai","kemanusiaan",
    "solidaritas","peduli","aman","terima","kasih","sukses","lindungi","bebas",
    "merdeka","mulia","ikhlas","salut","terbaik","positif","jujur","cerdas",
    "bermanfaat","membela","menolong","kebaikan","hak","keadilan"
}

NEGATIVE_WORDS = {
    "buruk","jelek","salah","bohong","hoax","tipu","fitnah","benci","marah",
    "gagal","tolak","ditolak","perang","keras","kekerasan","bunuh","mati",
    "serang","penjajah","zionis","israel","jahat","kejam","siksa","disiksa",
    "drama","provokasi","masalah","rusak","hina","bodoh","takut","ancam",
    "konflik","krisis","korban","sedih","tangis","kecewa","mossad","cuan"
}

NEGATION_WORDS = {"tidak", "tdk", "tak", "bukan", "jangan", "ga", "gak", "nggak"}

def score_sentiment(text):
    clean = clean_text(text)
    tokens = clean.split()
    score = 0
    pos_hits = []
    neg_hits = []

    for i, token in enumerate(tokens):
        multiplier = 1
        if i > 0 and tokens[i-1] in NEGATION_WORDS:
            multiplier = -1

        if token in POSITIVE_WORDS:
            score += 1 * multiplier
            pos_hits.append(token)
        elif token in NEGATIVE_WORDS:
            score -= 1 * multiplier
            neg_hits.append(token)

    if score > 0:
        label = "Positif"
    elif score < 0:
        label = "Negatif"
    else:
        label = "Netral"

    return label, score, ", ".join(pos_hits), ", ".join(neg_hits)

def add_sentiment_columns(df, text_col="Content"):
    results = df[text_col].fillna("").apply(score_sentiment)
    df = df.copy()
    df["Sentiment"] = results.apply(lambda x: x[0])
    df["SentimentScore"] = results.apply(lambda x: x[1])
    df["PositiveHits"] = results.apply(lambda x: x[2])
    df["NegativeHits"] = results.apply(lambda x: x[3])
    return df
