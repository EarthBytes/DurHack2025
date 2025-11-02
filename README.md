# Pokémon Battle Predictor

A machine learning-powered Pokémon battle prediction system with a web interface.

## Quick Start

### 1. Train the Model

```bash
cd algorithm
pip install -r requirements.txt
python train_model.py
```
This creates the trained model files (`.pkl` files).

### 2. Start the API Server

```bash
cd algorithm
python3 api.py
```

The API will run at `http://localhost:5000`

### 3. Open the Frontend

**Option A: Using Python HTTP Server**
```bash
cd frontend
python3 -m http.server 8000
```
Then open `http://localhost:8000` in your browser.

**Option B: Direct File**
Simply open `frontend/index.html` in your browser (may have CORS issues).

## Features

### ML Model
- **Algorithm**: Random Forest Classifier
- **Accuracy**: ~99.93% on test set
- **Features**: Stats, type advantages, weather, status effects, terrain, hazards
- **Training Data**: 49,500 battle scenarios

### Web Interface
- Select any two Pokémon from 11 available
- Adjust battle conditions:
  - Weather (Sun, Rain, Sandstorm, Hail, Clear)
  - Terrain (Electric, Grassy, Misty, Psychic)
  - Hazards (Stealth Rock, Spikes, Toxic Spikes)
- Set status effects (Burn, Paralysis)
- View prediction with confidence scores

## API Endpoints

- `GET /api/pokemon` - List all Pokémon
- `GET /api/pokemon/<name>` - Get Pokémon stats
- `POST /api/predict` - Predict battle winner

See `algorithm/README.md` for detailed API documentation.

## How It Works

1. 55 unique Pokémon pairs × 900 feature combinations = 49,500 scenarios
2. Individual stats, stat differences, type advantages, dynamic conditions
3. Random Forest learns patterns from training data
4. Model analyses features and predicts winner with confidence

## Model Performance

- Training Accuracy: 100.00%
- Test Accuracy: 99.93%
- Top Features:
  - Total stat difference
  - Status effects
  - Weather conditions
  - Attack difference
  - Type advantage
