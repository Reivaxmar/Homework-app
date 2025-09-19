from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import classes, schedule, homework

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Homework App API",
    description="A REST API for managing school schedules, classes, and homework assignments",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(classes.router)
app.include_router(schedule.router)
app.include_router(homework.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Homework App API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}