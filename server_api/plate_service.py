# plate_service.py

from sqlmodel import Session, select
from datetime import datetime
from fastapi import HTTPException, status

# Import model tabel PlateLog baru
from database import PlateLog

def register_vehicle_in(db: Session, plate_number: str) -> PlateLog:
    """
    Logika untuk alur MASUK. (Tidak berubah)
    """
    plate_number = plate_number.strip().upper()
    if not plate_number:
        raise HTTPException(status_code=400, detail="Plat nomor tidak boleh kosong")

    existing_log = db.exec(
        select(PlateLog).where(
            PlateLog.plate_number == plate_number,
            PlateLog.status == "in"
        )
    ).first()
    
    if existing_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error: Plat {plate_number} sudah tercatat 'in'."
        )

    new_log = PlateLog(plate_number=plate_number, status="in")
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    return new_log


def register_vehicle_out(db: Session, plate_number: str) -> PlateLog | None:
    """
    Logika untuk alur KELUAR.
    MENGEMBALIKAN 'None' JIKA GAGAL, BUKAN ERROR.
    """
    plate_number = plate_number.strip().upper()
    if not plate_number:
        return None # Kasus Gagal 1

    # Cari data 'in' menggunakan PlateLog
    log_to_update = db.exec(
        select(PlateLog).where(
            PlateLog.plate_number == plate_number,
            PlateLog.status == "in"
        )
    ).first()
    
    if not log_to_update:
        # --- PERUBAHAN UTAMA ---
        # JANGAN TAMPILKAN ERROR, tapi kembalikan None
        return None # Kasus Gagal 2: Tidak ditemukan
        # -----------------------
        
    # Kasus Sukses: Update data
    log_to_update.time_out = datetime.now()
    log_to_update.status = "out"
    db.add(log_to_update)
    db.commit()
    db.refresh(log_to_update)
    
    return log_to_update # Kembalikan data log jika sukses