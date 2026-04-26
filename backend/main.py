from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, SessionLocal
from routes import searches, campgrounds
from scheduler import start_scheduler, stop_scheduler, get_last_run_time
from scrapers.ontario_parks import seed_campgrounds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CampingBot - Ontario Parks Tracker")

init_db()

db = SessionLocal()
seed_campgrounds(db)
db.close()

app.include_router(searches.router)
app.include_router(campgrounds.router)

frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/")
def read_root():
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "CampingBot API - Visit /docs for API documentation"}

@app.post("/api/scraper/run")
def trigger_scraper():
    """Manually trigger the scraper immediately"""
    from scheduler import run_scraper_job
    try:
        run_scraper_job()
        return {"status": "success", "message": "Scraper job triggered"}
    except Exception as e:
        logger.error(f"Error triggering scraper: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/scraper/status")
def scraper_status():
    """Get scraper status and last run time"""
    last_run = get_last_run_time()
    return {
        "last_run": last_run,
        "status": "running"
    }

@app.on_event("startup")
async def startup_event():
    logger.info("Starting CampingBot...")
    start_scheduler()
    logger.info("CampingBot started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down CampingBot...")
    stop_scheduler()
    logger.info("CampingBot shut down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
