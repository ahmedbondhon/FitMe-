from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from DataBase.db_config import SessionLocal
from DataBase import curd, Models  # Added Models import
from services.scanner import run_scan

# Initialize a router instance
router = APIRouter(
    prefix="/scan",
    tags=["Scan"]
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define what kind of input data the API expects
class UserInput(BaseModel):
    style: str
    life_stage: str
    occasion: str
    price_range: str
    season: str
    unisex_preference: bool | None = False

@router.post("/")
async def start_scan(user: UserInput, db: Session = Depends(get_db)):
    """Runs scan asynchronously, saves to DB."""
    try:
        import asyncio
        # run blocking scan in a thread so server remains responsive
        scan_result = await asyncio.to_thread(run_scan, user.dict())
        # save to DB
        profile = Models.UserProfile(**scan_result)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return {"profile_id": profile.id, "result": scan_result}
    except Exception as e:
        db.rollback()  # Roll back the transaction on error
        raise HTTPException(status_code=500, detail=str(e))