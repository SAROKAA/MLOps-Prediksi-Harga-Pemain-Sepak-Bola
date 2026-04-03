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
        print("❌ Tidak ada file raw terbaru ditemukan di data/raw/")
        return None
    
    print(f"📂 Memproses file: {latest_raw_path}")

    with open(latest_raw_path, 'r') as f:
        raw_data = json.load(f)

    api_players = []

    for item in raw_data.get('response', []):
        player = item.get('player', {})
        stats_list = item.get('statistics', [])
        stats = stats_list[0] if stats_list else {}

        api_players.append({
            'player_id': player.get('id'),
            'name': player.get('name'),
            'age': player.get('age'),
            'height': player.get('height'),
            'weight': player.get('weight'),
            'nationality': player.get('nationality'),
            'team': stats.get('team', {}).get('name'),
            'league': stats.get('league', {}).get('name'),
            'rating': stats.get('games', {}).get('rating'),
            'position': stats.get('games', {}).get('position'),
            'source': 'api_sports'
        })

    df_api = pd.DataFrame(api_players)

    external_path = 'data/external/players_17937.csv'
    df_ext_cleaned = pd.DataFrame()

    if os.path.exists(external_path):
        print(f"📦 Mengolah data external: {external_path}")
        df_york = pd.read_csv(external_path)
        
        df_ext_cleaned = pd.DataFrame({
            'player_id': df_york['ID'],
            'name': df_york['name'],
            'age': df_york['Age'],
            'height': df_york['Height'], 
            'weight': df_york['Weight'],
            'nationality': None,
            'team': df_york['Team & Contract'].str.split('\n').str[0],
            'league': None,
            'rating': df_york['Overall rating'],
            'position': df_york['Best position'],
            'source': 'external_york',
            'market_value': df_york['Value']
        })
    
    combined_df = pd.concat([df_api, df_ext_cleaned], ignore_index=True)

    # ========================================================
    # 5. DATA CLEANING & TRANSFORMATION 
    # ========================================================
    print("🧹 Memulai pembersihan dan transformasi data mendalam...")

    # A. Pembersihan Satuan Fisik (Height & Weight)
    # Menangani format API ("188 cm") dan data External("182cm / 6'0")
    def clean_physical_stats(val, unit):
        if pd.isna(val): return np.nan
        val = str(val).split('/')[0] # Ambil bagian depan sebelum '/'
        return float(''.join(filter(str.isdigit, val)))

    combined_df['height_cm'] = combined_df['height'].apply(lambda x: clean_physical_stats(x, 'cm'))
    combined_df['weight_kg'] = combined_df['weight'].apply(lambda x: clean_physical_stats(x, 'kg'))

    # B. Konversi Market Value ke Numerik
    if 'market_value' in combined_df.columns:
        combined_df['market_value_clean'] = combined_df['market_value'].astype(str) \
            .str.replace('€', '', regex=False) \
            .str.replace('M', 'e6', regex=False) \
            .str.replace('K', 'e3', regex=False)
        combined_df['market_value_clean'] = pd.to_numeric(combined_df['market_value_clean'], errors='coerce')

    # C. Advanced Imputation (Rating)
    # Mengisi rating kosong berdasarkan rata-rata rating per posisi
    combined_df['rating'] = pd.to_numeric(combined_df['rating'], errors='coerce')
    combined_df['rating'] = combined_df.groupby('position')['rating'].transform(lambda x: x.fillna(x.mean()))

    # D. Feature Engineering 1: BMI (Body Mass Index)
    # Menunjukkan korelasi fisik pemain terhadap performa
    combined_df['bmi'] = combined_df['weight_kg'] / ((combined_df['height_cm'] / 100) ** 2)

    # E. Feature Engineering 2: Age Grouping
    # Mengkategorikan fase karier pemain
    bins = [0, 21, 29, 50]
    labels = ['Junior', 'Prime', 'Senior']
    combined_df['career_stage'] = pd.cut(combined_df['age'], bins=bins, labels=labels)

    # F. Final Selection: Menghapus kolom mentah yang sudah tidak dipakai
    cols_to_drop = ['height', 'weight', 'market_value']
    combined_df.drop(columns=[c for c in cols_to_drop if c in combined_df.columns], inplace=True)

    # ========================================================

    # 6. Simpan Hasil
    os.makedirs('data/processed', exist_ok=True)
    output_file = 'data/processed/players_final.csv'
    combined_df.to_csv(output_file, index=False)
    
    print(f"✅ Selesai! Data diproses: {len(combined_df)} baris.")
    print(f"💾 File tersimpan di: {output_file}")
    print(combined_df[['name', 'rating', 'bmi', 'career_stage']].head())

if __name__ == "__main__":
    preprocess_data()