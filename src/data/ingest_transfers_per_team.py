import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Konfigurasi path untuk .env
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../"))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=dotenv_path)

def get_player_ids_by_team(team_name):
    """Membaca file statistik tim tertentu untuk mengambil Player ID"""
    # Mencari file misal: stats_arsenal.json
    filename = f"stats_{team_name.lower().replace(' ', '_')}.json"
    stats_file = os.path.join(project_root, 'data', 'raw', 'league_621', filename)
    
    if not os.path.exists(stats_file):
        print(f"❌ File statistik untuk {team_name} tidak ditemukan di {stats_file}")
        return []

    with open(stats_file, 'r') as f:
        content = json.load(f)
        players = content.get('content', {}).get('response', [])
        return [str(p['player_id']) for p in players if p.get('player_id')]

def ingest_transfers_by_team(team_name):
    api_key = os.getenv("RAPIDAPI_KEY")
    url = "https://live-football-api.p.rapidapi.com/player-transfers"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "live-football-api.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    player_ids = get_player_ids_by_team(team_name)
    if not player_ids: return

    # Folder penyimpanan khusus tim ini (Landing Zone - ABD04)
    save_dir = os.path.join(project_root, 'data', 'raw', 'transfers', team_name.lower())
    os.makedirs(save_dir, exist_ok=True)

    print(f"🚀 Ingestion Transfer: {team_name} ({len(player_ids)} pemain)")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for p_id in player_ids:
        path = os.path.join(save_dir, f"transfer_{p_id}_{timestamp}.json")
        if os.path.exists(path): continue

        try:
            print(f"🔍 Fetching Player ID: {p_id}...")
            response = requests.get(url, headers=headers, params={"player_id": p_id, "page": "1"}, timeout=15)
            
            if response.status_code == 429:
                print("⏳ Kuota habis atau limit. Berhenti.")
                break
            
            response.raise_for_status()
            data = response.json()

            with open(path, 'w') as f:
                json.dump({"team": team_name, "player_id": p_id, "data": data}, f, indent=4)
            
            print(f"✅ Tersimpan: transfer_{p_id}.json")
            time.sleep(2) # Management Velocity agar aman

        except Exception as e:
            print(f"❌ Gagal pada ID {p_id}: {e}")
            if "401" in str(e): break

    print(f"🏁 Selesai untuk tim {team_name}!")

if __name__ == "__main__":
    # Pilihan: 'manchester_city', 'arsenal', 'liverpool', 'manchester_united', dll.
    target_team = "liverpool" 
    ingest_transfers_by_team(target_team)