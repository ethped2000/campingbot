from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from database import init_db
from routes import searches, campgrounds

app = FastAPI(title="CampingBot - Ontario Parks Tracker")

init_db()

app.include_router(searches.router)
app.include_router(campgrounds.router)


@app.get("/")
def read_root():
    return FileResponse("../frontend/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
