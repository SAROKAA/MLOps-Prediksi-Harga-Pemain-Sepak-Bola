import json
import os
import pandas as pd
import numpy as np
import glob

def get_latest_raw_file():
    raw_files = glob.glob('data/raw/players_raw_*.json')
    if not raw_files:
        return None
    latest_file = max(raw_files, key=os.path.getctime)
    return latest_file

def preprocess_data():
    latest_raw_path = get_latest_raw_file()
    if not latest_raw_path: 
        print("❌ Tidak ada file raw terbaru.")
        return None
    
    with open(latest_raw_path, 'r') as f:
        raw_data = json.load(f)

    # 1. Olah Data API (Fitur teknis diisi NaN karena API tidak menyediakannya)
    api_players = []
    for item in raw_data.get('response', []):
        p = item.get('player', {})
        s = item.get('statistics', [{}])[0]
        api_players.append({
            'player_id': p.get('id'),
            'name': p.get('name'),
            'age': p.get('age'),
            'rating': s.get('games', {}).get('rating'),
            'position': s.get('games', {}).get('position'),
            'source': 'api_sports',
            # Kolom teknis (diisi kosong untuk data API)
            'Potential': np.nan,
            'Short passing': np.nan,
            'Dribbling': np.nan,
            'Ball control': np.nan,
            'Sprint speed': np.nan,
            'Reactions': np.nan,
            'Shot power': np.nan,
            'International reputation': np.nan
        })
    df_api = pd.DataFrame(api_players)

    # 2. Olah Data External (York) - AMBIL FITUR TEKNIS
    external_path = 'data/external/players_17937.csv'
    df_ext_cleaned = pd.DataFrame()

    if os.path.exists(external_path):
        df_york = pd.read_csv(external_path)
        df_ext_cleaned = pd.DataFrame({
            'player_id': df_york['ID'],
            'name': df_york['name'],
            'age': df_york['Age'],
            'rating': df_york['Overall rating'],
            'position': df_york['Best position'],
            'source': 'external_york',
            'market_value_clean': df_york['Value'],
            # Ambil kolom teknis dari CSV York
            'Potential': df_york['Potential'],
            'Short passing': df_york['Short passing'],
            'Dribbling': df_york['Dribbling'],
            'Ball control': df_york['Ball control'],
            'Sprint speed': df_york['Sprint speed'],
            'Reactions': df_york['Reactions'],
            'Shot power': df_york['Shot power'],
            'International reputation': df_york['International reputation']
        })

    # 3. Gabungkan
    combined_df = pd.concat([df_api, df_ext_cleaned], ignore_index=True)

    # 4. Cleaning Market Value
    if 'market_value_clean' in combined_df.columns:
        combined_df['market_value_clean'] = combined_df['market_value_clean'].astype(str) \
            .str.replace('€', '', regex=False).str.replace('M', 'e6', regex=False).str.replace('K', 'e3', regex=False)
        combined_df['market_value_clean'] = pd.to_numeric(combined_df['market_value_clean'], errors='coerce')

    # 5. Imputasi Rating & Kolom Teknis
    # Isi nilai kosong dengan rata-rata agar model tidak error saat dropna
    cols_to_fix = ['rating', 'Potential', 'Short passing', 'Dribbling', 'Ball control', 'Sprint speed', 'Reactions', 'Shot power', 'International reputation']
    for col in cols_to_fix:
        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
        combined_df[col] = combined_df[col].fillna(combined_df[col].mean())

    os.makedirs('data/processed', exist_ok=True)
    combined_df.to_csv('data/processed/players_final.csv', index=False)
    print("✅ Preprocessing Selesai dengan Fitur Lengkap!")

if __name__ == "__main__":
    preprocess_data()