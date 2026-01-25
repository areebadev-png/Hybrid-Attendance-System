# Common Errors and Solutions

## 1. ModuleNotFoundError (Dependencies Not Installed)

**Error:**
```
ModuleNotFoundError: No module named 'sqlalchemy'
ModuleNotFoundError: No module named 'dotenv'
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt
```

## 2. FastAPI Lifespan Error

**Error:**
```
TypeError: lifespan() missing 1 required positional argument: 'app'
```

**Solution:** Already fixed - lifespan function is now properly defined before app initialization.

## 3. SQLAlchemy 2.0 Compatibility

**Error:**
```
AttributeError: 'declarative_base' object has no attribute...
```

**Solution:** Already fixed - using `DeclarativeBase` instead of deprecated `declarative_base()`.

## 4. Datetime UTC Error (Python 3.12+)

**Error:**
```
DeprecationWarning: datetime.utcnow() is deprecated
```

**Solution:** Already fixed - using `datetime.now(timezone.utc)` instead.

## 5. Service Not Initialized Error

**Error:**
```
AttributeError: 'NoneType' object has no attribute 'extract_face_encoding'
```

**Solution:** Already fixed - added service initialization checks.

## 6. Database Connection Error

**Error:**
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Solution:**
- Ensure you have write permissions in the project directory
- Run `python init_db.py` to initialize the database
- Check that SQLite is available (or configure PostgreSQL/MySQL in .env)

## 7. DeepFace Model Download Error

**Error:**
```
FileNotFoundError: Model weights not found
```

**Solution:**
- DeepFace will automatically download models on first use
- Ensure you have internet connection
- Models are downloaded to `~/.deepface/weights/` directory
- First run may take several minutes

## 8. Barcode Scanner Error (Pyzbar)

**Error:**
```
ImportError: Failed to load libzbar
```

**Solution:**
- **Windows:** Install ZBar from http://zbar.sourceforge.net/
- **Linux:** `sudo apt-get install libzbar0` (Ubuntu/Debian) or `sudo dnf install zbar` (Fedora)
- **macOS:** `brew install zbar`

## 9. OpenCV Error

**Error:**
```
ImportError: libGL.so.1: cannot open shared object file
```

**Solution:**
```bash
# Linux
sudo apt-get install libgl1-mesa-glx

# Or install opencv-python-headless instead
pip uninstall opencv-python
pip install opencv-python-headless
```

## 10. Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
- Change port in `.env` file: `PORT=8001`
- Or kill the process using port 8000:
  ```bash
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  
  # Linux/Mac
  lsof -ti:8000 | xargs kill
  ```

## 11. CORS Error (Frontend)

**Error:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:** Already configured - CORS middleware allows all origins. For production, update `allow_origins` in `app/main.py`.

## 12. File Upload Error

**Error:**
```
413 Request Entity Too Large
```

**Solution:**
- Increase `MAX_UPLOAD_SIZE` in `config.py`
- Or reduce image size before upload

## Quick Fix Checklist

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Initialize database: `python init_db.py`
3. ✅ Install system dependencies (zbar for barcode scanning)
4. ✅ Check Python version (3.8+)
5. ✅ Ensure write permissions in project directory
6. ✅ Check port availability (default: 8000)

## Testing the Installation

```bash
# Test database
python init_db.py

# Test imports
python -c "from database import init_db; print('OK')"

# Run server
python app/main.py
```

## Getting Help

If errors persist:
1. Check Python version: `python --version` (should be 3.8+)
2. Check installed packages: `pip list`
3. Check error logs in terminal output
4. Verify all files are in correct locations
