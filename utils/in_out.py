import cv2
import os

# Nama kelas yang ingin Anda deteksi
PLATE_CLASS_NAME = 'plate' 

def get_plate_crop(image_path: str, model_deteksi, conf_threshold: float = 0.25):
    """
    Mengambil path gambar & model, lalu mengembalikan 
    gambar crop dari plat terbaik yang ditemukan.
    """
    
    # 1. Baca gambar
    img = cv2.imread(image_path)
    if img is None:
        print(f"[ERROR] Gagal membaca gambar: {image_path}")
        return None

    # 2. Jalankan deteksi
    # 'model_deteksi' adalah objek YOLO dari main.py
    results = model_deteksi(img, conf=conf_threshold, verbose=False)

    # 3. Cari plat dengan confidence tertinggi
    best_plate_crop = None
    best_conf = 0.0
    model_names = model_deteksi.names # Ambil daftar nama kelas

    for box in results[0].boxes:
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        class_name = model_names[cls_id]
        
        # Cek apakah ini plat DAN conf-nya lebih baik
        if class_name == PLATE_CLASS_NAME and conf > best_conf:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            best_plate_crop = img[y1:y2, x1:x2] # Crop gambar
            best_conf = conf

    # 4. Kembalikan hasilnya
    if best_plate_crop is not None:
        print(f"[INFO] Plat ditemukan (conf: {best_conf:.2f})")
    else:
        print(f"[WARN] Plat tidak ditemukan di {image_path}")

    # Mengembalikan gambar (sebagai array NumPy) atau None
    return best_plate_crop