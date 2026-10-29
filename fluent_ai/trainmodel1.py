import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

#FILE PATHs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(
    BASE_DIR, "data", "writing_assessment_dataset.csv"
)
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")
MODEL_PATH = os.path.join(
    MODEL_DIR, "writing_level_model.pkl"
)
os.makedirs(MODEL_DIR, exist_ok=True)

#LOAD DATASET
if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}\n"
        "Place writing_assessment_dataset.csv inside the data folder."
    )
df = pd.read_csv(DATASET_PATH)
required_columns = {"text", "label"}
if not required_columns.issubset(df.columns):
    raise ValueError(
        "Dataset must contain these columns: text and label."
    )
df = df[["text", "label"]].copy()
df["text"] = df["text"].fillna("").astype(str).str.strip()
df["label"] = df["label"].fillna("").astype(str).str.strip().str.upper()
df = df[
    (df["text"] != "") &
    (df["label"] != "")
].drop_duplicates(subset=["text", "label"])
if df.empty:
    raise ValueError("The dataset has no valid text and label rows.")

#CONVERT CEFR LABELS INTO FOUR CATEGORIES
CEFR_MAPPING = {
    "A1": "Needs Improvement",
    "A2": "Needs Improvement",
    "B1": "Developing",
    "B2": "Proficient",
    "C1": "Advanced",
    "C2": "Advanced",
}

# Also accept rows that already use the four categories.
CATEGORY_MAPPING = {
    "NEEDS IMPROVEMENT": "Needs Improvement",
    "DEVELOPING": "Developing",
    "PROFICIENT": "Proficient",
    "ADVANCED": "Advanced",
}
def convert_label(label):
    if label in CEFR_MAPPING:
        return CEFR_MAPPING[label]
    if label in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[label]
    return None
df["proficiency_label"] = df["label"].apply(convert_label)
df = df.dropna(subset=["proficiency_label"])
if df.empty:
    raise ValueError(
        "No supported labels found. Use A1, A2, B1, B2, C1, C2 "
        "or the four proficiency categories."
    )
print("\nDataset loaded successfully.")
print("Total usable samples:", len(df))
print("\nCategory distribution:")
print(df["proficiency_label"].value_counts())
#CHECK DATA SUITABILITY
category_counts = df["proficiency_label"].value_counts()
if len(category_counts) < 2:
    raise ValueError(
        "At least two different proficiency categories are required."
    )
if category_counts.min() < 2:
    raise ValueError(
        "Each category needs at least two samples for training. "
        "Add more examples for the category with too few samples."
    )
X = df["text"]
y = df["proficiency_label"]
# Stratified splitting requires at least two examples per class.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

#BUILD THE WRITING ASSESSMENT MODEL
model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=20000,
            sublinear_tf=True,
            strip_accents="unicode"
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42
        )
    )
])

#TRAIN MODEL
print("\nTraining writing assessment model...")
model.fit(X_train, y_train)

#EVALUATE MODEL
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("\n" + "=" * 50)
print("WRITING ASSESSMENT MODEL RESULTS")
print("=" * 50)
print(f"Test accuracy: {accuracy:.2%}")
print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)

#SAVE MODEL
model_data = {
    "model": model,
    "labels": [
        "Needs Improvement",
        "Developing",
        "Proficient",
        "Advanced"
    ],
    "label_mapping": CEFR_MAPPING,
    "model_type": "TF-IDF + Logistic Regression"
}
joblib.dump(model_data, MODEL_PATH)
print("\nModel saved successfully!")
print("Model path:", MODEL_PATH)

#TEST WITH SAMPLE SENTENCES
test_sentences = [
    "I am a student. I like apples.",
    "I usually study in the evening because it helps me concentrate.",
    "Although the task was challenging, I completed it successfully.",
    "Despite considerable uncertainty, the findings demonstrate "
    "the importance of a comprehensive evaluation."
]
print("\nSample predictions:")
for sentence in test_sentences:
    predicted_label = model.predict([sentence])[0]
    probabilities = model.predict_proba([sentence])[0]
    confidence = max(probabilities)
    print("\nSentence:", sentence)
    print("Predicted category:", predicted_label)
    print(f"Model confidence: {confidence:.2%}")
