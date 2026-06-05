from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import init_db
from routers import auth, complaints, locker, certificates, notifications, dashboard, admin_users
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
FRONTEND_DIST_DIR = BASE_DIR.parent / "frontend" / "dist"
SPA_EXCLUDED_PREFIXES = (
    "auth",
    "complaints",
    "locker",
    "certificates",
    "notifications",
    "dashboard",
    "admin",
    "files",
    "health",
    "docs",
    "openapi.json",
    "redoc",
)

# Initialize FastAPI app
app = FastAPI(
    title="OneServe API",
    description="Unified Digital Platform for Government & Professional Services",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def on_startup():
    init_db()
    print("Database initialized")

# Include routers
app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(locker.router)
app.include_router(certificates.router)
app.include_router(notifications.router)
app.include_router(dashboard.router)
app.include_router(admin_users.router)

# Mount uploads folder for static files
UPLOADS_DIR.mkdir(exist_ok=True)
(UPLOADS_DIR / "complaints").mkdir(exist_ok=True)
(UPLOADS_DIR / "locker").mkdir(exist_ok=True)
(UPLOADS_DIR / "certificates").mkdir(exist_ok=True)

def _frontend_index_path():
    index_path = FRONTEND_DIST_DIR / "index.html"
    return index_path if index_path.exists() else None

@app.get("/files/complaints/{filename}")
async def get_complaint_image(filename: str):
    """Serve complaint images"""
    file_path = UPLOADS_DIR / "complaints" / filename
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/files/locker/{filename}")
async def get_locker_document(filename: str):
    """Serve locker documents"""
    file_path = UPLOADS_DIR / "locker" / filename
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/files/certificates/{filename}")
async def get_certificate_file(filename: str):
    """Serve certificate files"""
    file_path = UPLOADS_DIR / "certificates" / filename
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

# Root endpoint
@app.get("/")
def root():
    index_path = _frontend_index_path()
    if index_path:
        return FileResponse(index_path)
    return {
        "message": "OneServe API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    index_path = _frontend_index_path()
    if not index_path:
        raise HTTPException(status_code=404, detail="Frontend build not found")

    if full_path.startswith(SPA_EXCLUDED_PREFIXES):
        raise HTTPException(status_code=404, detail="Not found")

    requested_path = FRONTEND_DIST_DIR / full_path
    if requested_path.exists() and requested_path.is_file():
        return FileResponse(requested_path)

    return FileResponse(index_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
