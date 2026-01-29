# routers/scan.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import base64
import uuid
import os
from sqlalchemy.orm import Session
from DataBase.db_config import SessionLocal
from DataBase import models
from DataBase.recommendations import get_recommendations

router = APIRouter()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserInput(BaseModel):
    style: str
    life_stage: str
    occasion: str
    price_range: str
    season: str
    unisex_preference: bool = False
    image_data: Optional[str] = None  # Base64 image data

@router.post("/scan/")
def start_scan(user: UserInput, db: Session = Depends(get_db)):
    print(f" Scan endpoint called with style: {user.style}")
    
    try:
        # Save image if provided
        image_path = None
        if user.image_data:
            image_path = save_captured_image(user.image_data)
        
        # Process the scan and get body measurements
        scan_result = process_body_scan(user, image_path)
        
        # Map user input to database IDs
        gender_id = map_gender_to_id(user.style)
        price_range_id = map_price_range_to_id(user.price_range)
        season_id = map_season_to_id(user.season)
        occasion_id = map_occasion_to_id(user.occasion)
        life_stage_id = map_life_stage_to_id(user.life_stage)
        
        # For body_type and skin_tone, we'll use the scan result
        # For demo, we'll map to existing IDs or create defaults
        body_type_id = map_body_type_to_id(scan_result.get("body_type", "rectangle"))
        skin_tone_id = map_skin_tone_to_id(scan_result.get("skin_tone", "medium"))
        
        # Create user profile in database
        profile_data = {
            "gender_id": gender_id,
            "life_stage_id": life_stage_id,
            "occasion_id": occasion_id,
            "price_range_id": price_range_id,
            "season_id": season_id,
            "unisex_preference": user.unisex_preference,
            "body_type_id": body_type_id,
            "skin_tone_id": skin_tone_id,
            "timestamp": float(os.times().elapsed)  # Simple timestamp
        }
        
        # Save to database
        profile = models.UserProfile(**profile_data)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        # Get recommendations from database
        recommendations = get_recommendations(db, profile.id)
        
        # Prepare response
        result = {
            "profile_id": profile.id,
            "body_measurements": scan_result.get("body_measurements", {}),
            "detected_body_type": scan_result.get("body_type", "Unknown"),
            "detected_skin_tone": scan_result.get("skin_tone", "Unknown"),
            "style_preferences": user.dict(),
            "image_captured": image_path is not None,
            "recommendations": recommendations
        }
        
        return {
            "status": "success",
            "message": "Body scan completed successfully!",
            "profile_id": profile.id,
            "data": result
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

def save_captured_image(image_data: str):
    """Save base64 image to file"""
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Generate unique filename
        filename = f"scan_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join("uploads", filename)
        
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode and save image
        image_bytes = base64.b64decode(image_data)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        print(f" Image saved: {filepath}")
        return filepath
        
    except Exception as e:
        print(f" Failed to save image: {e}")
        return None

def process_body_scan(user_input: UserInput, image_path: str = None):
    """Process the body scan - integrates with your scanner service"""
    
    # If you have the scanner service, use it
    try:
        from services.scanner import run_scan
        # Convert user input to dict for scanner
        user_data = {
            "style": user_input.style,
            "life_stage": user_input.life_stage,
            "occasion": user_input.occasion,
            "price_range": user_input.price_range,
            "season": user_input.season,
            "unisex_preference": user_input.unisex_preference
        }
        
        # Run the actual scan if image is provided and scanner is available
        if image_path:
            scan_result = run_scan(user_data)
            return scan_result
        else:
            # Fallback to mock data if no image
            return generate_mock_scan_data(user_input)
            
    except ImportError:
        # Fallback if scanner service is not available
        print("⚠️ Scanner service not available, using mock data")
        return generate_mock_scan_data(user_input)

def generate_mock_scan_data(user_input: UserInput):
    """Generate realistic mock scan data based on user input"""
    
    # Body type probabilities based on gender
    if user_input.style.lower() == "male":
        body_types = ["Rectangle", "Inverted Triangle", "Apple"]
        body_weights = [0.4, 0.4, 0.2]
    elif user_input.style.lower() == "female":
        body_types = ["Hourglass", "Pear", "Rectangle", "Apple"]
        body_weights = [0.3, 0.3, 0.3, 0.1]
    else:  # unisex
        body_types = ["Rectangle", "Average"]
        body_weights = [0.7, 0.3]
    
    import random
    body_type = random.choices(body_types, weights=body_weights)[0]
    
    # Skin tones
    skin_tones = ["Very Light", "Light", "Medium", "Tan", "Dark", "Very Dark"]
    skin_tone = random.choice(skin_tones)
    
    # Generate realistic measurements based on body type and gender
    base_height = 170 if user_input.style.lower() == "male" else 160
    base_shoulders = 42 if user_input.style.lower() == "male" else 36
    base_chest = 95 if user_input.style.lower() == "male" else 85
    base_waist = 80 if user_input.style.lower() == "male" else 70
    base_hips = 95 if user_input.style.lower() == "male" else 95
    
    # Adjust measurements based on body type
    if body_type == "Hourglass":
        shoulders = base_shoulders
        waist = base_waist - 8
        hips = base_hips + 5
    elif body_type == "Pear":
        shoulders = base_shoulders - 3
        waist = base_waist - 5
        hips = base_hips + 8
    elif body_type == "Apple":
        shoulders = base_shoulders + 2
        waist = base_waist + 10
        hips = base_hips
    elif body_type == "Inverted Triangle":
        shoulders = base_shoulders + 5
        waist = base_waist
        hips = base_hips - 5
    else:  # Rectangle or Average
        shoulders = base_shoulders
        waist = base_waist
        hips = base_hips
    
    # Add some random variation
    height = base_height + random.randint(-5, 5)
    shoulders = max(30, shoulders + random.randint(-2, 2))
    chest = max(70, base_chest + random.randint(-5, 5))
    waist = max(60, waist + random.randint(-3, 3))
    hips = max(80, hips + random.randint(-3, 3))
    
    body_measurements = {
        "height": height,
        "shoulders": shoulders,
        "chest": chest,
        "waist": waist,
        "hips": hips
    }
    
    return {
        "body_type": body_type,
        "skin_tone": skin_tone,
        "body_measurements": body_measurements
    }

# Mapping functions for database IDs
def map_gender_to_id(gender: str) -> int:
    gender_map = {
        "male": 1,
        "female": 2,
        "unisex": 3
    }
    return gender_map.get(gender.lower(), 3)

def map_price_range_to_id(price_range: str) -> int:
    price_map = {
        "below 1k": 1,
        "1k-2k": 2,
        "2k-5k": 3,
        "5k+": 4
    }
    return price_map.get(price_range.lower().replace(" ", ""), 1)

def map_season_to_id(season: str) -> int:
    season_map = {
        "summer": 1,
        "winter": 2,
        "spring": 3,
        "autumn": 4
    }
    return season_map.get(season.lower(), 1)

def map_occasion_to_id(occasion: str) -> int:
    occasion_map = {
        "casual": 1,
        "formal": 2,
        "party": 3,
        "wedding": 4
    }
    return occasion_map.get(occasion.lower(), 1)

def map_life_stage_to_id(life_stage: str) -> int:
    life_stage_map = {
        "child": 1,
        "teen": 2,
        "adult": 3,
        "senior": 4
    }
    return life_stage_map.get(life_stage.lower(), 3)

def map_body_type_to_id(body_type: str) -> int:
    body_type_map = {
        "hourglass": 1,
        "pear": 2,
        "apple": 3,
        "rectangle": 4,
        "inverted triangle": 5,
        "average": 4,  # Map average to rectangle
        "unknown": 4   # Map unknown to rectangle
    }
    return body_type_map.get(body_type.lower(), 4)

def map_skin_tone_to_id(skin_tone: str) -> int:
    skin_tone_map = {
        "very light": 1,
        "light": 2,
        "medium": 3,
        "tan": 4,
        "dark": 5,
        "very dark": 6
    }
    return skin_tone_map.get(skin_tone.lower(), 3)

# Additional endpoint to get recommendations for existing profiles
@router.get("/recommendations/{profile_id}")
def get_recommendations_for_profile(profile_id: int, db: Session = Depends(get_db)):
    """Get clothing recommendations for an existing profile"""
    try:
        recommendations = get_recommendations(db, profile_id)
        
        return {
            "status": "success",
            "profile_id": profile_id,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")