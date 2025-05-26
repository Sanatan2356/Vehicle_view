from database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class UserAuthentication(Base):
    __tablename__ = "users"  

    id = Column(Integer, primary_key=True, index=True)  
    username = Column(String(200), nullable=False)
    email = Column(String(50), nullable=False, unique=True)  
    phoneno = Column(String(15), nullable=True)  
    password = Column(String(500), nullable=False)
    confirm_password = Column(String(500),nullable=False)
    
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_buyer = Column(Boolean, default=True)

    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    country=Column(String(50),nullable=True)
    gender = Column(String(10), nullable=True)
    
    profile_picture = Column(String, nullable=True)  
    otp = Column(Integer, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
   
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationship to User Tokens
    tokens = relationship("UserToken", backref="user", cascade="all, delete-orphan")
    
    
class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

