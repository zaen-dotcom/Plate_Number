import sys
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ultralytics import YOLO
import cv2
# import requests <-- HAPUS INI

# --- IMPORT FILE UTILS & SERVICE BARU ---
from utils.in_out import get_plate_crop
from utils.img_proc import get_plate_string
from services.api_client import send_plate # <-- IMPORT FUNGSI BARU
# ----------------------------------------

PATH_WATCH_IN = os.path.join("images", "in")
PATH_WATCH_OUT = os.path.join("images", "out")

PATH_OUTPUT_BASE = os.path.join("models", "outputs")
SUBDIR_CROP = "crop"
SUBDIR_IMG_PROC = "img_proc"
SUBDIR_OCR = "ocr"

PATH_MODELS = "models"
MODEL_DETECTION_PATH = os.path.join(PATH_MODELS, "detection.pt")
MODEL_OCR_PATH = os.path.join(PATH_MODELS, "plate_number.pt")

# --- HAPUS SEMUA KONFIGURASI API_URL DARI SINI ---


class MyEventHandler(FileSystemEventHandler):
    
    def __init__(self, model_deteksi, model_ocr):
        self.model_deteksi = model_deteksi
        self.model_ocr = model_ocr
        self.abs_watch_in = os.path.abspath(PATH_WATCH_IN)
        self.abs_watch_out = os.path.abspath(PATH_WATCH_OUT)

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        try:
            time.sleep(1)
        except InterruptedError:
            return 

        base_filename = os.path.basename(file_path)
        
        source_subdir = "" # Akan menjadi "in" atau "out"
        
        abs_file_path = os.path.abspath(file_path)

        if abs_file_path.startswith(self.abs_watch_in):
            print(f"[TERDETEKSI 'IN']  : {file_path}")
            source_subdir = "in"
        elif abs_file_path.startswith(self.abs_watch_out):
            print(f"[TERDETEKSI 'OUT'] : {file_path}")
            source_subdir = "out"
        
        if not source_subdir:
            return

        dynamic_crop_path = os.path.join(PATH_OUTPUT_BASE, source_subdir, SUBDIR_CROP)
        dynamic_proc_path = os.path.join(PATH_OUTPUT_BASE, source_subdir, SUBDIR_IMG_PROC)
        dynamic_ocr_path = os.path.join(PATH_OUTPUT_BASE, source_subdir, SUBDIR_OCR)

        # TAHAP 1: DETEKSI & CROP PLAT
        plate_crop_image = get_plate_crop(file_path, self.model_deteksi)
        if plate_crop_image is None:
            return

        # TAHAP 2: SIMPAN CROP
        save_path = os.path.join(dynamic_crop_path, f"crop_{base_filename}")
        cv2.imwrite(save_path, plate_crop_image)
        print(f"[INFO] Crop plat disimpan ke: {save_path}")
        
        # TAHAP 3: BACA STRING
        plate_string = get_plate_string(
            crop_image_path=save_path, 
            model_ocr=self.model_ocr,
            processed_output_dir=dynamic_proc_path,
            ocr_output_dir=dynamic_ocr_path
        )

        if not plate_string:
            return
            
        # --- TAHAP 4: KIRIM STRING (JAUH LEBIH BERSIH) ---
        # Panggil fungsi dari api_client.py
        send_plate(plate_string, source_subdir)
        # ---------------------------------------------

    # --- HAPUS SELURUH FUNGSI 'send_string_to_service' DARI SINI ---


def main():
    # (Fungsi main() tidak berubah, 
    #  semua kode pengecekan folder dan load model tetap sama)
    
    if not os.path.exists(PATH_WATCH_IN) or not os.path.exists(PATH_WATCH_OUT):
        print("Error: Folder 'images/in' dan 'images/out' tidak ditemukan.")
        sys.exit(1)
    
    if not os.path.exists(MODEL_DETECTION_PATH) or not os.path.exists(MODEL_OCR_PATH):
        print(f"Error: Pastikan '{MODEL_DETECTION_PATH}' dan '{MODEL_OCR_PATH}' ada.")
        sys.exit(1)
        
    print("Membuat struktur folder output...")
    for source_dir in ["in", "out"]:
        for subdir in [SUBDIR_CROP, SUBDIR_IMG_PROC, SUBDIR_OCR]:
            path_to_create = os.path.join(PATH_OUTPUT_BASE, source_dir, subdir)
            os.makedirs(path_to_create, exist_ok=True)
        
    print("Memuat model deteksi (detection.pt)...")
    model_deteksi = YOLO(MODEL_DETECTION_PATH)
    print("Model deteksi berhasil dimuat.")
        
    print("Memuat model OCR (plate_number.pt)...")
    model_ocr = YOLO(MODEL_OCR_PATH)
    print("Model OCR berhasil dimuat.")

    print("--- Watchdog Mulai Aktif ---")

    event_handler = MyEventHandler(
        model_deteksi=model_deteksi, 
        model_ocr=model_ocr
    )
    
    observer = Observer()
    observer.schedule(event_handler, path=PATH_WATCH_IN, recursive=False)
    observer.schedule(event_handler, path=PATH_WATCH_OUT, recursive=False)
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nWatchdog dihentikan.")
    
    observer.join()

if __name__ == "__main__":
    main()