from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# App schemas
class AppCreate(BaseModel):
    name: str

class AppResponse(BaseModel):
    id: int
    name: str
    api_key: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# User schemas
class UserCreate(BaseModel):
    external_user_id: str

class UserResponse(BaseModel):
    id: int
    external_user_id: str
    referral_code: str
    
    class Config:
        from_attributes = True

# Referral tracking schema
class TrackReferral(BaseModel):
    referee_id: str
    referral_code: str

class ReferralResponse(BaseModel):
    id: int
    referrer_id: int
    referee_id: int
    code_used: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Tree Visualization
class Referee(BaseModel):
    external_user_id: str
    referral_code: str
    children: List["Referee"] = []

class ReferralTree(BaseModel):
    app_name: str
    root_users: List[Referee]
