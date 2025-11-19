from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class VideoCreate(BaseModel):
    filename: str
    file_path: str
    user_id: Optional[int] = None

class VideoResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    user_id: Optional[int]
    analysis_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Compatibility method for Pydantic v2"""
        return cls.model_validate(obj)

class Weakness(BaseModel):
    category: str  # e.g., "footwork", "balance", "timing", "swing_path"
    severity: str  # "low", "medium", "high"
    description: str
    frame_timestamp: Optional[float] = None
    confidence: float

class Strength(BaseModel):
    category: str
    description: str
    score: float

class AnalysisCreate(BaseModel):
    video_id: int
    overall_score: float
    weaknesses: List[Dict[str, Any]]
    strengths: List[Dict[str, Any]]
    recommendations: List[str]
    detailed_metrics: Dict[str, Any]

class AnalysisResponse(BaseModel):
    id: int
    video_id: int
    overall_score: float
    weaknesses: List[Dict[str, Any]]
    strengths: List[Dict[str, Any]]
    recommendations: List[str]
    detailed_metrics: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Compatibility method for Pydantic v2"""
        return cls.model_validate(obj)

