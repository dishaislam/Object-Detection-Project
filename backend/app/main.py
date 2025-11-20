from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import os
from . import models, schemas, auth
from .database import engine, get_db
from .yolo_detector import get_detector
from .gemini_service import get_gemini_service

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="YOLO Object Detection API",
    description="API for object detection and AI-powered Q&A",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Authentication Endpoints
@app.post("/api/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # Check if username already exists
    db_user = auth.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@app.post("/api/login", response_model=schemas.Token)
async def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):

    # Authenticate user
    user = auth.authenticate_user(db, user_credentials.username, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(auth.get_current_user)):

    return current_user

@app.post("/api/detect", response_model=schemas.DetectionResponse)
async def detect_objects(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user)
):

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Get YOLO detector
        detector = get_detector()
        
        # Run detection
        annotated_image, detections, processing_time = detector.detect_objects(image_bytes)
        
        return schemas.DetectionResponse(
            annotated_image=annotated_image,
            detections=detections,
            processing_time=round(processing_time, 3)
        )
    
    except Exception as e:
        print(f"Error during detection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )


# Q&A Endpoint
@app.post("/api/ask", response_model=schemas.AnswerResponse)
async def ask_question(
    request: schemas.QuestionRequest,
    current_user: models.User = Depends(auth.get_current_user)
    ):

    try:
        # Get Gemini service
        gemini = get_gemini_service()
        
        # Get answer
        answer, processing_time = gemini.answer_question(
            question=request.question,
            detections=request.detections,
            image_base64=request.image_base64
        )
        
        return schemas.AnswerResponse(
            answer=answer,
            processing_time=round(processing_time, 3)
        )
    
    except Exception as e:
        print(f"Error during Q&A: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "YOLO Object Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
