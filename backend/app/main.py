"""FastAPI application entry point for the Fat Loss PK backend."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import auth, dashboard, food, friends, pk, weight, admin

app = FastAPI(
    title="减脂PK Backend",
    description="Fat Loss PK - A weight loss competition application",
    version="1.0.0",
)

# Ensure uploads directory exists
os.makedirs("uploads/avatars", exist_ok=True)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS - restrict to your domain in production
allowed_origins = os.environ.get("CORS_ORIGINS", "http://localhost:8080,http://yoyo678.cc.cd,https://yoyo678.cc.cd").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("Fat Loss PK backend starting up...")
    try:
        from app.init_db import init_db
        init_db()
    except Exception as e:
        print(f"Error during init_db on startup: {e}")



@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("Fat Loss PK backend shutting down...")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "fat-loss-pk", "version": "1.0.0"}


# Include all routers under /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(food.router, prefix="/api")
app.include_router(weight.router, prefix="/api")
app.include_router(friends.router, prefix="/api")
app.include_router(pk.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
