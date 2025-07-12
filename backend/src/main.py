from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import Base, engine
from src.routers.audits import router as audits_router
from src.utils.logging import logger

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Firewall Policy Optimization Tool",
    description="Backend API for analyzing Palo Alto firewall configurations",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(audits_router)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Firewall Policy Optimization Tool API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Firewall Policy Optimization Tool API")
    uvicorn.run(app, host="0.0.0.0", port=8000)
