from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, cast, Date
from datetime import datetime, date, timedelta, timezone
from contextlib import asynccontextmanager
import os
import shutil
import cv2
import uuid
from typing import Optional, List
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from ..database import get_db, init_db, User, Attendance, AttendanceLog
from face_recognition_service import FaceRecognitionService
from barcode_service import BarcodeService
from config import Config

# Initialize services
face_service = None
barcode_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global face_service, barcode_service
    init_db()
    # Create uploads directory
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs("face_encodings", exist_ok=True)
    face_service = FaceRecognitionService()
    barcode_service = BarcodeService()
    yield
    # Shutdown (if needed)
    pass

# Initialize FastAPI app
app = FastAPI(
    title="Hybrid Attendance Management System", 
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== User Management ====================

@app.post("/api/users/register")
async def register_user(
    name: str = Form(...),
    email: str = Form(...),
    barcode_id: str = Form(...),
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Register a new user with face image and barcode ID"""
    if face_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            or_(User.email == email, User.barcode_id == barcode_id)
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email or barcode ID already exists")
        
        # Save uploaded image
        file_extension = face_image.filename.split('.')[-1]
        if file_extension not in Config.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file format")
        
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(face_image.file, buffer)
        
        # Extract face encoding
        face_encoding = face_service.extract_face_encoding(file_path)
        if face_encoding is None:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Could not detect face in image")
        
        # Create user
        new_user = User(
            name=name,
            email=email,
            barcode_id=barcode_id,
            face_encoding_path=None  # Will be set after saving encoding
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Save face encoding
        encoding_path = face_service.save_face_encoding(new_user.id, face_encoding)
        new_user.face_encoding_path = encoding_path
        db.commit()
        
        return {
            "message": "User registered successfully",
            "user_id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "barcode_id": new_user.barcode_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.get("/api/users")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all registered users"""
    users = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    return {
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "barcode_id": user.barcode_id,
                "created_at": user.created_at.isoformat()
            }
            for user in users
        ],
        "total": db.query(User).filter(User.is_active == True).count()
    }

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    return {"message": "User deleted successfully"}

# ==================== Attendance Marking ====================

