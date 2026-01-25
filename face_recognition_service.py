import cv2
import numpy as np
from deepface import DeepFace
import os
from pathlib import Path
from config import Config
import pickle

class FaceRecognitionService:
    def __init__(self):
        self.model_name = Config.FACE_RECOGNITION_MODEL
        self.backend = Config.FACE_DETECTION_BACKEND
        self.threshold = Config.FACE_RECOGNITION_THRESHOLD
        self.encodings_dir = Path("face_encodings")
        self.encodings_dir.mkdir(exist_ok=True)
    
    def detect_face(self, image_path):
        """Detect face in image and return face region"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None, None
            
            # Use DeepFace to detect face
            face_objs = DeepFace.extract_faces(
                img_path=image_path,
                detector_backend=self.backend,
                enforce_detection=False
            )
            
            if len(face_objs) == 0:
                return None, None
            
            # Return the first detected face
            return face_objs[0], img
        except Exception as e:
            print(f"Face detection error: {str(e)}")
            return None, None
    
    def extract_face_encoding(self, image_path):
        """Extract face encoding/embedding from image"""
        try:
            # Extract face embedding using DeepFace
            embedding = DeepFace.represent(
                img_path=image_path,
                model_name=self.model_name,
                detector_backend=self.backend,
                enforce_detection=False
            )
            
            if embedding and len(embedding) > 0:
                # Convert to numpy array
                encoding = np.array(embedding[0]['embedding'])
                return encoding
            return None
        except Exception as e:
            print(f"Face encoding extraction error: {str(e)}")
            return None
    
    def save_face_encoding(self, user_id, encoding):
        """Save face encoding to file"""
        encoding_path = self.encodings_dir / f"user_{user_id}.pkl"
        with open(encoding_path, 'wb') as f:
            pickle.dump(encoding, f)
        return str(encoding_path)
    
    def load_face_encoding(self, encoding_path):
        """Load face encoding from file"""
        try:
            with open(encoding_path, 'rb') as f:
                encoding = pickle.load(f)
            return encoding
        except Exception as e:
            print(f"Error loading face encoding: {str(e)}")
            return None
    
    def compare_faces(self, encoding1, encoding2):
        """Compare two face encodings and return similarity score"""
        try:
            # Calculate cosine similarity
            dot_product = np.dot(encoding1, encoding2)
            norm1 = np.linalg.norm(encoding1)
            norm2 = np.linalg.norm(encoding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            print(f"Face comparison error: {str(e)}")
            return 0.0
    
    def verify_face(self, image_path, user_encoding_path):
        """Verify if face in image matches stored encoding"""
        try:
            # Extract encoding from input image
            input_encoding = self.extract_face_encoding(image_path)
            if input_encoding is None:
                return False, 0.0
            
            # Load stored encoding
            stored_encoding = self.load_face_encoding(user_encoding_path)
            if stored_encoding is None:
                return False, 0.0
            
            # Compare encodings
            similarity = self.compare_faces(input_encoding, stored_encoding)
            
            # Check if similarity exceeds threshold
            is_match = similarity >= self.threshold
            
            return is_match, similarity
        except Exception as e:
            print(f"Face verification error: {str(e)}")
            return False, 0.0
    
    def recognize_face_from_camera(self, frame):
        """Recognize face from camera frame"""
        try:
            # Save frame temporarily
            temp_path = "temp_camera_frame.jpg"
            cv2.imwrite(temp_path, frame)
            
            # Extract encoding
            encoding = self.extract_face_encoding(temp_path)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return encoding
        except Exception as e:
            print(f"Face recognition from camera error: {str(e)}")
            return None
    
    def find_matching_user(self, input_encoding, db_session, User):
        """Find user whose face encoding matches the input"""
        try:
            users = db_session.query(User).filter(User.is_active == True).all()
            best_match = None
            best_similarity = 0.0
            
            for user in users:
                if user.face_encoding_path and os.path.exists(user.face_encoding_path):
                    stored_encoding = self.load_face_encoding(user.face_encoding_path)
                    if stored_encoding is not None:
                        similarity = self.compare_faces(input_encoding, stored_encoding)
                        if similarity > best_similarity and similarity >= self.threshold:
                            best_similarity = similarity
                            best_match = user
            
            return best_match, best_similarity
        except Exception as e:
            print(f"Find matching user error: {str(e)}")
            return None, 0.0
