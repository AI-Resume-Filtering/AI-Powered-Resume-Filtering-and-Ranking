import os
import logging
from datetime import datetime

try:
    import joblib
except ImportError:
    joblib = None

try:
    from sklearn.ensemble import RandomForestClassifier
except ImportError:
    RandomForestClassifier = None

logger = logging.getLogger(__name__)

MODEL_FILENAME = "model.pkl"
FEATURE_COLUMNS = ["semantic_score", "experience_score", "education_score"]


def _default_model_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_FILENAME)


def prepare_feedback_dataset(db):
    """
    Build (X, y) from feedback collection.
    Features: semantic_score, experience_score, education_score
    Label: selected (1/0)
    """
    docs = list(db["feedback"].find({}, {
        "_id": 0,
        "semantic_score": 1,
        "experience_score": 1,
        "education_score": 1,
        "selected": 1,
    }))

    X = []
    y = []

    for doc in docs:
        try:
            semantic = float(doc.get("semantic_score", 0.0))
            experience = float(doc.get("experience_score", 0.0))
            education = float(doc.get("education_score", 0.0))
            selected = doc.get("selected", False)

            if isinstance(selected, bool):
                label = 1 if selected else 0
            else:
                label = 1 if str(selected).strip().lower() in {"1", "true", "yes", "selected"} else 0

            X.append([semantic, experience, education])
            y.append(label)
        except (TypeError, ValueError):
            continue

    return X, y


def train_model_from_feedback(db, min_samples: int = 20, model_path: str = None):
    """
    Train RandomForest on feedback data and persist model to model.pkl.
    """
    if joblib is None or RandomForestClassifier is None:
        return {
            "success": False,
            "message": "Training dependencies missing (scikit-learn/joblib).",
            "modelPath": model_path or _default_model_path(),
        }

    X, y = prepare_feedback_dataset(db)
    if len(X) < min_samples:
        return {
            "success": False,
            "message": f"Not enough feedback samples. Need {min_samples}, found {len(X)}.",
            "modelPath": model_path or _default_model_path(),
        }

    if len(set(y)) < 2:
        return {
            "success": False,
            "message": "Need both selected and rejected samples to train classifier.",
            "modelPath": model_path or _default_model_path(),
        }

    clf = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    clf.fit(X, y)

    output_path = model_path or _default_model_path()
    bundle = {
        "model": clf,
        "trained_at": datetime.utcnow().isoformat(),
        "feature_columns": FEATURE_COLUMNS,
        "sample_count": len(X),
    }
    joblib.dump(bundle, output_path)

    return {
        "success": True,
        "message": "Model trained successfully.",
        "modelPath": output_path,
        "sampleCount": len(X),
    }


def maybe_retrain_model(db, retrain_threshold: int = 50, min_samples: int = 20, model_path: str = None):
    """
    Trigger retraining every N feedback rows.
    """
    count = db["feedback"].count_documents({})
    if count <= 0 or retrain_threshold <= 0:
        return {
            "triggered": False,
            "feedbackCount": count,
            "reason": "threshold-disabled-or-empty",
        }

    if count % retrain_threshold != 0:
        return {
            "triggered": False,
            "feedbackCount": count,
            "reason": "threshold-not-met",
        }

    result = train_model_from_feedback(db, min_samples=min_samples, model_path=model_path)
    result["triggered"] = True
    result["feedbackCount"] = count
    return result
