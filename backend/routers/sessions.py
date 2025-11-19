from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import User, Session as SessionModel, ProcessingStatus
from auth import get_current_user
from schemas.session import (
    SessionCreate, SessionResponse, SessionDetailResponse,
    DeliveryResponse, WeaknessSummaryResponse, WeaknessDetailResponse
)
from storage import storage_service
from celery_app import celery_app
import uuid
import os

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new session and upload video"""
    # Validate file
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video"
        )
    
    # Check file size (500MB limit)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    await file.seek(0)  # Reset file pointer
    
    if file_size > 500 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 500MB limit"
        )
    
    # Upload to S3
    try:
        s3_key = storage_service.upload_file(
            file.file,
            file.filename or "video.mp4",
            file.content_type or "video/mp4"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        )
    
    # Create session
    session = SessionModel(
        user_id=current_user.id,
        title=session_data.title,
        location=session_data.location,
        notes=session_data.notes,
        batting_hand=session_data.batting_hand,
        bowler_type=session_data.bowler_type,
        surface=session_data.surface,
        raw_video_url=s3_key,
        processing_status=ProcessingStatus.PENDING
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Enqueue analysis job
    try:
        celery_app.send_task(
            "analyze_session",
            args=[session.id, s3_key]
        )
    except Exception as e:
        # Log error but don't fail session creation
        print(f"Failed to enqueue analysis job: {e}")
    
    return SessionResponse.from_orm(session)

@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's sessions"""
    sessions = db.query(SessionModel).filter(
        SessionModel.user_id == current_user.id
    ).order_by(
        SessionModel.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [SessionResponse.from_orm(s) for s in sessions]

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get session details"""
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get delivery count
    delivery_count = len(session.deliveries)
    
    # Get latest weakness summary
    weakness_summary = None
    if session.weakness_summaries:
        latest = max(session.weakness_summaries, key=lambda w: w.created_at)
        weakness_summary = {
            'id': latest.id,
            'summary_text': latest.summary_text,
            'strengths_text': latest.strengths_text,
            'key_weakness_tags': latest.key_weakness_tags
        }
    
    response = SessionDetailResponse.from_orm(session)
    response.delivery_count = delivery_count
    response.weakness_summary = weakness_summary
    
    return response

@router.get("/{session_id}/deliveries", response_model=List[DeliveryResponse])
async def get_deliveries(
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get deliveries for a session"""
    # Verify session belongs to user
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    deliveries = session.deliveries[skip:skip+limit]
    return [DeliveryResponse.from_orm(d) for d in deliveries]

@router.get("/{session_id}/weaknesses", response_model=WeaknessDetailResponse)
async def get_weaknesses(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weakness analysis for a session"""
    # Verify session belongs to user
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get latest weakness summary
    if not session.weakness_summaries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weakness analysis not available yet"
        )
    
    latest = max(session.weakness_summaries, key=lambda w: w.created_at)
    
    # Format response
    weaknesses = []
    if latest.metric_breakdown and 'combinations' in latest.metric_breakdown:
        for tag in latest.key_weakness_tags or []:
            combo_data = latest.metric_breakdown.get('combinations', {}).get(tag, {})
            if combo_data:
                weaknesses.append({
                    'tag': tag,
                    'description': f"Attempted {combo_data.get('attempts', 0)} shots, "
                                 f"middled {combo_data.get('middled', 0)}, "
                                 f"edges {combo_data.get('edges', 0)}",
                    'evidence': {
                        'attempts': combo_data.get('attempts', 0),
                        'middled': combo_data.get('middled', 0),
                        'edges': combo_data.get('edges', 0),
                        'mishits': combo_data.get('mishits', 0),
                        'misses': combo_data.get('misses', 0)
                    },
                    'recommendations': latest.recommendations.get('drills', []) if latest.recommendations else []
                })
    
    strengths = []
    if latest.strengths_text:
        strengths = [s.strip() for s in latest.strengths_text.split('.') if s.strip()]
    
    return WeaknessDetailResponse(
        overall_summary=latest.summary_text,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=latest.recommendations.get('focus_points', []) if latest.recommendations else []
    )

@router.get("/{session_id}/video")
async def get_video_url(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get presigned URL for video download"""
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    try:
        url = storage_service.get_presigned_download_url(session.raw_video_url)
        return {"url": url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate video URL: {str(e)}"
        )

