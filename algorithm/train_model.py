import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Set paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.dirname(__file__)

print("Loading training data...")
df = pd.read_csv(os.path.join(DATA_DIR, 'training_data.csv'))

print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Prepare features and target
print("\nPreparing features...")

# Features to use (exclude identifiers and computed scores)
feature_columns = [
    'p1_hp', 'p1_attack', 'p1_defense', 'p1_sp_attack', 'p1_sp_defense', 'p1_speed', 'p1_total',
    'p2_hp', 'p2_attack', 'p2_defense', 'p2_sp_attack', 'p2_sp_defense', 'p2_speed', 'p2_total',
    'hp_diff', 'attack_diff', 'defense_diff', 'sp_attack_diff', 'sp_defense_diff', 'speed_diff', 'total_diff',
    'type_advantage',
    'weather', 'status_p1', 'status_p2', 'terrain', 'hazards'
]

# Separate numeric and categorical features
numeric_features = [
    'p1_hp', 'p1_attack', 'p1_defense', 'p1_sp_attack', 'p1_sp_defense', 'p1_speed', 'p1_total',
    'p2_hp', 'p2_attack', 'p2_defense', 'p2_sp_attack', 'p2_sp_defense', 'p2_speed', 'p2_total',
    'hp_diff', 'attack_diff', 'defense_diff', 'sp_attack_diff', 'sp_defense_diff', 'speed_diff', 'total_diff',
    'type_advantage'
]

categorical_features = ['weather', 'status_p1', 'status_p2', 'terrain', 'hazards']

# Encode categorical variables
print("Encoding categorical features...")
label_encoders = {}
X_encoded = df[numeric_features].copy()

for feature in categorical_features:
    le = LabelEncoder()
    X_encoded[feature] = le.fit_transform(df[feature])
    label_encoders[feature] = le

# Prepare full feature matrix
X = X_encoded[feature_columns]
y = df['winner']

print(f"Feature matrix shape: {X.shape}")
print(f"Target distribution:\n{y.value_counts()}")

# Split data
print("\nSplitting data into train/test sets...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")

# Train model
print("\nTraining Random Forest Classifier...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Evaluate model
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)

print(f"\nModel Performance:")
print(f"  Training Accuracy: {train_score:.4f}")
print(f"  Test Accuracy: {test_score:.4f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Most Important Features:")
print(feature_importance.head(10).to_string(index=False))

# Save model and encoders
print("\nSaving model and encoders...")
joblib.dump(model, os.path.join(MODEL_DIR, 'pokemon_battle_model.pkl'))
joblib.dump(label_encoders, os.path.join(MODEL_DIR, 'label_encoders.pkl'))
joblib.dump(feature_columns, os.path.join(MODEL_DIR, 'feature_columns.pkl'))

print(f"\n Model saved to: {os.path.join(MODEL_DIR, 'pokemon_battle_model.pkl')}")
print(f" Encoders saved to: {os.path.join(MODEL_DIR, 'label_encoders.pkl')}")
print(f" Feature columns saved to: {os.path.join(MODEL_DIR, 'feature_columns.pkl')}")

