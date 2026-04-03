import joblib
import pandas as pd
import sys

def manual_prediction():
    # 1. Load model dan list fitur
    try:
        data = joblib.load('models/player_value_model_v2.pkl')
        model = data['model']
        features = data['features']
    except FileNotFoundError:
        print("❌ Error: File model tidak ditemukan. Jalankan 'train.py' dulu!")
        return

    print("="*45)
    print("⚽ FOOTBALL PLAYER VALUE PREDICTOR (York Style)")
    print("="*45)
    print("Silakan masukkan atribut pemain di bawah ini:\n")
    
    user_input = {}
    
    # 2. Loop untuk mengambil input dari user
    for feat in features:
        while True:
            try:
                # Memberikan petunjuk range angka biar user nggak bingung
                if feat == 'International reputation':
                    prompt = f"👉 {feat} (1-5): "
                elif feat == 'age':
                    prompt = f"👉 {feat} (15-45): "
                else:
                    prompt = f"👉 {feat} (1-99): "
                
                val = float(input(prompt))
                user_input[feat] = val
                break
            except ValueError:
                print("⚠️  Input harus berupa angka! Coba lagi.")

    # 3. Convert ke DataFrame & Prediksi
    input_df = pd.DataFrame([user_input])
    input_df = input_df[features] # Pastikan urutan kolom sesuai training

    prediction = model.predict(input_df)[0]

    # 4. Output Hasil yang "Cakep"
    print("\n" + "="*45)
    print(f"💰 ESTIMASI HARGA PASAR: €{prediction:,.2f}")
    
    # Bonus: Konversi ke Rupiah (Asumsi 1 Euro = 17.000 IDR) biar makin impresif
    prediction_idr = prediction * 17000
    print(f"🇮🇩 Estimasi dalam Rupiah: Rp {prediction_idr:,.0f}")
    print("="*45)

if __name__ == "__main__":
    manual_prediction()