# AI Image Analysis & Q&A Platform

A full-stack AI web application that allows users to upload images, run object detection using YOLOv8, and ask questions about the detected objects using Gemini AI.

## Features

- **User Authentication**: Secure login/signup with JWT tokens
- **Image Upload**: Upload images for object detection
- **YOLO Object Detection**: Real-time object detection with bounding boxes
- **Results Visualization**: Sortable table with detection results
- **AI Q&A**: Ask questions about detected objects using Gemini AI
- **Responsive Design**: Works on desktop and mobile devices

## Architecture

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **State Management**: React hooks
- **API Communication**: Fetch API

### Backend (FastAPI)
- **Framework**: FastAPI (Python)
- **Object Detection**: YOLOv8 (Ultralytics)
- **AI Assistant**: Google Gemini 2.5 Flash
- **Authentication**: JWT tokens with bcrypt password hashing
- **Database**: SQLite (can be upgraded to PostgreSQL)

### Docker
- Multi-container setup with docker-compose
- Separate containers for frontend, backend, and database
- Volume mounts for data persistence

## Technical Stack

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python, YOLOv8, Gemini API
- **Database**: SQLite
- **Containerization**: Docker, Docker Compose

## Prerequisites

- Docker and Docker Compose installed
- Google Gemini API key (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/dishaislam/Object-Detection-Project.git
   cd yolo-detection-app
   ```

2. **Set up environment variables**
   
   Create a `.env` file in the backend directory:
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Edit `backend/.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

3. **Run the application**
   ```bash
   docker compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Usage

1. **Sign Up**: Create a new account on the signup page
2. **Login**: Log in with your credentials
3. **Upload Image**: Select an image file from your device
4. **Detect Objects**: Click the "Detect Objects" button
5. **View Results**: See the annotated image and sortable detection table
6. **Ask Questions**: Use the Q&A box to ask questions about detected objects

## Project Structure

```
yolo-detection-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── auth.py              # Authentication logic
│   │   ├── database.py          # Database configuration
│   │   ├── models.py            # Database models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── yolo_detector.py     # YOLO detection service
│   │   └── gemini_service.py    # Gemini AI service
│   ├── models/                  # YOLO model weights
│   ├── static/uploads/          # Uploaded images
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Home/Login page
│   │   │   ├── signup/          # Signup page
│   │   │   ├── dashboard/       # Main application
│   │   │   └── layout.tsx
│   │   ├── components/          # React components
│   │   ├── lib/                 # Utility functions
│   │   └── types/               # TypeScript types
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   └── tailwind.config.js
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/signup` - Create new user account
- `POST /api/login` - Login and get JWT token

### Detection
- `POST /api/detect` - Upload image and run object detection
- `POST /api/ask` - Ask questions about detection results

## Development

### Running without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

**Backend (.env):**
- `GEMINI_API_KEY`: Your Google Gemini API key
- `SECRET_KEY`: Secret key for JWT token generation
- `DATABASE_URL`: Database connection string (default: SQLite)

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Secure HTTP-only cookie support
- Input validation with Pydantic
- CORS configuration for production

## Troubleshooting

**Issue**: YOLO model not downloading
- **Solution**: Check internet connection. Model will auto-download on first run.

**Issue**: Gemini API errors
- **Solution**: Verify your API key in the `.env` file

**Issue**: Docker containers not starting
- **Solution**: Ensure ports 3000 and 8000 are not in use

## Future Enhancements

- User profile management
- Detection history
- Batch image processing
- Export results to CSV/PDF
- Multiple YOLO model support
- Real-time webcam detection

Sharmin Islam Disha 