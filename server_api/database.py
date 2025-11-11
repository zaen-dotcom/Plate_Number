# database.py

from sqlmodel import Field, SQLModel, create_engine, Session
from typing import Optional
from datetime import datetime

# Mengganti nama model dari ParkingLog -> PlateLog
class PlateLog(SQLModel, table=True):
    """
    Model yang mendefinisikan tabel 'platelog'.
    ID Unik akan dibuat otomatis di sini.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    plate_number: str = Field(index=True)
    time_in: datetime = Field(default_factory=datetime.now)
    time_out: Optional[datetime] = Field(default=None)
    status: str = Field(default="in") # Status: "in" atau "out"

# Nama file database tetap (bisa diubah jika mau)
sqlite_file_name = "plate.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    """Dipanggil sekali saat server start untuk membuat tabel."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency untuk FastAPI."""
    with Session(engine) as session:
        yield session