import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

from config.settings import MODEL_DIR, DATA_DIR

def train_salary_model():
    print("Loading salary seed data...")
    csv_path = DATA_DIR / "salary_seed.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Seed data not found at {csv_path}. Please run seed generator first.")
        
    df = pd.read_csv(csv_path)
    
    # Map education levels to numerical scale
    edu_map = {"b.sc": 1, "b.tech": 2, "m.sc": 3, "mca": 4, "m.tech": 5}
    df['education_encoded'] = df['education_level'].str.lower().map(edu_map).fillna(2).astype(int)
    
    # Features & Targets
    # Categorical features to encode: job_role
    # Numeric features to pass through: years_experience, location_tier, num_skills, education_encoded, num_certifications
    feature_cols = ['job_role', 'years_experience', 'location_tier', 'num_skills', 'education_encoded', 'num_certifications']
    X = df[feature_cols]
    y = df['salary']
    
    # Preprocessor
    print("Fitting Column Transformer...")
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['job_role'])
        ],
        remainder='passthrough'
    )
    
    X_processed = preprocessor.fit_transform(X)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)
    
    # Model
    print("Training Random Forest Regressor...")
    rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf_regressor.fit(X_train, y_train)
    
    # Score
    preds = rf_regressor.predict(X_test)
    r2 = r2_score(y_test, preds)
    mae = mean_absolute_error(y_test, preds)
    print(f"Salary Model R2 Score: {r2:.4f}")
    print(f"Salary Model MAE (LPA): {mae:.4f}")
    
    # Save artifacts
    preprocessor_path = MODEL_DIR / "salary_preprocessor.pkl"
    regressor_path = MODEL_DIR / "salary_rf.pkl"
    
    joblib.dump(preprocessor, preprocessor_path)
    joblib.dump(rf_regressor, regressor_path)
    
    print(f"Saved Salary Preprocessor to {preprocessor_path}")
    print(f"Saved Salary Regressor to {regressor_path}")

if __name__ == "__main__":
    train_salary_model()
