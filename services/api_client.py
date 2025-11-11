import requests

API_BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT_IN = f"{API_BASE_URL}/api/masuk"
API_ENDPOINT_OUT = f"{API_BASE_URL}/api/keluar"

def send_plate(plate_number: str, direction: str):
    """
    Mengirim string plat nomor ke server berdasarkan 'direction' ('in' atau 'out').
    """
    
    if direction == "in":
        url = API_ENDPOINT_IN
    elif direction == "out":
        url = API_ENDPOINT_OUT
    else:
        print(f"[API CLIENT] Arah tidak diketahui: {direction}")
        return

    payload = {"plate_number": plate_number}
    
    print(f"[API CLIENT] Mengirim '{plate_number}' ke {url}...")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"[SERVER SUKSES] Respon: {response.json()}")
        else:
            print(f"[SERVER GAGAL {response.status_code}] Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"[FATAL] Gagal terhubung ke server di {API_BASE_URL}.")
    except Exception as e:
        print(f"[FATAL] Terjadi error saat mengirim JSON: {e}")