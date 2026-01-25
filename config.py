import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
    
    # Face Recognition Configuration
    FACE_RECOGNITION_MODEL = "VGG-Face"  # Options: VGG-Face, Facenet, OpenFace, DeepFace, DeepID, Dlib, ArcFace
    FACE_DETECTION_BACKEND = "opencv"  # Options: opencv, ssd, dlib, mtcnn, retinaface
    FACE_RECOGNITION_THRESHOLD = 0.6  # Lower = more strict
    
    # Barcode Configuration
    BARCODE_TYPES = ["CODE128", "CODE39", "EAN13", "EAN8", "QRCODE"]
    
    # File Upload Configuration
    UPLOAD_FOLDER = "uploads"
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp"}
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
