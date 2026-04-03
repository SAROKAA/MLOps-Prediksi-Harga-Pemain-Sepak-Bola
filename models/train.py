import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def train_model():

    data_path = 'data/processed/players_final.csv'
    df = pd.read_csv(data_path)

    features = [
        'age', 'rating', 'Potential', 'Short passing', 
        'Dribbling', 'Ball control', 'Sprint speed', 
        'Reactions', 'Shot power', 'International reputation'
    ]

    train_df = df[df['source'] == 'external_york'].dropna(subset=features + ['market_value_clean'])

    X = train_df[features]
    y = train_df['market_value_clean']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Model Performance:\nMSE: {mse:.2f}\nR²: {r2:.2f}")

    os.makedirs('models', exist_ok=True)
    model_data = {
        'model': model,
        'features': features,
    }
    joblib.dump(model_data, 'models/player_value_model_v2.pkl')
    
if __name__ == "__main__":
    train_model()