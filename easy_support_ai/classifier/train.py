"""Treinamento do classificador de urgência usando scikit-learn."""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

DATA_PATH = Path("data/tickets_treino.csv")
MODEL_PATH = Path("classifier/urgency_model.joblib")
RANDOM_STATE = 42


def train_model() -> tuple[Pipeline, float, float]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Arquivo de treino não encontrado em {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["texto", "urgencia"]).drop_duplicates()

    X_train, X_test, y_train, y_test = train_test_split(
        df["texto"],
        df["urgencia"],
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=df["urgencia"],
    )

    # 1. Baseline simples com classe mais frequente
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X_train.to_frame(), y_train)
    baseline_pred = baseline.predict(X_test.to_frame())
    baseline_f1 = f1_score(y_test, baseline_pred, average="macro")

    # 2. Pipeline do modelo real
    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                min_df=2,
                max_features=5000,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            ),
        ),
    ])

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    model_f1 = f1_score(y_test, predictions, average="macro")

    print("==========================================")
    print("RELATÓRIO DE TREINAMENTO DO CLASSIFICADOR")
    print("==========================================")
    print("F1 macro do baseline:", round(baseline_f1, 3))
    print("F1 macro do modelo:  ", round(model_f1, 3))
    print("
Detalhamento por classe:")
    print(classification_report(y_test, predictions, zero_division=0))

    if model_f1 <= baseline_f1:
        raise RuntimeError("O modelo treinado não superou o baseline obrigatório.")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Modelo salvo com sucesso em: {MODEL_PATH}")

    return pipeline, baseline_f1, model_f1


if __name__ == "__main__":
    train_model()
