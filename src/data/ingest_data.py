import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def fetch_all_football_data():
    api_key = os.getenv("FOOTBALL_API_KEY")
    url = "https://v3.football.api-sports.io/players"
    headers = {"x-apisports-key": api_key}
    
    all_responses = []
    current_page = 1
    total_pages = 1 # Default awal

    # Poin 3 Tugas Dosen: Timestamp untuk nama file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"Memulai Ingestion (Batch: {timestamp})...")

    while current_page <= total_pages:
        query = {"league": "78", "season": "2024", "page": str(current_page)}
        
        try:
            response = requests.get(url, headers=headers, params=query, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get('errors'):
                error_msg = str(data['errors'])
                if 'plan' in error_msg.lower() or 'limit' in error_msg.lower():
                    print(f"🛑 Berhenti: Mencapai batas maksimal paket (Halaman {current_page-1}).")
                    break
            # Ambil info total halaman dari respon pertama
            if current_page == 1:
                total_pages = data.get('paging', {}).get('total', 1)
                print(f"Terdeteksi total {total_pages} halaman.")

            all_responses.extend(data.get('response', []))
            print(f"✅ Berhasil menarik halaman {current_page}/{total_pages}")
            
            current_page += 1
            
            # Jeda sedikit biar gak kena rate limit API (Safety First)
            time.sleep(2) 

        except Exception as e:
            print(f"Error pada halaman {current_page}: {e}")
            break

    # Simpan semua data yang terkumpul ke satu file bertanda waktu
    if all_responses:
        save_path = os.path.join('data', 'raw', f'players_raw_{timestamp}.json')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w') as f:
            json.dump({"response": all_responses}, f)
            
        print(f"\nSelesai! {len(all_responses)} pemain disimpan di: {save_path}")
        return save_path
    
    return None

if __name__ == "__main__":
    fetch_all_football_data()