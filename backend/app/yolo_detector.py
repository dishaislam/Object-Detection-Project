from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from typing import List, Tuple
import time
import torch
import os
import functools

from . import schemas


class YOLODetector:
    
    def __init__(self, model_name: str = "yolov8n.pt"):
        print(f"Loading YOLO model: {model_name}")
        print(f"PyTorch version: {torch.__version__}")
        
        os.environ['YOLO_VERBOSE'] = 'False'
        self._register_safe_globals()
        self._load_model(model_name)
    
    def _register_safe_globals(self):
        """Register YOLO classes for PyTorch 2.6+ compatibility"""
        try:
            from ultralytics.nn.tasks import DetectionModel, SegmentationModel, ClassificationModel
            from ultralytics.engine.model import Model
            
            if hasattr(torch.serialization, 'add_safe_globals'):
                torch.serialization.add_safe_globals([
                    DetectionModel, SegmentationModel, ClassificationModel, Model
                ])
                print(" Registered YOLO classes as safe globals for PyTorch 2.6+")
        except (ImportError, AttributeError) as e:
            print(f"Note: Using legacy PyTorch loading (pre-2.6): {e}")
    
    def _load_model(self, model_name: str):
        """Load YOLO model with fallback mechanisms"""
        try:
            self.model = YOLO(model_name)
            print("✓ YOLO model loaded successfully!")
        except Exception as first_error:
            print(f"Warning: Standard load failed: {first_error}")
            print("Attempting alternative loading method...")
            self._load_with_patch(model_name)
    
    def _load_with_patch(self, model_name: str):
        """Load model using patched torch.load"""
        original_load = torch.load
        
        @functools.wraps(original_load)
        def patched_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        
        try:
            torch.load = patched_load
            self.model = YOLO(model_name)
            print("YOLO model loaded with patched loader!")
        except Exception as e:
            raise RuntimeError(
                f"Failed to load YOLO model. PyTorch: {torch.__version__}. Error: {e}"
            )
        finally:
            torch.load = original_load
    
    def detect_objects(
        self, 
        image_bytes: bytes, 
        confidence_threshold: float = 0.25
    ) -> Tuple[str, List[schemas.Detection], float]:
        """Run object detection and return annotated image with detections"""
        start_time = time.time()
        
        image_cv = self._bytes_to_cv_image(image_bytes)
        results = self.model(image_cv, conf=confidence_threshold)
        detections = self._extract_detections(results)
        annotated_image = self._draw_boxes(image_cv, detections)
        annotated_base64 = self._image_to_base64(annotated_image)
        
        processing_time = time.time() - start_time
        return annotated_base64, detections, processing_time
    
    def _bytes_to_cv_image(self, image_bytes: bytes) -> np.ndarray:
        """Convert image bytes to OpenCV format"""
        image = Image.open(BytesIO(image_bytes))
        image_np = np.array(image)
        
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            return cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        return image_np
    
    def _extract_detections(self, results) -> List[schemas.Detection]:
        """Extract detection data from YOLO results"""
        detections = []
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])
                
                detection = schemas.Detection(
                    class_name=class_name,
                    confidence=round(confidence, 3),
                    bounding_box=schemas.BoundingBox(
                        x1=round(float(x1), 2),
                        y1=round(float(y1), 2),
                        x2=round(float(x2), 2),
                        y2=round(float(y2), 2)
                    )
                )
                detections.append(detection)
        
        return detections
    
    def _draw_boxes(self, image: np.ndarray, detections: List[schemas.Detection]) -> np.ndarray:
        """Draw bounding boxes and labels on image"""
        annotated = image.copy()
        
        for detection in detections:
            bbox = detection.bounding_box
            x1, y1 = int(bbox.x1), int(bbox.y1)
            x2, y2 = int(bbox.x2), int(bbox.y2)
            
            # Draw rectangle
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Prepare label
            label = f"{detection.class_name}: {detection.confidence:.2f}"
            (text_width, text_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            
            # Draw label background
            cv2.rectangle(
                annotated, 
                (x1, y1 - text_height - 10), 
                (x1 + text_width, y1), 
                (0, 255, 0), 
                -1
            )
            
            # Draw label text
            cv2.putText(
                annotated, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1
            )
        
        return annotated
    
    def _image_to_base64(self, image: np.ndarray) -> str:
        """Convert OpenCV image to base64 string"""
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{image_base64}"


_detector = None

def get_detector() -> YOLODetector:
    """Get or create YOLO detector instance (singleton)"""
    global _detector
    if _detector is None:
        _detector = YOLODetector()
    return _detector