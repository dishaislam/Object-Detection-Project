from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=6, max_length=100)


class UserResponse(UserBase):
    """Schema for user response (without password)"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


# Token Schemas
class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for JWT token payload"""
    username: Optional[str] = None


# Detection Schemas
class BoundingBox(BaseModel):
    """Schema for bounding box coordinates"""
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    """Schema for a single object detection"""
    class_name: str
    confidence: float
    bounding_box: BoundingBox


class DetectionResponse(BaseModel):
    """Schema for detection API response"""
    annotated_image: str  # Base64 encoded image
    detections: List[Detection]
    processing_time: float


# Q&A Schemas
class QuestionRequest(BaseModel):
    """Schema for asking questions about detections"""
    question: str = Field(..., min_length=1, max_length=500)
    detections: List[Detection]
    image_base64: Optional[str] = None


class AnswerResponse(BaseModel):
    """Schema for AI answer response"""
    answer: str
    processing_time: float