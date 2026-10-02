import datetime
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Lock the database path permanently to the directory where this file resides (backend/)
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "grievances.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(String, unique=True, index=True)
    citizen_name = Column(String, default="Anonymous")
    citizen_phone = Column(String, default="")
    description = Column(String, nullable=False)
    location = Column(String, default="Unspecified")
    
    # AI Predictions
    predicted_department = Column(String)
    confidence_score = Column(Float)
    priority_level = Column(String)
    needs_human_triage = Column(Boolean, default=False)
    
    # Novelty Feature: Semantic Duplicate Linkage
    is_duplicate = Column(Boolean, default=False)
    parent_ticket_id = Column(String, nullable=True)
    similarity_score = Column(Float, default=0.0)
    
    # Workflow status: "Pending", "In Progress", "Resolved", "Duplicate Linked", "Officially Closed", etc.
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)