"""
BharatMandir FastAPI Application
Entry point — run with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import temples, route_planner, admin
from db.connection import get_pool, close_pool
import os
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# App initialization
# ─────────────────────────────────────────────

app = FastAPI(
    title="BharatMandir API",
    description="Temple Discovery Platform — PostgreSQL + PostGIS Backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ─────────────────────────────────────────────
# Static files — serve uploaded images/videos
# /uploads/filename.jpg → backend/uploads/filename.jpg
# ─────────────────────────────────────────────

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Startup / Shutdown Events
# ─────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    print("🚀 BharatMandir API starting...")
    try:
        get_pool()
        print("✅ Database pool ready")
    except Exception as e:
        print(f"⚠️  Could not connect to DB on startup: {e}")
        print("🔄  Will retry connection on first API request...")


@app.on_event("shutdown")
async def shutdown_event():
    close_pool()
    print("🔒 Database pool closed")


# ─────────────────────────────────────────────
# Register Routers
# ─────────────────────────────────────────────

app.include_router(temples.router)
app.include_router(route_planner.router)
app.include_router(admin.router)       # ← NEW: Admin routes

# ─────────────────────────────────────────────
# Root & Health Check
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "project": "BharatMandir",
        "version": "1.0.0",
        "status":  "running",
        "docs":    "/api/docs",
    }


@app.get("/api/health")
def health_check():
    try:
        from db.connection import get_db_cursor
        with get_db_cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM temples")
            result = cur.fetchone()
        return {
            "status":        "healthy",
            "database":      "connected",
            "total_temples": result["count"],
        }
    except Exception as e:
        return {
            "status":   "unhealthy",
            "database": "disconnected",
            "error":    str(e),
        }