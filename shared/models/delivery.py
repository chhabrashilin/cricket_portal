"""
Delivery/Shot model for individual ball analysis
"""
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from shared.models.base import BaseModel
from shared.types.enums import DeliveryType, Line, ShotType, Outcome

class Delivery(BaseModel):
    """
    Delivery model representing a single ball/shot in a session.
    
    Contains classification, outcome, and performance metrics.
    """
    __tablename__ = "deliveries"
    
    # Foreign keys
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    
    # Timing
    timestamp_in_video = Column(Float, nullable=False)  # seconds
    
    # Classification
    inferred_delivery_type = Column(SQLEnum(DeliveryType), nullable=True)
    line = Column(SQLEnum(Line), nullable=True)
    shot_type = Column(SQLEnum(ShotType), nullable=True)
    outcome = Column(SQLEnum(Outcome), nullable=True)
    
    # Performance metrics
    ball_speed_estimate = Column(Float, nullable=True)  # km/h
    bat_speed_estimate = Column(Float, nullable=True)  # km/h
    score_zone = Column(String, nullable=True)  # cover, mid_off, etc.
    rating = Column(Float, nullable=True)  # 0-10
    
    # Indexes for analysis queries
    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp_in_video'),
        Index('idx_delivery_shot', 'inferred_delivery_type', 'shot_type'),
        Index('idx_outcome', 'outcome'),
    )
    
    # Relationships
    session = relationship("Session", back_populates="deliveries")
    poses = relationship("Pose", back_populates="delivery", cascade="all, delete-orphan")

