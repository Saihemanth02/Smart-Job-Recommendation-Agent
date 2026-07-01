import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.sparse import hstack
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from config.settings import MODEL_DIR, DATA_DIR
from ml.preprocessing import lemmatize_light

def train_job_models():
    print("Loading resumes seed data...")
    csv_path = DATA_DIR / "resumes_seed.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Seed data not found at {csv_path}. Please run seed generator first.")
        
    df = pd.read_csv(csv_path)
    
    print("Preprocessing resume texts...")
    df['cleaned_text'] = df['resume_text'].apply(lemmatize_light)
    
    # Map education levels to numerical scale
    edu_map = {"b.sc": 1, "b.tech": 2, "m.sc": 3, "mca": 4, "m.tech": 5}
    df['education_encoded'] = df['education_level'].str.lower().map(edu_map).fillna(2).astype(int)
    
    # 1. TF-IDF Vectorizer
    print("Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')
    X_tfidf = vectorizer.fit_transform(df['cleaned_text'])
    
    # Save Vectorizer
    vectorizer_path = MODEL_DIR / "tfidf_vectorizer.pkl"
    joblib.dump(vectorizer, vectorizer_path)
    print(f"Saved TF-IDF Vectorizer to {vectorizer_path}")
    
    # 2. Train Multinomial Naive Bayes for Job Category
    y_category = df['job_category']
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X_tfidf, y_category, test_size=0.2, random_state=42, stratify=y_category
    )
    
    print("Training Naive Bayes for Job Category...")
    nb_model = MultinomialNB(alpha=0.1)
    nb_model.fit(X_train_c, y_train_c)
    
    category_preds = nb_model.predict(X_test_c)
    cat_accuracy = accuracy_score(y_test_c, category_preds)
    print(f"Job Category Accuracy: {cat_accuracy:.4f}")
    
    # Save NB Model
    nb_path = MODEL_DIR / "job_category_nb.pkl"
    joblib.dump(nb_model, nb_path)
    print(f"Saved Job Category NB model to {nb_path}")
    
    # 3. Train Random Forest for Job Role
    # Numeric features: years_experience, num_skills, num_certifications, education_level_encoded
    X_numeric = df[['experience_years', 'num_skills', 'num_certifications', 'education_encoded']].values
    
    # Stack TF-IDF with engineered numeric features
    X_combined = hstack([X_tfidf, X_numeric])
    
    y_role = df['job_role']
    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
        X_combined, y_role, test_size=0.2, random_state=42, stratify=y_role
    )
    
    print("Training Random Forest Classifier for Job Role...")
    rf_model = RandomForestClassifier(n_estimators=150, max_depth=25, random_state=42, n_jobs=-1)
    rf_model.fit(X_train_r, y_train_r)
    
    role_preds = rf_model.predict(X_test_r)
    role_accuracy = accuracy_score(y_test_r, role_preds)
    print(f"Job Role RF Accuracy: {role_accuracy:.4f}")
    
    # Save RF Model
    rf_path = MODEL_DIR / "job_role_rf.pkl"
    joblib.dump(rf_model, rf_path)
    print(f"Saved Job Role RF model to {rf_path}")
    
if __name__ == "__main__":
    train_job_models()
