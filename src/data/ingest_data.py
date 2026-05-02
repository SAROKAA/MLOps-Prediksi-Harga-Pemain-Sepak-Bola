import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def ingest_premier_league_stats():
    api_key = os.getenv("RAPIDAPI_KEY") 
    
    if not api_key:
        print("❌ Error: API_KEY tidak ditemukan di file .env")
        return

    url = "https://live-football-api.p.rapidapi.com/player-statistics"
    league_id = "621" 
    season = "2024"
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "live-football-api.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    # 2. Dictionary Tim dengan ID yang sudah divalidasi (Corrected IDs)
    teams = {
        "69": "Arsenal",
        "70": "Manchester City",
        "65": "Liverpool",
        "51": "Manchester United",
        "60": "Chelsea",
        "54": "Tottenham Hotspur",
        "53": "Newcastle United",
        "94": "Aston Villa",
        "62": "Brighton"
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"🚀 Memulai Ingestion Batch Premier League - {timestamp}")

    for team_id, team_name in teams.items():
        print(f"🔍 Fetching data: {team_name} (ID: {team_id})...")
        
        querystring = {
            "season": season, 
            "league_id": league_id, 
            "team_id": team_id
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=15)
            response.raise_for_status()
            data = response.json()

            # 3. Persistence ke Landing Zone/Raw Layer (ABD04) [cite: 71, 84, 123]
            folder_path = os.path.join('data', 'raw', f'league_{league_id}')
            os.makedirs(folder_path, exist_ok=True)

            filename = f"stats_{team_name.lower().replace(' ', '_')}.json"
            save_path = os.path.join(folder_path, filename)

            with open(save_path, 'w') as f:
                json.dump({
                    "metadata": {
                        "ingested_at": timestamp,
                        "team_id": team_id,
                        "team_name": team_name,
                        "source": "RapidAPI-Live-Football"
                    },
                    "content": data
                }, f, indent=4)

            print(f"✅ Berhasil simpan {team_name}")
            
            # 4. Velocity Management (ABD02) [cite: 55, 72]
            time.sleep(2) 

        except Exception as e:
            print(f"❌ Gagal mengambil data {team_name}: {e}")

    print("\n🏁 Ingestion Selesai! Semua data tim kini ada di Landing Zone.")

if __name__ == "__main__":
    ingest_premier_league_stats()