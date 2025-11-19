import sys
import os

# Add parent directory to path so we can import from backend
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from celery import Task
from backend.celery_app import celery_app
from backend.analysis.pipeline import AnalysisPipeline
from backend.database import SessionLocal
from backend.models import Session, ProcessingStatus
import logging

logger = logging.getLogger(__name__)

class AnalysisTask(Task):
    """Custom task class with error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        session_id = args[0] if args else None
        if session_id:
            db = SessionLocal()
            try:
                session = db.query(Session).filter(Session.id == session_id).first()
                if session:
                    session.processing_status = ProcessingStatus.FAILED
                    session.processing_error = str(exc)
                    db.commit()
            except Exception as e:
                logger.error(f"Error updating session status: {e}")
            finally:
                db.close()
        logger.error(f"Task {task_id} failed: {exc}")

@celery_app.task(bind=True, base=AnalysisTask, name="analyze_session")
def analyze_session(self, session_id: int, video_url: str):
    """
    Analyze a cricket batting session video
    
    Args:
        session_id: ID of the session to analyze
        video_url: S3 URL or path to the video file
    """
    db = SessionLocal()
    pipeline = AnalysisPipeline()
    
    try:
        # Update status to analyzing
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.processing_status = ProcessingStatus.ANALYZING
        db.commit()
        
        logger.info(f"Starting analysis for session {session_id}")
        
        # Run analysis pipeline
        result = pipeline.analyze(video_url, session_id, db)
        
        # Update status to completed
        session.processing_status = ProcessingStatus.COMPLETED
        session.processing_error = None
        db.commit()
        
        logger.info(f"Analysis completed for session {session_id}")
        return {"status": "completed", "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Analysis failed for session {session_id}: {str(e)}")
        if session:
            session.processing_status = ProcessingStatus.FAILED
            session.processing_error = str(e)
            db.commit()
        raise
    finally:
        db.close()

