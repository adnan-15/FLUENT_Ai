from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "X_y_train.csv"
)

MODEL_DIR = (
    BASE_DIR
    / "ml_models"
)

MODEL_DIR.mkdir(
    exist_ok=True
)

MODEL_PATH = (
    MODEL_DIR
    / "cefr_model.pkl"
)


print("Loading dataset...")

df = pd.read_csv(
    DATA_PATH
)

print(
    f"Dataset shape: {df.shape}"
)


# -------------------------
# FIND TEXT COLUMN
# -------------------------

text_candidates = [
    "text",
    "Text",
    "sentence",
    "Sentence",
    "utterance",
    "Utterance",
    "X",
    "content",
    "essay",
]

text_column = None

for column in text_candidates:

    if column in df.columns:

        text_column = column
        break


if text_column is None:

    object_columns = (
        df
        .select_dtypes(
            include=["object"]
        )
        .columns
        .tolist()
    )

    if not object_columns:

        raise ValueError(
            "No text column found."
        )

    text_column = object_columns[0]


# -------------------------
# FIND LABEL COLUMN
# -------------------------

label_candidates = [
    "label",
    "Label",
    "y",
    "Y",
    "level",
    "Level",
    "cefr",
    "CEFR",
    "cefr_level",
]

label_column = None

for column in label_candidates:

    if column in df.columns:

        label_column = column
        break


if label_column is None:

    remaining = [
        column
        for column in df.columns
        if column != text_column
    ]

    if not remaining:

        raise ValueError(
            "No label column found."
        )

    label_column = remaining[-1]


print(
    f"Text column: {text_column}"
)

print(
    f"Label column: {label_column}"
)


# -------------------------
# CLEAN DATA
# -------------------------

df = df[
    [
        text_column,
        label_column
    ]
].dropna()


df[text_column] = (
    df[text_column]
    .astype(str)
    .str.strip()
)


df = df[
    df[text_column].str.len() > 10
]


X = df[text_column]

y = df[label_column]


# -------------------------
# CEFR LABEL MAPPING
# -------------------------

numeric_mapping = {
    0: "A1",
    1: "A2",
    2: "B1",
    3: "B2",
    4: "C1",
}


if pd.api.types.is_numeric_dtype(y):

    y = y.map(
        numeric_mapping
    )

else:

    y = (
        y
        .astype(str)
        .str.upper()
        .str.strip()
    )


valid_levels = [
    "A1",
    "A2",
    "B1",
    "B2",
    "C1",
]


mask = y.isin(
    valid_levels
)

X = X[mask]

y = y[mask]


print("\nCEFR distribution:")

print(
    y.value_counts()
)


# -------------------------
# TRAIN / TEST SPLIT
# -------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# -------------------------
# MODEL
# -------------------------

model = Pipeline(
    [
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                sublinear_tf=True,
                max_features=80000,
            )
        ),

        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            )
        ),
    ]
)


print("\nTraining model...")

model.fit(
    X_train,
    y_train
)


# -------------------------
# EVALUATION
# -------------------------

predictions = model.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    predictions
)


print(
    f"\nAccuracy: {accuracy:.4f}"
)

print(
    "\nClassification Report:"
)

print(
    classification_report(
        y_test,
        predictions
    )
)


# -------------------------
# SAVE PICKLE
# -------------------------

joblib.dump(
    model,
    MODEL_PATH
)


print(
    "\n--------------------------------"
)

print(
    "MODEL CREATED SUCCESSFULLY"
)

print(
    f"Saved at: {MODEL_PATH}"
)

print(
    "--------------------------------"
)