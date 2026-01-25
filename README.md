# Hybrid Attendance Management System

A secure, accurate, and scalable attendance management system that combines AI-based face recognition with barcode scanning for dual verification.

## Features

- **Dual Verification**: Face recognition + Barcode scanning for enhanced security
- **Real-time Attendance Marking**: Mark attendance instantly with camera and barcode scanner
- **User Management**: Register users with face images and unique barcode IDs
- **Attendance Reports**: View, filter, and export attendance records (CSV/PDF)
- **Statistics Dashboard**: Get attendance statistics and analytics
- **RESTful API**: Complete FastAPI backend with comprehensive endpoints

## Technology Stack

### Backend
- **Python 3.8+**
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: Database ORM
- **DeepFace**: Face recognition using deep learning
- **OpenCV**: Image processing
- **Pyzbar**: Barcode scanning
- **SQLite/PostgreSQL/MySQL**: Database support

### Frontend
- **React**: Modern UI with Vite
- **React Router**: Navigation
- **Axios**: API communication
- **Recharts**: Data visualization

## Installation

### Prerequisites
- Python 3.8 or higher
- Webcam or IP camera
- Barcode scanner (USB or camera-based)

### System Dependencies

**For Barcode Scanning (Pyzbar):**

- **Windows**: Download and install [ZBar](http://zbar.sourceforge.net/) or use: `pip install pyzbar` (may require Visual C++ redistributables)
- **Linux (Ubuntu/Debian)**: `sudo apt-get install libzbar0`
- **Linux (Fedora)**: `sudo dnf install zbar`
- **macOS**: `brew install zbar`

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd hybrid-attendance-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python -c "from database import init_db; init_db()"
```

6. **Run the server**
```bash
python app/main.py
# Or using uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Running the Frontend

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "barcode_id=123456789" \
  -F "face_image=@/path/to/face/image.jpg"
```

### 2. Mark Attendance

**Method 1: Face + Barcode**
```bash
curl -X POST "http://localhost:8000/api/attendance/mark-with-barcode" \
  -F "barcode_data=123456789" \
  -F "face_image=@/path/to/face/image.jpg"
```

**Method 2: Face Recognition Only**
```bash
curl -X POST "http://localhost:8000/api/attendance/mark" \
  -F "face_image=@/path/to/face/image.jpg" \
  -F "barcode_data=123456789"
```

### 3. Get Attendance Records

```bash
curl "http://localhost:8000/api/attendance?start_date=2024-01-01&end_date=2024-12-31"
```

### 4. Export Reports

**CSV Export:**
```bash
curl "http://localhost:8000/api/attendance/export/csv?start_date=2024-01-01" -o report.csv
```

**PDF Export:**
```bash
curl "http://localhost:8000/api/attendance/export/pdf?start_date=2024-01-01" -o report.pdf
```

## API Endpoints

### User Management
- `POST /api/users/register` - Register new user
- `GET /api/users` - Get all users
- `DELETE /api/users/{user_id}` - Delete user

### Attendance
- `POST /api/attendance/mark` - Mark attendance (face recognition)
- `POST /api/attendance/mark-with-barcode` - Mark attendance (barcode + face)
- `GET /api/attendance` - Get attendance records
- `GET /api/attendance/stats` - Get attendance statistics
- `GET /api/attendance/export/csv` - Export CSV report
- `GET /api/attendance/export/pdf` - Export PDF report

## Project Structure

```
hybrid-attendance-system/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── database.py              # Database models and setup
├── face_recognition_service.py  # Face recognition service
├── barcode_service.py       # Barcode scanning service
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── README.md               # This file
├── uploads/               # Uploaded images (auto-created)
└── face_encodings/        # Face encodings storage (auto-created)
```

## Configuration

Edit `config.py` or `.env` file to customize:

- **Face Recognition Model**: VGG-Face, Facenet, OpenFace, DeepFace, DeepID, Dlib, ArcFace
- **Face Detection Backend**: opencv, ssd, dlib, mtcnn, retinaface
- **Recognition Threshold**: Adjust sensitivity (default: 0.6)
- **Database**: SQLite (default), PostgreSQL, or MySQL

## Face Recognition Models

The system supports multiple pre-trained models:
- **VGG-Face**: Good balance of speed and accuracy
- **Facenet**: High accuracy, slower
- **OpenFace**: Fast, good for real-time
- **ArcFace**: State-of-the-art accuracy

Change model in `config.py`:
```python
FACE_RECOGNITION_MODEL = "VGG-Face"  # or "Facenet", "ArcFace", etc.
```

## Database Migration

To use PostgreSQL or MySQL:

1. Update `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost/attendance_db
```

2. Install database driver:
```bash
pip install psycopg2-binary  # For PostgreSQL
# or
pip install pymysql  # For MySQL (already in requirements.txt)
```

## Security Considerations

- Change `SECRET_KEY` in production
- Use HTTPS in production
- Restrict CORS origins in production
- Implement authentication/authorization
- Encrypt sensitive data
- Regular database backups

## Troubleshooting

### Face not detected
- Ensure good lighting conditions
- Face should be clearly visible
- Try different face detection backend in config

### Barcode not scanned
- Ensure barcode is clear and readable
- Check barcode format (CODE128, CODE39, EAN13, etc.)
- Use good quality camera/scanner

### Low recognition accuracy
- Collect multiple face images per user (10-20 images)
- Vary lighting, angles, expressions
- Adjust recognition threshold in config
- Use higher accuracy model (Facenet, ArcFace)

## Future Enhancements

- [ ] Real-time camera feed processing
- [ ] Mobile app integration
- [ ] RFID support
- [ ] QR code support
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Advanced analytics dashboard
- [ ] Multi-location support
- [ ] Biometric fallback options

## License

This project is for educational and research purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For questions or support, please open an issue in the repository.
