import re
from collections import Counter
import pandas as pd

STOPWORDS_ID = {
    "yang","dan","di","ke","dari","ini","itu","untuk","dengan","pada","ada","karena",
    "dalam","jadi","atau","juga","saya","aku","kita","kami","mereka","dia","nya",
    "lah","pun","sih","dong","kok","ya","ga","gak","nggak","tidak","tdk","bukan",
    "akan","sudah","belum","bisa","harus","sebagai","oleh","para","lebih","lagi",
    "kalau","kalo","apa","aja","saja","semua","orang","masa","dgn","yg","dmn",
    "the","a","an","of","to","in","is","are","and","or"
}

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+|#\w+", " ", text)
    text = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_static_data(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    required_cols = [
        "Id","UserId","Avatar","Author","Content","Url","ReactionsCount",
        "Depth","SubCommentsCount","CommentAt","Platform"
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
    df["Content"] = df["Content"].fillna("").astype(str)
    df["clean_content"] = df["Content"].apply(clean_text)
    df["word_count"] = df["clean_content"].apply(lambda x: len(x.split()) if x else 0)
    df["ReactionsCount"] = pd.to_numeric(df["ReactionsCount"], errors="coerce").fillna(0).astype(int)
    df["Depth"] = pd.to_numeric(df["Depth"], errors="coerce").fillna(0).astype(int)
    df["SubCommentsCount"] = pd.to_numeric(df["SubCommentsCount"], errors="coerce").fillna(0).astype(int)
    df["CommentAt_parsed"] = pd.to_datetime(df["CommentAt"], errors="coerce")
    return df

def get_top_words(text_series, top_n=20):
    words = []
    for text in text_series.dropna():
        for word in str(text).split():
            if len(word) > 2 and word not in STOPWORDS_ID:
                words.append(word)
    counts = Counter(words).most_common(top_n)
    return pd.DataFrame(counts, columns=["word", "count"])
