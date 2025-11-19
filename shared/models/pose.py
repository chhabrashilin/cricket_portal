"""
Pose metrics model for frame-level pose data
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from shared.models.base import BaseModel

class Pose(BaseModel):
    """
    Pose model for frame-level pose estimation data.
    
    Stores keypoints and derived metrics for cricket-specific analysis.
    """
    __tablename__ = "poses"
    
    # Foreign keys
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=False, index=True)
    
    # Frame information
    frame_index = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)  # seconds
    
    # Pose data
    keypoints = Column(JSON, nullable=True)  # Joint positions: {joint_name: {x, y, z, visibility}}
    derived_metrics = Column(JSON, nullable=True)  # {
    #   head_stability: float,
    #   stride_length: float,
    #   bat_angle: float,
    #   backlift_height: float,
    #   center_of_mass: {x, y},
    #   ...
    # }
    
    # Indexes
    __table_args__ = (
        Index('idx_delivery_frame', 'delivery_id', 'frame_index'),
    )
    
    # Relationships
    delivery = relationship("Delivery", back_populates="poses")

