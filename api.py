"""
FastAPI server for Halloween Quest
Handles photo uploads and status checks
"""

import os
import uuid
import aiofiles
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import config
from database import db
from bot import send_photo_for_review

# FastAPI app
app = FastAPI(title="Halloween Quest API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.WEB_APP_URL, "http://localhost:3000", "https://imasha.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class LinkCheckResponse(BaseModel):
    linked: bool
    parent_name: Optional[str] = None

class PhotoSubmissionResponse(BaseModel):
    success: bool
    submission_id: Optional[str] = None
    message: str

class PhotoStatusResponse(BaseModel):
    status: str  # pending, approved, rejected
    comment: Optional[str] = None
    reviewed_at: Optional[str] = None

# Ensure upload directory exists
os.makedirs(config.PHOTOS_DIR, exist_ok=True)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Halloween Quest API is running", "version": "1.0.0"}

@app.get("/api/check-parent-link/{session_id}", response_model=LinkCheckResponse)
async def check_parent_link(session_id: str):
    """Check if parent is linked to child session"""
    try:
        parent = await db.get_parent_by_session(session_id)
        
        if parent:
            return LinkCheckResponse(
                linked=True,
                parent_name=parent.get("parent_first_name", "Родитель")
            )
        else:
            return LinkCheckResponse(linked=False)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/upload-photo", response_model=PhotoSubmissionResponse)
async def upload_photo(
    session_id: str = Form(...),
    task_id: int = Form(...),
    task_name: str = Form(...),
    photo: UploadFile = File(...)
):
    """Upload photo for parent review"""
    try:
        # Validate file
        if not photo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check file size
        if photo.size > config.MAX_PHOTO_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Check if parent is linked
        parent = await db.get_parent_by_session(session_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not linked")
        
        # Generate unique submission ID
        submission_id = str(uuid.uuid4())
        
        # Generate unique filename
        file_extension = photo.filename.split(".")[-1] if "." in photo.filename else "jpg"
        filename = f"{submission_id}.{file_extension}"
        file_path = os.path.join(config.PHOTOS_DIR, filename)
        
        # Save file
        async with aiofiles.open(file_path, "wb") as f:
            content = await photo.read()
            await f.write(content)
        
        # Create public URL
        photo_url = f"{config.WEB_APP_URL}/uploads/photos/{filename}"
        
        # Save to database
        success = await db.submit_photo(
            submission_id=submission_id,
            child_session_id=session_id,
            task_id=task_id,
            task_name=task_name,
            photo_url=photo_url,
            photo_path=file_path
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save photo submission")
        
        # Send to parent via Telegram
        parent_chat_id = parent["parent_chat_id"]
        bot_success = await send_photo_for_review(parent_chat_id, submission_id, task_name, file_path)
        
        if not bot_success:
            raise HTTPException(status_code=500, detail="Failed to send photo to parent")
        
        return PhotoSubmissionResponse(
            success=True,
            submission_id=submission_id,
            message="Photo uploaded and sent to parent for review"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@app.get("/api/photo-status/{submission_id}", response_model=PhotoStatusResponse)
async def get_photo_status(submission_id: str):
    """Get photo submission status"""
    try:
        submission = await db.get_photo_submission(submission_id)
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        return PhotoStatusResponse(
            status=submission["status"],
            comment=submission.get("parent_comment"),
            reviewed_at=submission.get("reviewed_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/session/{session_id}/photos")
async def get_session_photos(session_id: str):
    """Get all photo submissions for a session"""
    try:
        # TODO: Implement if needed
        return {"message": "Feature not implemented yet"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "message": str(exc.detail)}
    )

@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "Something went wrong"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