@app.post("/api/attendance/mark")
async def mark_attendance(
    face_image: UploadFile = File(...),
    barcode_data: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Mark attendance using face recognition and barcode verification"""
    if face_service is None or barcode_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        # Save uploaded image
        file_extension = face_image.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(face_image.file, buffer)
        
        # Extract face encoding
        face_encoding = face_service.extract_face_encoding(file_path)
        if face_encoding is None:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Could not detect face in image")
        
        # Find matching user by face
        matched_user, face_confidence = face_service.find_matching_user(face_encoding, db, User)
        
        if matched_user is None:
            os.remove(file_path)
            raise HTTPException(status_code=404, detail="Face not recognized")
        
        # Verify barcode if provided
        barcode_verified = False
        if barcode_data:
            barcode_verified = barcode_service.verify_barcode(barcode_data, matched_user.barcode_id)
            if not barcode_verified:
                os.remove(file_path)
                raise HTTPException(status_code=400, detail="Barcode verification failed")
        else:
            # Try to decode barcode from image
            barcode_data, _ = barcode_service.decode_barcode_from_image(file_path)
            if barcode_data:
                barcode_verified = barcode_service.verify_barcode(barcode_data, matched_user.barcode_id)
        
        # Check if attendance already marked today
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        existing_attendance = db.query(Attendance).filter(
            and_(
                Attendance.user_id == matched_user.id,
                Attendance.attendance_date >= today_start
            )
        ).first()
        
        if existing_attendance:
            os.remove(file_path)
            return {
                "message": "Attendance already marked today",
                "attendance": {
                    "id": existing_attendance.id,
                    "user_name": existing_attendance.user_name,
                    "attendance_date": existing_attendance.attendance_date.isoformat()
                }
            }
        
        # Mark attendance
        attendance = Attendance(
            user_id=matched_user.id,
            user_name=matched_user.name,
            user_email=matched_user.email,
            barcode_id=matched_user.barcode_id,
            face_match_confidence=face_confidence,
            verification_method="dual" if barcode_verified else "face_only",
            status="present"
        )
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        
        # Log attendance
        log = AttendanceLog(
            attendance_id=attendance.id,
            log_type="attendance_marked",
            log_message=f"Attendance marked for {matched_user.name} with face confidence {face_confidence:.2f}"
        )
        db.add(log)
        db.commit()
        
        # Clean up
        os.remove(file_path)
        
        return {
            "message": "Attendance marked successfully",
            "attendance": {
                "id": attendance.id,
                "user_name": attendance.user_name,
                "user_email": attendance.user_email,
                "attendance_date": attendance.attendance_date.isoformat(),
                "face_match_confidence": face_confidence,
                "verification_method": attendance.verification_method
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attendance marking failed: {str(e)}")

@app.post("/api/attendance/mark-with-barcode")
async def mark_attendance_with_barcode(
    barcode_data: str = Form(...),
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Mark attendance with barcode scan and face verification"""
    if face_service is None or barcode_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        # Find user by barcode
        user = db.query(User).filter(User.barcode_id == barcode_data).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found with this barcode ID")
        
        # Save uploaded image
        file_extension = face_image.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(face_image.file, buffer)
        
        # Verify face
        face_match, face_confidence = face_service.verify_face(file_path, user.face_encoding_path)
        
        if not face_match:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Face verification failed. Confidence: {face_confidence:.2f}")
        
        # Check if attendance already marked today
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        existing_attendance = db.query(Attendance).filter(
            and_(
                Attendance.user_id == user.id,
                Attendance.attendance_date >= today_start
            )
        ).first()
        
        if existing_attendance:
            os.remove(file_path)
            return {
                "message": "Attendance already marked today",
                "attendance": {
                    "id": existing_attendance.id,
                    "user_name": existing_attendance.user_name,
                    "attendance_date": existing_attendance.attendance_date.isoformat()
                }
            }
        
        # Mark attendance
        attendance = Attendance(
            user_id=user.id,
            user_name=user.name,
            user_email=user.email,
            barcode_id=user.barcode_id,
            face_match_confidence=face_confidence,
            verification_method="dual",
            status="present"
        )
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        
        # Clean up
        os.remove(file_path)
        
        return {
            "message": "Attendance marked successfully",
            "attendance": {
                "id": attendance.id,
                "user_name": attendance.user_name,
                "attendance_date": attendance.attendance_date.isoformat(),
                "face_match_confidence": face_confidence
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attendance marking failed: {str(e)}")

# ==================== Attendance Reports ====================

@app.get("/api/attendance")
async def get_attendance(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get attendance records with filters"""
    query = db.query(Attendance)
    
    if start_date:
        query = query.filter(Attendance.attendance_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Attendance.attendance_date <= datetime.fromisoformat(end_date))
    if user_id:
        query = query.filter(Attendance.user_id == user_id)
    
    total = query.count()
    attendances = query.order_by(Attendance.attendance_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "attendances": [
            {
                "id": att.id,
                "user_id": att.user_id,
                "user_name": att.user_name,
                "user_email": att.user_email,
                "barcode_id": att.barcode_id,
                "attendance_date": att.attendance_date.isoformat(),
                "face_match_confidence": att.face_match_confidence,
                "verification_method": att.verification_method,
                "status": att.status
            }
            for att in attendances
        ],
        "total": total
    }

@app.get("/api/attendance/stats")
async def get_attendance_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get attendance statistics"""
    query = db.query(Attendance)
    
    if start_date:
        query = query.filter(Attendance.attendance_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Attendance.attendance_date <= datetime.fromisoformat(end_date))
    
    total_records = query.count()
    total_users = db.query(User).filter(User.is_active == True).count()
    
    # Daily attendance count (SQLite compatible)
    daily_stats = db.query(
        cast(Attendance.attendance_date, Date).label('date'),
        func.count(Attendance.id).label('count')
    ).group_by(cast(Attendance.attendance_date, Date)).all()
    
    return {
        "total_records": total_records,
        "total_users": total_users,
        "daily_stats": [
            {"date": str(stat.date), "count": stat.count}
            for stat in daily_stats
        ]
    }

@app.get("/api/attendance/export/csv")
async def export_attendance_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export attendance records to CSV"""
    query = db.query(Attendance)
    
    if start_date:
        query = query.filter(Attendance.attendance_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Attendance.attendance_date <= datetime.fromisoformat(end_date))
    
    attendances = query.all()
    
    data = []
    for att in attendances:
        data.append({
            "ID": att.id,
            "User Name": att.user_name,
            "Email": att.user_email,
            "Barcode ID": att.barcode_id,
            "Date": att.attendance_date.strftime("%Y-%m-%d"),
            "Time": att.attendance_date.strftime("%H:%M:%S"),
            "Face Confidence": att.face_match_confidence,
            "Verification Method": att.verification_method,
            "Status": att.status
        })
    
    df = pd.DataFrame(data)
    csv_path = "attendance_export.csv"
    df.to_csv(csv_path, index=False)
    
    return FileResponse(csv_path, media_type="text/csv", filename="attendance_report.csv")

@app.get("/api/attendance/export/pdf")
async def export_attendance_pdf(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export attendance records to PDF"""
    query = db.query(Attendance)
    
    if start_date:
        query = query.filter(Attendance.attendance_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Attendance.attendance_date <= datetime.fromisoformat(end_date))
    
    attendances = query.order_by(Attendance.attendance_date.desc()).limit(100).all()
    
    pdf_path = "attendance_report.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("Attendance Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Table data
    data = [["Name", "Email", "Date", "Time", "Status", "Confidence"]]
    for att in attendances:
        data.append([
            att.user_name,
            att.user_email,
            att.attendance_date.strftime("%Y-%m-%d"),
            att.attendance_date.strftime("%H:%M:%S"),
            att.status,
            f"{att.face_match_confidence:.2f}" if att.face_match_confidence else "N/A"
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return FileResponse(pdf_path, media_type="application/pdf", filename="attendance_report.pdf")

# ==================== Health Check ====================

@app.get("/")
async def root():
    return {"message": "Hybrid Attendance Management System API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
