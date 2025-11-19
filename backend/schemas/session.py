from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SessionCreate(BaseModel):
    title: str
    location: Optional[str] = None
    notes: Optional[str] = None
    batting_hand: Optional[str] = None
    bowler_type: Optional[str] = None
    surface: Optional[str] = None

class SessionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    location: Optional[str]
    notes: Optional[str]
    batting_hand: Optional[str]
    bowler_type: Optional[str]
    surface: Optional[str]
    raw_video_url: str
    thumbnail_url: Optional[str]
    processing_status: str
    processing_error: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        return cls.model_validate(obj)

class SessionDetailResponse(SessionResponse):
    delivery_count: Optional[int] = 0
    weakness_summary: Optional[dict] = None

class DeliveryResponse(BaseModel):
    id: int
    session_id: int
    timestamp_in_video: float
    inferred_delivery_type: Optional[str]
    line: Optional[str]
    shot_type: Optional[str]
    outcome: Optional[str]
    ball_speed_estimate: Optional[float]
    bat_speed_estimate: Optional[float]
    score_zone: Optional[str]
    rating: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        return cls.model_validate(obj)

class WeaknessSummaryResponse(BaseModel):
    id: int
    user_id: int
    session_id: int
    summary_text: str
    strengths_text: Optional[str]
    key_weakness_tags: Optional[List[str]]
    metric_breakdown: Optional[dict]
    recommendations: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        return cls.model_validate(obj)

class WeaknessDetailResponse(BaseModel):
    overall_summary: str
    strengths: List[str]
    weaknesses: List[dict]
    recommendations: List[str]

