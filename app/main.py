from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, clothing, orders, sales, reports, users

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wholesale Clothing Management System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(clothing.router, prefix="/api/clothing", tags=["clothing"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(sales.router, prefix="/api/sales", tags=["sales"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory="static", html=True), name="static_root")

@app.get("/")
async def root():
    return {"message": "Wholesale Clothing Management System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
