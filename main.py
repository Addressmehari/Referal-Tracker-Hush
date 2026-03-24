from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.db.session import engine, Base
from app.api.endpoints import router as api_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RefChain API", 
             description="A simple, modular API for tracking referrals across any app.")

# Setup templates and static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include the API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
