import google.generativeai as genai
import os
import time
from typing import List, Tuple

from . import schemas


class GeminiService:
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        print("Gemini AI service initialized successfully!")
    
    def answer_question(self,question: str,detections: List[schemas.Detection],image_base64: str = None) -> Tuple[str, float]:
        """Answer question about detected objects"""
        start_time = time.time()
        
        system_instruction = self._create_system_instruction(detections)
        prompt = self._build_prompt(system_instruction, question)
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            answer = self._create_fallback_response(detections, str(e))
        
        return answer, time.time() - start_time
    
    def _build_prompt(self, system_instruction: str, question: str) -> str:
        """Build complete prompt for Gemini"""
        return (
            f"You are an AI assistant helping users understand object detection results.\n\n"
            f"{system_instruction}\n\n"
            f"User Question: {question}\n\n"
            f"Please provide a clear, concise, and accurate answer based on the detection data."
        )
    
    def _create_system_instruction(self, detections: List[schemas.Detection]) -> str:
        """Create formatted detection summary"""
        if not detections:
            return "No objects were detected in the image."
        
        class_counts = self._count_by_class(detections)
        
        parts = [
            "Detection Results:",
            f"Total objects detected: {len(detections)}\n",
            "Object Summary:",
            *[f"- {cls}: {count}" for cls, count in sorted(class_counts.items())],
            "\nDetailed Detection Data:",
            *[self._format_detection(i, det) for i, det in enumerate(detections, 1)]
        ]
        
        return "\n".join(parts)
    
    def _count_by_class(self, detections: List[schemas.Detection]) -> dict:
        """Count detections by class name"""
        counts = {}
        for detection in detections:
            counts[detection.class_name] = counts.get(detection.class_name, 0) + 1
        return counts
    
    def _format_detection(self, index: int, detection: schemas.Detection) -> str:
        """Format single detection for display"""
        bbox = detection.bounding_box
        return (
            f"{index}. {detection.class_name} "
            f"(confidence: {detection.confidence:.3f}, "
            f"location: x1={bbox.x1:.1f}, y1={bbox.y1:.1f}, "
            f"x2={bbox.x2:.1f}, y2={bbox.y2:.1f})"
        )
    
    def _create_fallback_response(self, detections: List[schemas.Detection], error: str) -> str:
        """Create response when API fails"""
        if not detections:
            return "No objects detected and AI service unavailable."
        
        class_counts = self._count_by_class(detections)
        summary = "\n".join(
            f"• {cls}: {count}" for cls, count in sorted(class_counts.items())
        )
        
        return (
            f"AI service temporarily unavailable. "
            f"Detected {len(detections)} objects:\n{summary}"
        )


_service = None

def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance (singleton)"""
    global _service
    if _service is None:
        _service = GeminiService()
    return _service