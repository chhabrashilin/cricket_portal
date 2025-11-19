"""
Weakness summary model for aggregated insights
"""
from sqlalchemy import Column, Integer, Text, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from shared.models.base import BaseModel

class WeaknessSummary(BaseModel):
    """
    Weakness summary model for aggregated analysis insights.
    
    Contains natural language summaries, tagged weaknesses, metrics,
    and personalized recommendations.
    """
    __tablename__ = "weakness_summaries"
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    
    # Summaries
    summary_text = Column(Text, nullable=False)  # Natural language overall summary
    strengths_text = Column(Text, nullable=True)  # Natural language strengths
    
    # Structured data
    key_weakness_tags = Column(JSON, nullable=True)  # Array of WeaknessCategory strings
    metric_breakdown = Column(JSON, nullable=True)  # {
    #   total_deliveries: int,
    #   by_delivery_type: {...},
    #   by_shot_type: {...},
    #   by_outcome: {...},
    #   combinations: {...},
    #   line_length_matrix: {...},
    #   timing_consistency: float,
    #   control_percentage: {...},
    #   head_stability_score: float,
    #   footwork_stability_score: float
    # }
    recommendations = Column(JSON, nullable=True)  # {
    #   drills: [str],
    #   focus_points: [str],
    #   weakness_specific_recommendations: {weakness_tag: [str]}
    # }
    
    # Indexes
    __table_args__ = (
        Index('idx_user_session', 'user_id', 'session_id'),
    )
    
    # Relationships
    user = relationship("User", back_populates="weakness_summaries")
    session = relationship("Session", back_populates="weakness_summaries")

