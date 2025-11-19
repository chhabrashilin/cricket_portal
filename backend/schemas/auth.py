from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str
    handedness: Optional[str] = "right"
    skill_level: Optional[str] = "beginner"
    primary_role: Optional[str] = "batsman"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    handedness: str
    skill_level: str
    primary_role: str
    created_at: str
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        return cls.model_validate(obj)

