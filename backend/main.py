"""
DriveSafe Backend — main.py
FastAPI REST API — Persoana 1
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import trips, users, health

app = FastAPI(
    title="DriveSafe Backend",
    description="REST API pentru aplicația DriveSafe",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrânge în producție
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routere
app.include_router(health.router)
app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
