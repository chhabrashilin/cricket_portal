"""
Session model for video uploads and analysis
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from shared.models.base import BaseModel
from shared.types.enums import ProcessingStatus, Handedness, BowlerType, Surface

class Session(BaseModel):
    """
    Session model representing a video upload and analysis session.
    
    Tracks video upload, processing status, and metadata.
    """
    __tablename__ = "sessions"
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Session metadata
    title = Column(String, nullable=False)
    location = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Cricket context
    batting_hand = Column(SQLEnum(Handedness), nullable=True)
    bowler_type = Column(SQLEnum(BowlerType), nullable=True)
    surface = Column(SQLEnum(Surface), nullable=True)
    
    # Video storage
    raw_video_url = Column(String, nullable=False)  # S3 path
    thumbnail_url = Column(String, nullable=True)   # S3 path
    
    # Processing
    processing_status = Column(
        SQLEnum(ProcessingStatus),
        default=ProcessingStatus.PENDING,
        index=True,
        nullable=False
    )
    processing_error = Column(Text, nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'processing_status'),
        Index('idx_created_at', 'created_at'),
    )
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    deliveries = relationship("Delivery", back_populates="session", cascade="all, delete-orphan")
    weakness_summaries = relationship("WeaknessSummary", back_populates="session", cascade="all, delete-orphan")

