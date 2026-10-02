import sys
import uuid
from pathlib import Path
from difflib import SequenceMatcher
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Add ai_engine to path
AI_ENGINE_PATH = Path(__file__).resolve().parent.parent / "ai_engine"
sys.path.append(str(AI_ENGINE_PATH))

from service import process_grievance, embedder, util
from backend.database import SessionLocal, Complaint

app = FastAPI(title="AI Grievance Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ComplaintCreate(BaseModel):
    citizen_name: str = "Anonymous"
    citizen_phone: str = ""
    description: str
    location: str = "Local Ward"

class StatusUpdate(BaseModel):
    status: str

def compute_similarity(text1: str, text2: str) -> float:
    """Computes semantic embedding similarity, falls back to sequence matcher."""
    try:
        e1 = embedder.encode(text1, convert_to_tensor=True)
        e2 = embedder.encode(text2, convert_to_tensor=True)
        score = float(util.cos_sim(e1, e2).item())
        return score
    except Exception:
        # Fallback heuristic
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

@app.post("/api/complaints")
def submit_complaint(data: ComplaintCreate, db: Session = Depends(get_db)):
    if not data.description.strip():
        raise HTTPException(status_code=400, detail="Description cannot be empty")
    
    # 1. Fetch open complaints in the SAME locality
    existing_records = db.query(Complaint).filter(
        Complaint.location == data.location,
        Complaint.status != "Resolved"
    ).all()
    
    is_duplicate = False
    parent_id = None
    best_similarity = 0.0

    # 2. Check for duplicate using semantic embedding similarity
    for item in existing_records:
        sim = compute_similarity(data.description, item.description)
        print(f"[DEBUG SIMILARITY] Comparing with {item.tracking_id} | Score: {sim:.2f}")
        
        if sim > best_similarity:
            best_similarity = sim
            # If similarity is >= 45%, mark as duplicate
            if sim >= 0.45:
                is_duplicate = True
                parent_id = item.tracking_id

    # 3. Run AI Classification Engine
    ai_result = process_grievance(data.description)
    
    tracking_code = f"GRV-{uuid.uuid4().hex[:6].upper()}"
    assigned_status = "Duplicate Linked" if is_duplicate else "Pending"

    new_ticket = Complaint(
        tracking_id=tracking_code,
        citizen_name=data.citizen_name,
        citizen_phone=data.citizen_phone,
        description=data.description,
        location=data.location,
        predicted_department=ai_result["predicted_department"],
        confidence_score=ai_result["confidence_score"],
        priority_level=ai_result["priority_level"],
        needs_human_triage=ai_result["needs_human_triage"],
        is_duplicate=is_duplicate,
        parent_ticket_id=parent_id,
        similarity_score=round(best_similarity, 2),
        status=assigned_status
    )
    
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    return {
        "message": "Grievance registered",
        "tracking_id": new_ticket.tracking_id,
        "ai_analysis": ai_result,
        "duplicate_detection": {
            "is_duplicate": bool(is_duplicate),
            "parent_id": str(parent_id) if parent_id else None,
            "similarity": float(round(best_similarity, 2))
        }
    }

@app.get("/api/complaints/track/{tracking_id}")
def track_complaint(tracking_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Complaint).filter(Complaint.tracking_id == tracking_id.upper()).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return ticket

@app.get("/api/officer/complaints")
def list_complaints(db: Session = Depends(get_db)):
    return db.query(Complaint).order_by(Complaint.created_at.desc()).all()

@app.patch("/api/officer/complaints/{tracking_id}/status")
def update_status(tracking_id: str, payload: StatusUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Complaint).filter(Complaint.tracking_id == tracking_id.upper()).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    ticket.status = payload.status
    db.commit()
    db.refresh(ticket)
    return {"message": "Status updated successfully", "ticket": ticket}