#!/usr/bin/env python3
"""
Error checking script for Hybrid Attendance Management System
Run this to check for common errors before starting the server
"""

import sys
import os

def check_imports():
    """Check if all required modules can be imported"""
    print("Checking imports...")
    errors = []
    
    try:
        import fastapi
        print("✓ FastAPI")
    except ImportError as e:
        errors.append(f"✗ FastAPI: {e}")
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy")
    except ImportError as e:
        errors.append(f"✗ SQLAlchemy: {e}")
    
    try:
        import cv2
        print("✓ OpenCV")
    except ImportError as e:
        errors.append(f"✗ OpenCV: {e}")
    
    try:
        import deepface
        print("✓ DeepFace")
    except ImportError as e:
        errors.append(f"✗ DeepFace: {e}")
    
    try:
        from pyzbar import pyzbar
        print("✓ Pyzbar")
    except ImportError as e:
        errors.append(f"✗ Pyzbar: {e}")
    
    try:
        import pandas
        print("✓ Pandas")
    except ImportError as e:
        errors.append(f"✗ Pandas: {e}")
    
    try:
        import reportlab
        print("✓ ReportLab")
    except ImportError as e:
        errors.append(f"✗ ReportLab: {e}")
    
    try:
        import numpy
        print("✓ NumPy")
    except ImportError as e:
        errors.append(f"✗ NumPy: {e}")
    
    return errors

def check_project_structure():
    """Check if all required files exist"""
    print("\nChecking project structure...")
    errors = []
    
    required_files = [
        "app/main.py",
        "database.py",
        "config.py",
        "face_recognition_service.py",
        "barcode_service.py",
        "requirements.txt"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            errors.append(f"✗ Missing: {file}")
    
    return errors

def check_code_imports():
    """Check if project modules can be imported"""
    print("\nChecking code imports...")
    errors = []
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from config import Config
        print("✓ config.py")
    except Exception as e:
        errors.append(f"✗ config.py: {e}")
    
    try:
        from database import init_db, User, Attendance
        print("✓ database.py")
    except Exception as e:
        errors.append(f"✗ database.py: {e}")
    
    try:
        from face_recognition_service import FaceRecognitionService
        print("✓ face_recognition_service.py")
    except Exception as e:
        errors.append(f"✗ face_recognition_service.py: {e}")
    
    try:
        from barcode_service import BarcodeService
        print("✓ barcode_service.py")
    except Exception as e:
        errors.append(f"✗ barcode_service.py: {e}")
    
    return errors

def check_directories():
    """Check if required directories exist or can be created"""
    print("\nChecking directories...")
    errors = []
    
    directories = ["uploads", "face_encodings"]
    
    for dir_name in directories:
        try:
            os.makedirs(dir_name, exist_ok=True)
            print(f"✓ {dir_name}/")
        except Exception as e:
            errors.append(f"✗ Cannot create {dir_name}/: {e}")
    
    return errors

def main():
    print("=" * 50)
    print("Hybrid Attendance System - Error Checker")
    print("=" * 50)
    
    all_errors = []
    
    # Check imports
    all_errors.extend(check_imports())
    
    # Check project structure
    all_errors.extend(check_project_structure())
    
    # Check code imports
    all_errors.extend(check_code_imports())
    
    # Check directories
    all_errors.extend(check_directories())
    
    # Summary
    print("\n" + "=" * 50)
    if all_errors:
        print("ERRORS FOUND:")
        for error in all_errors:
            print(f"  {error}")
        print("\nPlease fix these errors before running the server.")
        print("Install missing dependencies with: pip install -r requirements.txt")
        return 1
    else:
        print("✓ All checks passed! You can run the server now.")
        print("\nTo start the server:")
        print("  python app/main.py")
        return 0

if __name__ == "__main__":
    sys.exit(main())
