"""
User model with roles and extended profile
"""
from sqlalchemy import Column, String, Integer, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from shared.models.base import BaseModel
from shared.types.enums import UserRole, Handedness, ExperienceLevel, PlayStyle

class User(BaseModel):
    """
    User model with authentication and profile information.
    
    Supports role-based access: player, coach, admin
    """
    __tablename__ = "users"
    
    # Authentication
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Role-based access
    role = Column(SQLEnum(UserRole), default=UserRole.PLAYER, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Cricket profile
    handedness = Column(SQLEnum(Handedness), default=Handedness.RIGHT, nullable=True)
    age = Column(Integer, nullable=True)
    experience_level = Column(SQLEnum(ExperienceLevel), default=ExperienceLevel.BEGINNER, nullable=True)
    play_style = Column(SQLEnum(PlayStyle), nullable=True)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    weakness_summaries = relationship("WeaknessSummary", back_populates="user", cascade="all, delete-orphan")
    
    def is_player(self) -> bool:
        """Check if user is a player"""
        return self.role == UserRole.PLAYER
    
    def is_coach(self) -> bool:
        """Check if user is a coach"""
        return self.role == UserRole.COACH
    
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.role == UserRole.ADMIN
    
    def can_view_session(self, session_user_id: int) -> bool:
        """
        Check if user can view a session.
        Players can view own sessions, coaches/admins can view all.
        """
        if self.is_admin() or self.is_coach():
            return True
        return self.id == session_user_id

