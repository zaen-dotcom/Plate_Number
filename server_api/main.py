from fastapi import FastAPI
from contextlib import asynccontextmanager

from database import create_db_and_tables
from plate_router import router as plate_api_router 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Membuat database dan tabel...")
    create_db_and_tables() 
    print("Database siap!")
    yield
    print("Server dimatikan.")

app = FastAPI(
    title="Plate Detection API",
    description="API untuk menerima string plat nomor",
    version="1.0.0",
    lifespan=lifespan 
)

app.include_router(plate_api_router)

@app.get("/")
def read_root():
    return {"message": "API Server berjalan. Buka /docs untuk dokumentasi."}