import cv2
import os

def get_plate_string(crop_image_path: str, 
                       model_ocr, 
                       processed_output_dir: str,
                       ocr_output_dir: str,
                       conf_threshold: float = 0.6):
    """
    Menerima path crop, menjalankan OCR, menyimpan gambar proses DAN
    gambar hasil deteksi, lalu mengembalikan string yang sudah difilter.
    """
    
    base_filename = os.path.basename(crop_image_path)
    
    img = cv2.imread(crop_image_path)
    if img is None:
        print(f"[ERROR OCR] Gagal membaca gambar crop: {crop_image_path}")
        return ""

    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(bilateral)
        processed_bgr = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
    except Exception as e:
        print(f"[WARN OCR] Gagal processing: {e}")
        processed_bgr = img

    try:
        save_path_proc = os.path.join(processed_output_dir, f"proc_{base_filename}")
        cv2.imwrite(save_path_proc, processed_bgr)
        print(f"[INFO OCR] Gambar proses disimpan ke: {save_path_proc}")
    except Exception as e:
        print(f"[WARN OCR] Gagal menyimpan gambar proses: {e}")

    results = model_ocr(processed_bgr, conf=conf_threshold, verbose=False)
    
    try:
        img_with_boxes = results[0].plot() 
        save_path_ocr = os.path.join(ocr_output_dir, f"ocr_{base_filename}")
        cv2.imwrite(save_path_ocr, img_with_boxes)
        print(f"[INFO OCR] Gambar hasil deteksi (mentah) disimpan ke: {save_path_ocr}")
    except Exception as e:
        print(f"[WARN OCR] Gagal menyimpan gambar hasil deteksi: {e}")

    detected_chars = []
    model_names = model_ocr.names

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        class_name = model_names[cls_id]
        
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        height = y2 - y1
        y_center = y1 + (height / 2)
        x_center = x1 + ((x2 - x1) / 2)
        
        detected_chars.append({
            'char': class_name, 
            'x': x_center, 
            'y': y_center, 
            'h': height
        })

    if not detected_chars:
        print(f"[WARN OCR] Tidak ada karakter terdeteksi di {crop_image_path}")
        return ""

    all_y = sorted([c['y'] for c in detected_chars])
    all_h = sorted([c['h'] for c in detected_chars])
    
    median_y = all_y[len(all_y) // 2]
    median_h = all_h[len(all_h) // 2]

    y_tolerance = median_h * 0.75 
    h_tolerance = median_h * 0.50

    print(f"[DEBUG OCR] Median Y: {median_y:.0f} (Toleransi: {y_tolerance:.0f}), Median H: {median_h:.0f} (Toleransi: {h_tolerance:.0f})")

    filtered_chars = []
    for c in detected_chars:
        is_y_aligned = abs(c['y'] - median_y) < y_tolerance
        is_good_height = c['h'] > h_tolerance

        if is_y_aligned and is_good_height:
            filtered_chars.append(c) 
        else:
            print(f"[DEBUG OCR] Mengabaikan '{c['char']}' (Y: {c['y']:.0f}, H: {c['h']:.0f})")

    filtered_chars.sort(key=lambda c: c['x'])
    plate_string = "".join([c['char'] for c in filtered_chars])
    
    if plate_string:
        print(f"[INFO OCR] String terbaca (setelah filter): {plate_string}")
    else:
        print(f"[WARN OCR] Tidak ada karakter lolos filter di {crop_image_path}")

    return plate_string