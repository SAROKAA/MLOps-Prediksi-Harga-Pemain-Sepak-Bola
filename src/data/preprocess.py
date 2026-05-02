import pandas as pd
import json
import os
import glob
import numpy as np
from datetime import datetime
import re

# --- KONFIGURASI PATH ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../"))
stats_dir = os.path.join(project_root, 'data', 'raw', 'league_621')
transfers_base_dir = os.path.join(project_root, 'data', 'raw', 'transfers')
output_dir = os.path.join(project_root, 'data', 'processed')

def clean_currency_to_float(value_str):
    """Mengatasi Karakteristik Data Variety (ABD02)"""
    if not value_str: return 0.0
    s = str(value_str).upper()
    if any(x in s for x in ["FREE", "LOAN", "UNKNOWN", "N/A"]): return 0.0
    
    numeric_part = re.sub(r'[^\d.]', '', s)
    try:
        val = float(numeric_part)
        if 'M' in s: val *= 1_000_000
        if 'K' in s: val *= 1_000
        return val
    except: return 0.0

def process_single_team(stats_file):
    """Memproses satu file statistik tim dan menggabungkannya dengan data transfernya"""
    # Ambil nama tim dari nama file (misal: stats_arsenal.json -> arsenal)
    team_name = os.path.basename(stats_file).replace("stats_", "").replace(".json", "")
    
    with open(stats_file, 'r') as f:
        raw_stats = json.load(f).get('content', {}).get('response', [])
    
    if not raw_stats: return pd.DataFrame()

    df_stats = pd.DataFrame([{
        'player_id': p.get('player_id'),
        'team_name': team_name, # Tambahkan kolom tim sebagai fitur
        'name': p.get('player_name'),
        'rating': float(p.get('statistics', {}).get('games', {}).get('rating') or 0),
        'minutes': p.get('statistics', {}).get('games', {}).get('minutes') or 0,
        'appearances': p.get('statistics', {}).get('games', {}).get('appearences') or 0,
        'goals': p.get('statistics', {}).get('goals', {}).get('total') or 0,
        'assists': p.get('statistics', {}).get('goals', {}).get('assists') or 0,
        'saves': p.get('statistics', {}).get('goals', {}).get('saves') or 0,  # GK stat
        'conceded': p.get('statistics', {}).get('goals', {}).get('conceded') or 0,  # GK stat
        'shots_total': p.get('statistics', {}).get('shots', {}).get('total') or 0,
        'shots_on': p.get('statistics', {}).get('shots', {}).get('on') or 0,
        'passes_total': p.get('statistics', {}).get('passes', {}).get('total') or 0,
        'passes_key': p.get('statistics', {}).get('passes', {}).get('key') or 0,
        'tackles_total': p.get('statistics', {}).get('tackles', {}).get('total') or 0,
        'tackles_blocks': p.get('statistics', {}).get('tackles', {}).get('blocks') or 0,
        'tackles_interceptions': p.get('statistics', {}).get('tackles', {}).get('interceptions') or 0,
        'dribbles_success': p.get('statistics', {}).get('dribbles', {}).get('success') or 0,
        'dribbles_attempts': p.get('statistics', {}).get('dribbles', {}).get('attempts') or 0,
        'duels_won': p.get('statistics', {}).get('duels', {}).get('won') or 0,
        'duels_total': p.get('statistics', {}).get('duels', {}).get('total') or 0,
        'fouls_committed': p.get('statistics', {}).get('fouls', {}).get('committed') or 0,
        'fouls_drawn': p.get('statistics', {}).get('fouls', {}).get('drawn') or 0,
        'cards_yellow': p.get('statistics', {}).get('cards', {}).get('yellow') or 0,
        'cards_red': p.get('statistics', {}).get('cards', {}).get('red') or 0,
        'penalty_scored': p.get('statistics', {}).get('penalty', {}).get('scored') or 0,
        'penalty_missed': p.get('statistics', {}).get('penalty', {}).get('missed') or 0,
        'position': p.get('statistics', {}).get('games', {}).get('position')
    } for p in raw_stats])

    # Cari data transfer di folder tim tersebut
    team_transfer_dir = os.path.join(transfers_base_dir, team_name)
    player_prices = {}
    
    if os.path.exists(team_transfer_dir):
        transfer_files = glob.glob(os.path.join(team_transfer_dir, "transfer_*.json"))
        for t_file in transfer_files:
            try:
                # Parse player_id dari filename (support format: transfer_ID.json atau transfer_ID_timestamp.json)
                filename = os.path.basename(t_file).replace("transfer_", "").replace(".json", "")
                # Ambil hanya bagian pertama sebelum underscore (jika ada)
                p_id = int(filename.split("_")[0])
                
                with open(t_file, 'r') as f:
                    t_list = json.load(f).get('data', {}).get('response', [])
                    prices = [clean_currency_to_float(t.get('type')) for t in t_list]
                    player_prices[p_id] = max(prices) if prices else 0.0
            except: continue

    df_stats['market_value'] = df_stats['player_id'].map(player_prices).fillna(0.0)
    return df_stats

def run_pipeline():
    print("🚀 Menjalankan Preprocessing Pipeline untuk SEMUA tim...")
    
    all_team_files = glob.glob(os.path.join(stats_dir, "stats_*.json"))
    master_list = []

    for file in all_team_files:
        print(f"📦 Processing: {os.path.basename(file)}...")
        df_team = process_single_team(file)
        if not df_team.empty:
            master_list.append(df_team)

    if not master_list:
        print("❌ Tidak ada data yang bisa diproses.")
        return

    # Gabungkan semua tim (Data Integration)
    df_master = pd.concat(master_list, ignore_index=True)

    # Feature Engineering Master
    df_master['goal_contribution'] = df_master['goals'] + df_master['assists']
    df_master['shot_accuracy'] = (df_master['shots_on'] / df_master['shots_total'].replace(0, 1)).fillna(0)
    df_master['pass_ratio'] = (df_master['passes_key'] / df_master['passes_total'].replace(0, 1)).fillna(0)
    df_master['dribble_success_rate'] = (df_master['dribbles_success'] / df_master['dribbles_attempts'].replace(0, 1)).fillna(0)
    df_master['duel_win_rate'] = (df_master['duels_won'] / df_master['duels_total'].replace(0, 1)).fillna(0)
    df_master['defensive_actions'] = df_master['tackles_total'] + df_master['tackles_blocks'] + df_master['tackles_interceptions']
    df_master['discipline_score'] = (df_master['cards_yellow'] * 0.5) + (df_master['cards_red'] * 2)  # Weighted card score
    
    # Cleaning: Buang data sampah (Minutes 0 atau Harga 0)
    df_clean = df_master[(df_master['minutes'] > 0) & (df_master['market_value'] > 0)].copy()

    # Simpan dengan Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, f"data_processed_{timestamp}.csv")
    
    df_clean.to_csv(save_path, index=False)
    print(f"\n✅ SUKSES! Master dataset disimpan di: {save_path}")
    print(f"📊 Total Data: {len(df_clean)} pemain dari {len(master_list)} klub.")

if __name__ == "__main__":
    run_pipeline()