# C:\Users\Rence\Downloads\Lakb.ai-main\src\storage\models.py

from sqlalchemy import Column, Integer, String, Enum, Float, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
import enum

# Initialize the declarative base
Base = declarative_base()

# -----------------------
# USER ROLE ENUM
# -----------------------
class UserRole(enum.Enum):
    """Defines the roles a user can have in the application."""
    traveler = "traveler"
    admin = "admin"

# -----------------------
# USERS TABLE
# -----------------------
class Users(Base):
    """Database model for application users."""
    
    __tablename__ = "users" # REQUIRED: Links the class to the physical table name

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(180), unique=True, nullable=False)
    email = Column(String(180), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Stores the role as a string in the database, validating against the UserRole Enum
    role = Column(Enum(UserRole), default=UserRole.traveler, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}', role='{self.role.value}')>"

# -----------------------
# PLACES TABLE
# -----------------------
class Places(Base):
    """Database model for travel destinations and points of interest."""

    __tablename__ = "places"

    place_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    image_url = Column(String(255))
    rating = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Place(id={self.place_id}, name='{self.name}', location='{self.location}')>"