from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from models import*
from routers import assets, users, menu, orders, expenses, reports,printer
from routers.auth import router as auth_router
from startup import initialize_admin

# Create DB tables
Base.metadata.create_all(bind=engine)

# Initialize default admin
initialize_admin()

# Initialize FastAPI app
app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dede-backend.kejahook.co.ke",
        "https://front.kejahook.co.ke",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(menu.router, prefix="/menu", tags=["Menu"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
app.include_router(assets.router, prefix="/inventory", tags=["Inventory"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(assets.router, prefix="/assets", tags=["Assets"])
app.include_router(printer.router, prefix="/printer", tags=["Printer"])
