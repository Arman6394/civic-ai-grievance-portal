import joblib
import numpy as np

dept_model = joblib.load("dept_classifier.joblib")
priority_model = joblib.load("priority_classifier.joblib")

CRITICAL_KEYWORDS = ["fire", "sparks", "burst", "accident", "missing manhole", "chemical", "live wire"]

def process_grievance(text: str):
    # Predict Department & Confidence
    dept_probs = dept_model.predict_proba([text])[0]
    best_idx = np.argmax(dept_probs)
    dept_name = str(dept_model.classes_[best_idx])
    confidence = float(dept_probs[best_idx])
    
    # Predict Priority
    priority = str(priority_model.predict([text])[0])
    
    # Heuristic override for high-risk hazards
    is_critical = any(kw in text.lower() for kw in CRITICAL_KEYWORDS)
    if is_critical:
        priority = "P1"

    # Require triage only when model has very low confidence (e.g. out-of-domain text)
    needs_triage = confidence < 0.28

    return {
        "predicted_department": dept_name,
        "confidence_score": round(confidence, 2),
        "priority_level": priority,
        "needs_human_triage": needs_triage,
        "routing_status": "Human Triage Required" if needs_triage else f"Routed to {dept_name}"
    }

if __name__ == "__main__":
    test_cases = [
        "Live wire is hanging loose after the rain and sparking!",
        "Main pipeline burst and clean drinking water is leaking everywhere",
        "Garbage pile is rotting near community park gate",
        "Something weird happened yesterday, please check"
    ]
    for case in test_cases:
        print(f"\nQuery: {case}")
        print(process_grievance(case))