# database/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from . import models

def save_user_profile(db: Session, data: dict):
    """Save or update user profile"""
    try:
        profile = models.UserProfile(**data)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_user_profile(db: Session, user_id: int):
    """Get user profile by ID"""
    return db.query(models.UserProfile).filter(models.UserProfile.id == user_id).first()

def get_all_profiles(db: Session):
    """Get all user profiles"""
    return db.query(models.UserProfile).all()

def update_user_profile(db: Session, user_id: int, update_data: dict):
    """Update existing user profile"""
    try:
        profile = db.query(models.UserProfile).filter(models.UserProfile.id == user_id).first()
        if profile:
            for key, value in update_data.items():
                setattr(profile, key, value)
            db.commit()
            db.refresh(profile)
        return profile
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def save_scan_result(db: Session, user_id: int, scan_data: dict):
    """Save scan results for specific user"""
    try:
        # Update existing user profile with scan results
        profile = db.query(models.UserProfile).filter(models.UserProfile.id == user_id).first()
        if profile:
            for key, value in scan_data.items():
                setattr(profile, key, value)
            db.commit()
            db.refresh(profile)
            return profile
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise e