# main.py (Untuk SERVER FastAPI)

from fastapi import FastAPI
from contextlib import asynccontextmanager

# Import file database dan router Anda
from database import create_db_and_tables
from plate_router import router as plate_api_router 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Membuat database dan tabel...")
    create_db_and_tables() # Membuat file parking.db
    print("Database siap!")
    yield
    print("Server dimatikan.")

# INI ADALAH 'app' YANG DICARI OLEH UVICORN
app = FastAPI(
    title="Plate Detection API",
    description="API untuk menerima string plat nomor",
    version="1.0.0",
    lifespan=lifespan 
)

# "Pasang" router dari file plate_router.py
app.include_router(plate_api_router)

@app.get("/")
def read_root():
    return {"message": "API Server berjalan. Buka /docs untuk dokumentasi."}