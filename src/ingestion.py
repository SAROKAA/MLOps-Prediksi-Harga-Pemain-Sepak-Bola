import requests
import json
import os
from dotenv import load_dotenv

# Load key dari file .env
load_dotenv()

def fetch_football_data():
    api_key = os.getenv("FOOTBALL_API_KEY")
    
    # Endpoint untuk ambil data pemain (contoh: Premier League id=39)
    url = "https://v3.football.api-sports.io/players"
    query = {"league": "39", "season": "2023"}
    
    headers = {
        "x-apisports-key": api_key
    }

    print("🚀 Memulai proses Ingestion (Data Extraction)...")
    response = requests.get(url, headers=headers, params=query)
    
    if response.status_code == 200:
        data = response.json()
        
        # Pastikan folder data/raw ada
        os.makedirs('data/raw', exist_ok=True)
        
        # Simpan hasil ke data/raw/
        with open('data/raw/players_raw.json', 'w') as f:
            json.dump(data, f)
            
        print(f"✅ Berhasil! Data disimpan di data/raw/players_raw.json")
        print(f"📊 Jumlah data yang didapat: {len(data.get('response', []))}")
    else:
        print(f"❌ Gagal narik data. Status: {response.status_code}")
        print(f"Pesan Error: {response.text}")

if __name__ == "__main__":
    fetch_football_data()