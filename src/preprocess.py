import json
import pandas as pd
import os

def preprocess_data():
    input_file = 'data/raw/players_raw.json'
    output_file = 'data/processed/players_processed.csv'

    if not os.path.exists(input_file):
        print(f"❌ File {input_file} gak ada!")
        return

    with open(input_file, 'r') as f:
        data = json.load(f)

    players_list = data.get('response', [])
    rows = []

    for item in players_list:
        player = item.get('player', {})
        # API ini pake typo 'appearences', jadi kita sesuaikan
        # Kita pake .get() biar kalau datanya null/gak ada, script gak langsung mati
        for stat in item.get('statistics', []):
            games = stat.get('games', {})
            goals_data = stat.get('goals', {})
            
            rows.append({
                'player_id': player.get('id'),
                'name': player.get('name'),
                'age': player.get('age'),
                'team': stat.get('team', {}).get('name'),
                'appearances': games.get('appearences') or 0, # Pake typo API: 'appearences'
                'rating': games.get('rating'),
                'goals': goals_data.get('total') or 0,
                'assists': goals_data.get('assists') or 0
            })

    df = pd.DataFrame(rows)

    # Bersihin data: Hapus yang ratingnya null karena gak bisa dipake buat prediksi
    df = df.dropna(subset=['rating'])
    df['rating'] = df['rating'].astype(float)

    # Feature Engineering sederhana
    df['goal_contribution'] = df['goals'] + df['assists']
    df['market_value_estimate'] = (df['rating'] * 1000000) + (df['goals'] * 500000)

    os.makedirs('data/processed', exist_ok=True)
    df.to_csv(output_file, index=False)

    print(f"✅ Berhasil! {len(df)} data pemain siap di {output_file}")
    print(df[['name', 'rating', 'market_value_estimate']].head())

if __name__ == "__main__":
    preprocess_data()