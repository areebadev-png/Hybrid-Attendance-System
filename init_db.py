#!/usr/bin/env python3
"""
Initialize the database for the Hybrid Attendance Management System
"""
from database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    print("You can now run the server with: python app/main.py")
