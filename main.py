from fastapi import FastAPI
from DataBase.db_config import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Create the app
app = FastAPI(title="FitMe Backend API")

# Create database tables
Base.metadata.create_all(bind=engine)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the scan router
from routers.scan import router as scan_router
app.include_router(scan_router)

# Create static directory if it doesn't exist
if not os.path.exists("static"):
    os.makedirs("static")

#  FIX: Mount static files at /static instead of root
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

#  ADD: Serve index.html at root
@app.get("/")
def serve_frontend():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")

# Test route to verify API is working
@app.get("/test")
def test_route():
    return {"status": "success", "message": "API is working correctly!"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "FitMe Backend"}