import uuid
import datetime
from database import SessionLocal, Complaint

sample_tickets = [
    {
        "citizen_name": "Aman Verma",
        "citizen_phone": "9811223344",
        "description": "High voltage wire snapped and hanging close to pavement near school gate",
        "location": "Ward 12 - North Crossing",
        "predicted_department": "Electricity",
        "confidence_score": 0.94,
        "priority_level": "P1",
        "needs_human_triage": False,
        "is_duplicate": False,
        "parent_ticket_id": None,
        "similarity_score": 0.0,
        "status": "In Progress"
    },
    {
        "citizen_name": "Sunita Rao",
        "citizen_phone": "9871122445",
        "description": "Garbage dump overflowing outside community park, strong foul smell",
        "location": "Ward 15 - Industrial Sector",
        "predicted_department": "Sanitation",
        "confidence_score": 0.88,
        "priority_level": "P3",
        "needs_human_triage": False,
        "is_duplicate": False,
        "parent_ticket_id": None,
        "similarity_score": 0.0,
        "status": "Pending"
    },
    {
        "citizen_name": "Deepak Mehta",
        "citizen_phone": "9910023456",
        "description": "Deep pothole on main road causing severe traffic jam and bike skidding",
        "location": "Ward 22 - Green Park",
        "predicted_department": "Roads & Infrastructure",
        "confidence_score": 0.85,
        "priority_level": "P2",
        "needs_human_triage": False,
        "is_duplicate": False,
        "parent_ticket_id": None,
        "similarity_score": 0.0,
        "status": "In Progress"
    },
    {
        "citizen_name": "Pooja Nair",
        "citizen_phone": "9818833441",
        "description": "Street lights not functioning in alleyway 5 for over a week",
        "location": "Ward 10 - Central",
        "predicted_department": "Electricity",
        "confidence_score": 0.91,
        "priority_level": "P3",
        "needs_human_triage": False,
        "is_duplicate": False,
        "parent_ticket_id": None,
        "similarity_score": 0.0,
        "status": "Resolved"
    },
    {
        "citizen_name": "Karan Singh",
        "citizen_phone": "9899112233",
        "description": "Sewage drain completely clogged and dirty water entering residential lane",
        "location": "Ward 15 - Industrial Sector",
        "predicted_department": "Sanitation",
        "confidence_score": 0.89,
        "priority_level": "P2",
        "needs_human_triage": False,
        "is_duplicate": False,
        "parent_ticket_id": None,
        "similarity_score": 0.0,
        "status": "Resolved"
    },
    {
        "citizen_name": "Ritu Kapoor",
        "citizen_phone": "9711223399",
        "description": "General query about municipal property tax rebate schemes",
        "location": "Ward 10 - Central",
        "predicted_department": "General Administration",
        "confidence_score": 0.22,
        "priority_level": "P4",
        "needs_human_triage": True,
        "is_duplicate": False,
        "parent_ticket_id": None,
        "similarity_score": 0.0,
        "status": "Pending"
    }
]

def seed():
    db = SessionLocal()
    count = 0
    for item in sample_tickets:
        ticket = Complaint(
            tracking_id=f"GRV-{uuid.uuid4().hex[:6].upper()}",
            created_at=datetime.datetime.utcnow(),
            **item
        )
        db.add(ticket)
        count += 1
    db.commit()
    db.close()
    print(f"Successfully inserted {count} realistic municipal complaints!")

if __name__ == "__main__":
    seed()