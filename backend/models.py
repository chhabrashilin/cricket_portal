from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

# Enums
class Handedness(str, enum.Enum):
    LEFT = "left"
    RIGHT = "right"

class SkillLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"

class PrimaryRole(str, enum.Enum):
    BATSMAN = "batsman"
    ALL_ROUNDER = "all_rounder"
    BOWLER = "bowler"

class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"

class DeliveryType(str, enum.Enum):
    SHORT = "short"
    GOOD_LENGTH = "good_length"
    FULL = "full"
    YORKER = "yorker"
    BOUNCER = "bouncer"

class Line(str, enum.Enum):
    OFF_STUMP = "off_stump"
    MIDDLE = "middle"
    LEG_STUMP = "leg_stump"
    WIDE_OFF = "wide_off"
    WIDE_LEG = "wide_leg"

class ShotType(str, enum.Enum):
    DRIVE = "drive"
    PULL = "pull"
    CUT = "cut"
    SWEEP = "sweep"
    DEFENSE = "defense"
    LOFTED = "lofted"
    SLOG = "slog"
    LEAVE = "leave"

class Outcome(str, enum.Enum):
    MIDDLED = "middled"
    EDGE = "edge"
    MISHIT = "mishit"
    MISS = "miss"
    WICKET_RISK = "wicket_risk"

class BowlerType(str, enum.Enum):
    PACE = "pace"
    SPIN = "spin"

class Surface(str, enum.Enum):
    TURF = "turf"
    CEMENT = "cement"
    ASTRO = "astro"

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    handedness = Column(SQLEnum(Handedness), default=Handedness.RIGHT)
    skill_level = Column(SQLEnum(SkillLevel), default=SkillLevel.BEGINNER)
    primary_role = Column(SQLEnum(PrimaryRole), default=PrimaryRole.BATSMAN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    weakness_summaries = relationship("WeaknessSummary", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    location = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    batting_hand = Column(SQLEnum(Handedness), nullable=True)
    bowler_type = Column(SQLEnum(BowlerType), nullable=True)
    surface = Column(SQLEnum(Surface), nullable=True)
    raw_video_url = Column(String, nullable=False)  # S3 path
    thumbnail_url = Column(String, nullable=True)  # S3 path
    processing_status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING, index=True)
    processing_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    deliveries = relationship("Delivery", back_populates="session", cascade="all, delete-orphan")
    weakness_summaries = relationship("WeaknessSummary", back_populates="session", cascade="all, delete-orphan")

class Delivery(Base):
    __tablename__ = "deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    timestamp_in_video = Column(Float, nullable=False)  # seconds
    inferred_delivery_type = Column(SQLEnum(DeliveryType), nullable=True)
    line = Column(SQLEnum(Line), nullable=True)
    shot_type = Column(SQLEnum(ShotType), nullable=True)
    outcome = Column(SQLEnum(Outcome), nullable=True)
    ball_speed_estimate = Column(Float, nullable=True)  # km/h
    bat_speed_estimate = Column(Float, nullable=True)  # km/h
    score_zone = Column(String, nullable=True)  # cover, mid_off, etc.
    rating = Column(Float, nullable=True)  # 0-10
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="deliveries")
    poses = relationship("Pose", back_populates="delivery", cascade="all, delete-orphan")

class Pose(Base):
    __tablename__ = "poses"
    
    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=False, index=True)
    frame_index = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)  # seconds
    keypoints = Column(JSON, nullable=True)  # Joint positions
    derived_metrics = Column(JSON, nullable=True)  # head_stability, stride_length, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    delivery = relationship("Delivery", back_populates="poses")

class WeaknessSummary(Base):
    __tablename__ = "weakness_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    summary_text = Column(Text, nullable=False)
    strengths_text = Column(Text, nullable=True)
    key_weakness_tags = Column(JSON, nullable=True)  # Array of strings
    metric_breakdown = Column(JSON, nullable=True)  # Detailed metrics
    recommendations = Column(JSON, nullable=True)  # Drills and focus points
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="weakness_summaries")
    session = relationship("Session", back_populates="weakness_summaries")
