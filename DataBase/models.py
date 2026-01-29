# database/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from .db_config import Base

class Gender(Base):
    __tablename__ = "genders"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), unique=True)
    display_name = Column(String(64))
    is_exact_match = Column(Boolean, default=True)

class BodyType(Base):
    __tablename__ = "body_types"
    id = Column(Integer, primary_key=True)
    code = Column(String(32), unique=True)
    display_name = Column(String(64))
    is_exact_match = Column(Boolean, default=True)

class SkinTone(Base):
    __tablename__ = "skin_tones"
    id = Column(Integer, primary_key=True)
    code = Column(String(32), unique=True)
    display_name = Column(String(64))
    is_exact_match = Column(Boolean, default=False)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    gender_id = Column(Integer, ForeignKey("genders.id"))
    life_stage_id = Column(Integer)
    occasion_id = Column(Integer)
    price_range_id = Column(Integer)
    season_id = Column(Integer)
    unisex_preference = Column(Boolean)
    body_type_id = Column(Integer, ForeignKey("body_types.id"))
    skin_tone_id = Column(Integer, ForeignKey("skin_tones.id"))
    timestamp = Column(Float)
