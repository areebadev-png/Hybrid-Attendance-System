import cv2


import numpy as np
from pyzbar import pyzbar
from PIL import Image
import os
from config import Config

class BarcodeService:
    def __init__(self):
        self.supported_types = Config.BARCODE_TYPES
    
    def decode_barcode_from_image(self, image_path):
        """Decode barcode from image file"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return None, None
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Decode barcodes
            barcodes = pyzbar.decode(gray)
            
            if len(barcodes) == 0:
                return None, None
            
            # Return first barcode data
            barcode = barcodes[0]
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            
            return barcode_data, barcode_type
        except Exception as e:
            print(f"Barcode decoding error: {str(e)}")
            return None, None
    
    def decode_barcode_from_frame(self, frame):
        """Decode barcode from camera frame"""
        try:
            # Convert frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Decode barcodes
            barcodes = pyzbar.decode(gray)
            
            if len(barcodes) == 0:
                return None, None
            
            # Return first barcode data
            barcode = barcodes[0]
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            
            return barcode_data, barcode_type
        except Exception as e:
            print(f"Barcode decoding from frame error: {str(e)}")
            return None, None
    
    def verify_barcode(self, scanned_barcode, user_barcode):
        """Verify if scanned barcode matches user's barcode"""
        return scanned_barcode == user_barcode
    
    def generate_barcode_image(self, barcode_data, barcode_type="CODE128"):
        """Generate barcode image (for testing/display purposes)"""
        try:
            from barcode import Code128
            from barcode.writer import ImageWriter
            import io
            
            code = Code128(barcode_data, writer=ImageWriter())
            buffer = io.BytesIO()
            code.write(buffer)
            buffer.seek(0)
            
            return buffer
        except Exception as e:
            print(f"Barcode generation error: {str(e)}")
            return None
    
    def draw_barcode_on_frame(self, frame, barcode_data, barcode_type):
        """Draw barcode information on frame"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            barcodes = pyzbar.decode(gray)
            
            for barcode in barcodes:
                # Extract barcode location
                points = barcode.polygon
                if len(points) == 4:
                    pts = np.array(points, dtype=np.int32)
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                
                # Extract barcode data
                barcode_data_decoded = barcode.data.decode('utf-8')
                barcode_type_decoded = barcode.type
                
                # Draw text
                x, y = barcode.rect.left, barcode.rect.top
                text = f"{barcode_data_decoded} ({barcode_type_decoded})"
                cv2.putText(frame, text, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            return frame
        except Exception as e:
            print(f"Draw barcode error: {str(e)}")
            return frame
