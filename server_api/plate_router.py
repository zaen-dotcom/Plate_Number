# plate_router.py

from fastapi import APIRouter, Depends
from sqlmodel import Session
from pydantic import BaseModel

import plate_service
from database import get_session, PlateLog

class PlateRequest(BaseModel):
    plate_number: str

router = APIRouter(
    prefix="/api",
    tags=["Plate"]
)

@router.post("/masuk")
async def api_vehicle_in(
    payload: PlateRequest,
    db: Session = Depends(get_session)
):
    """
    Endpoint untuk mencatat kendaraan MASUK. (Tidak berubah)
    """
    log = plate_service.register_vehicle_in(db, payload.plate_number)
    
    return {
        "status": "sukses",
        "message": "Kendaraan berhasil dicatat masuk",
        "data": {
            "plate_id": log.id,
            "plate_number": log.plate_number,
            "time_in": log.time_in
        }
    }

@router.post("/keluar")
async def api_vehicle_out(
    payload: PlateRequest,
    db: Session = Depends(get_session)
):
    """
    Endpoint untuk mencatat kendaraan KELUAR.
    MENGEMBALIKAN JSON TRUE/FALSE.
    """
    
    # Panggil service (sekarang bisa mengembalikan 'None')
    log = plate_service.register_vehicle_out(db, payload.plate_number)
    
    # --- PERUBAHAN UTAMA DI SINI ---
    if log:
        # Jika 'log' BUKAN None (Sukses), kirim True
        return {
            "status": True,
            "message": "Kendaraan diizinkan keluar."
        }
    else:
        # Jika 'log' ADALAH None (Gagal), kirim False
        return {
            "status": False,
            "message": "Plat tidak ditemukan atau sudah keluar."
        }
    # ---------------------------------