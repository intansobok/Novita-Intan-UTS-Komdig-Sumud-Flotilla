"""Sentiment analysis module for Indonesian social-media comments.

The preferred method uses a Hugging Face Transformers model that is suitable for
Bahasa Indonesia. The app defaults to an Indonesian RoBERTa sentiment model
because it is practical for three-class public-comment sentiment analysis.
Users may replace the model name with an IndoBERT fine-tuned sentiment model
through the Streamlit sidebar or environment variable.
"""

from __future__ import annotations

import os
from typing import Iterable, List, Tuple

import pandas as pd

from src.sentiment import score_sentiment

DEFAULT_TRANSFORMER_MODEL = os.getenv(
    "SENTIMENT_MODEL_NAME",
    "w11wo/indonesian-roberta-base-sentiment-classifier",
)

LABEL_MAP = {
    # Common English labels
    "positive": "Positif",
    "pos": "Positif",
    "neutral": "Netral",
    "neu": "Netral",
    "negative": "Negatif",
    "neg": "Negatif",
    # Common Indonesian labels
    "positif": "Positif",
    "netral": "Netral",
    "negatif": "Negatif",
    # Common numeric label order used by many sentiment checkpoints.
    # If a selected model uses a different mapping, change the model or mapping.
    "label_0": "Negatif",
    "label_1": "Netral",
    "label_2": "Positif",
    "0": "Negatif",
    "1": "Netral",
    "2": "Positif",
}


def normalize_label(raw_label: str) -> str:
    """Normalize model labels into Positif, Netral, or Negatif."""
    key = str(raw_label).strip().lower().replace(" ", "_")
    return LABEL_MAP.get(key, raw_label.title() if raw_label else "Netral")


def get_transformer_pipeline(model_name: str = DEFAULT_TRANSFORMER_MODEL):
    """Load a Transformers sentiment-analysis pipeline.

    This import is intentionally inside the function so the project can still
    run in lightweight/offline environments using the lexicon fallback.
    """
    from transformers import pipeline

    return pipeline(
        task="sentiment-analysis",
        model=model_name,
        tokenizer=model_name,
        truncation=True,
        max_length=256,
    )


def predict_transformer(
    texts: Iterable[str],
    model_name: str = DEFAULT_TRANSFORMER_MODEL,
    batch_size: int = 16,
) -> Tuple[List[str], List[float], str]:
    """Predict sentiment labels and confidence scores using Transformers."""
    pipe = get_transformer_pipeline(model_name)
    clean_texts = [str(t) if pd.notna(t) else "" for t in texts]
    results = pipe(clean_texts, batch_size=batch_size)

    labels = [normalize_label(item.get("label", "Netral")) for item in results]
    scores = [round(float(item.get("score", 0.0)), 4) for item in results]
    return labels, scores, model_name


def add_indobert_sentiment_columns(
    df: pd.DataFrame,
    text_col: str = "Content",
    model_name: str = DEFAULT_TRANSFORMER_MODEL,
    batch_size: int = 16,
    fallback_to_lexicon: bool = True,
) -> Tuple[pd.DataFrame, str, str | None]:
    """Add three-class sentiment columns to every comment.

    Returns:
        dataframe, method_used, warning_message
    """
    out = df.copy()
    texts = out[text_col].fillna("").astype(str).tolist()

    try:
        labels, confidence, used_model = predict_transformer(
            texts=texts,
            model_name=model_name,
            batch_size=batch_size,
        )
        out["Sentiment"] = labels
        out["SentimentConfidence"] = confidence
        out["SentimentMethod"] = f"Transformers: {used_model}"
        # Keep numeric score for compatibility with older charts/table.
        score_map = {"Positif": 1, "Netral": 0, "Negatif": -1}
        out["SentimentScore"] = out["Sentiment"].map(score_map).fillna(0)
        return out, f"Transformers: {used_model}", None
    except Exception as exc:  # pragma: no cover - depends on runtime model availability
        if not fallback_to_lexicon:
            raise

        lexicon_results = out[text_col].fillna("").apply(score_sentiment)
        out["Sentiment"] = lexicon_results.apply(lambda x: x[0])
        out["SentimentScore"] = lexicon_results.apply(lambda x: x[1])
        out["SentimentConfidence"] = None
        out["SentimentMethod"] = "Fallback lexicon Bahasa Indonesia"
        warning = (
            "Model Transformers/IndoBERT tidak dapat dimuat pada lingkungan ini, "
            "sehingga dashboard memakai fallback lexicon. Detail teknis: " + str(exc)
        )
        return out, "Fallback lexicon Bahasa Indonesia", warning
