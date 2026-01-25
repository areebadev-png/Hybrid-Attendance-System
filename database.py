from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone
from config import Config

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    barcode_id = Column(String(50), unique=True, nullable=False, index=True)
    face_encoding_path = Column(String(255))  # Path to stored face encoding
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    user_name = Column(String(100), nullable=False)
    user_email = Column(String(100), nullable=False)
    barcode_id = Column(String(50), nullable=False)
    attendance_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    face_match_confidence = Column(Float)
    verification_method = Column(String(20), default="dual")  # dual, face_only, barcode_only
    status = Column(String(20), default="present")  # present, absent, late
    notes = Column(Text)

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    attendance_id = Column(Integer, nullable=False)
    log_type = Column(String(50))  # face_recognition, barcode_scan, verification_failed, etc.
    log_message = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Database setup
engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
