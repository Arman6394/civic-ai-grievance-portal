import os
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer, util # type: ignore

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEPT_MODEL_PATH = os.path.join(CURRENT_DIR, "dept_classifier.joblib")
PRIORITY_MODEL_PATH = os.path.join(CURRENT_DIR, "priority_classifier.joblib")

dept_model = joblib.load(DEPT_MODEL_PATH)
priority_model = joblib.load(PRIORITY_MODEL_PATH)

# Load lightweight sentence transformer for semantic matching
embedder = SentenceTransformer("all-MiniLM-L6-v2")

CRITICAL_KEYWORDS = ["fire", "sparks", "burst", "accident", "missing manhole", "chemical", "live wire"]

def process_grievance(text: str):
    dept_probs = dept_model.predict_proba([text])[0]
    best_idx = np.argmax(dept_probs)
    dept_name = str(dept_model.classes_[best_idx])
    confidence = float(dept_probs[best_idx])
    
    priority = str(priority_model.predict([text])[0])
    if any(kw in text.lower() for kw in CRITICAL_KEYWORDS):
        priority = "P1"

    needs_triage = confidence < 0.25

    return {
        "predicted_department": dept_name,
        "confidence_score": round(confidence, 2),
        "priority_level": priority,
        "needs_human_triage": needs_triage,
        "routing_status": "Human Triage Required" if needs_triage else f"Routed to {dept_name}"
    }

def check_duplicate(new_text: str, existing_complaints: list, threshold: float = 0.58):
    """
    Compares new complaint text against existing open complaints in the same locality.
    Threshold calibrated to 0.58 for civic grievance paraphrasing.
    Uses batch tensor encoding for faster inference.
    """
    if not existing_complaints:
        return {"is_duplicate": False, "parent_id": None, "similarity": 0.0}

    # Extract clean descriptions (stripping base64 image strings if present)
    descriptions = []
    for item in existing_complaints:
        desc = item["description"]
        if "[ATTACHED_IMAGE_BASE64:" in desc:
            desc = desc.split("[ATTACHED_IMAGE_BASE64:")[0].strip()
        descriptions.append(desc)

    # Encode new input and all candidate existing complaints in batched tensors
    new_embedding = embedder.encode(new_text, convert_to_tensor=True)
    existing_embeddings = embedder.encode(descriptions, convert_to_tensor=True)

    # Compute cosine similarities simultaneously across the tensor
    cosine_scores = util.cos_sim(new_embedding, existing_embeddings)[0]

    best_idx = int(np.argmax(cosine_scores.cpu().numpy()))
    highest_score = float(cosine_scores[best_idx].item())
    best_match_id = existing_complaints[best_idx]["tracking_id"]

    print(f"[DUPLICATE CHECK] Top match: {best_match_id} | Highest Score: {highest_score:.2f}")

    if highest_score >= threshold:
        return {
            "is_duplicate": True,
            "parent_id": best_match_id,
            "similarity": round(highest_score, 2)
        }
            
    return {"is_duplicate": False, "parent_id": None, "similarity": round(highest_score, 2)}