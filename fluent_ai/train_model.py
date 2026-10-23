
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = (
    BASE_DIR / "data" / "Fluent AI MCQ Dataset - Responses.csv"
)

MODEL_DIR = BASE_DIR / "ml_models"
MODEL_PATH = MODEL_DIR / "mcq_level_model.pkl"

# Use percentages, not raw counts that change with test length.
FEATURES = [
    "TotalPercentage",
    "GrammarPercentage",
    "VocabularyPercentage",
    "ConversationPercentage",
]

TARGET = "ProficiencyLabel"

LABELS = [
    "Needs Improvement",
    "Developing",
    "Proficient",
    "Advanced",
]


def build_model():
    return Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="median"),
        ),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=5,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ])


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required = FEATURES + [TARGET]
    missing = [
        column for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df = df[required].copy()

    for column in FEATURES:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df[TARGET] = (
        df[TARGET]
        .astype("string")
        .str.strip()
    )

    df = df.dropna(
        subset=FEATURES + [TARGET]
    )

    df = df[df[TARGET].isin(LABELS)]

    if df.empty:
        raise ValueError("No valid labelled records found.")

    class_counts = df[TARGET].value_counts()

    print("\nDataset size:", len(df))
    print("\nClass distribution:")
    print(class_counts.to_string())

    if len(class_counts) != 4 or class_counts.min() < 2:
        raise ValueError(
            "All four labels need at least two real examples."
        )

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    # First, evaluate on records excluded from training.
    evaluation_model = build_model()
    evaluation_model.fit(X_train, y_train)

    predictions = evaluation_model.predict(X_test)

    print("\nHeld-out test accuracy:",
          f"{accuracy_score(y_test, predictions):.2%}")

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=LABELS,
            zero_division=0,
        )
    )

    # Then train the deployed model on all available records.
    final_model = build_model()
    final_model.fit(X, y)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "model": final_model,
            "features": FEATURES,
            "labels": LABELS,
            "model_type": "Percentage-based Random Forest",
        },
        MODEL_PATH,
    )

    print("\nFinal model trained on all records.")
    print("Saved to:", MODEL_PATH)


if __name__ == "__main__":
    main()
