"""FastAPI backend for Expenses Dashboard."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import spending, income, hierarchy, locations, receipts, transactions, system


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Expenses Dashboard API",
    description="API for managing personal expenses, income, and receipts",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(spending.router, prefix="/api/spending", tags=["spending"])
app.include_router(income.router, prefix="/api/income", tags=["income"])
app.include_router(hierarchy.router, prefix="/api/hierarchy", tags=["hierarchy"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])
app.include_router(receipts.router, prefix="/api/receipts", tags=["receipts"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(system.router, prefix="/api/system", tags=["system"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Expenses Dashboard API", "docs": "/docs"}
