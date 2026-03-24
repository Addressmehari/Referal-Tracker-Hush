from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base
import secrets

class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True, default=lambda: secrets.token_hex(16))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="app", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"))
    
    # The ID of the user in the EXTERNAL app (e.g., "user_99" from HabitTracker)
    external_user_id = Column(String, index=True)
    
    # The referral code generated for this user
    referral_code = Column(String, unique=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Status (e.g., if they are active)
    is_active = Column(Boolean, default=True)

    # Relationships
    app = relationship("App", back_populates="users")
    
    # Referrals where THIS user is the referrer
    referrals_made = relationship(
        "Referral", 
        back_populates="referrer",
        foreign_keys="Referral.referrer_id"
    )
    
    # Referral where THIS user is the referee (who referred them?)
    referred_by = relationship(
        "Referral", 
        back_populates="referee", 
        foreign_keys="Referral.referee_id",
        uselist=False
    )

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"))
    
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referee_id = Column(Integer, ForeignKey("users.id"))
    
    # Which code was used for this referral
    code_used = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_made")
    referee = relationship("User", foreign_keys=[referee_id], back_populates="referred_by")
