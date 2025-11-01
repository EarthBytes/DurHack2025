# Pokémon Battle Predictor - ML Algorithm

Machine learning model for predicting Pokémon battle outcomes.

## Setup

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Train the model:
```bash
python train_model.py
```

This will create:
- `pokemon_battle_model.pkl` - Trained model
- `label_encoders.pkl` - Categorical encoders
- `feature_columns.pkl` - Feature column order

## Running the API Server

Start the Flask API server:

```bash
python api.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### `GET /api/pokemon`
Get list of available Pokémon

### `GET /api/pokemon/<name>`
Get stats for a specific Pokémon

### `POST /api/predict`
Predict battle winner

Request body:
```json
{
  "pokemon1": "pikachu",
  "pokemon2": "squirtle",
  "weather": "Rain",
  "status_p1": "None",
  "status_p2": "None",
  "terrain": "None",
  "hazards": "None"
}
```

Response:
```json
{
  "winner": "pokemon1",
  "winner_name": "pikachu",
  "confidence": 0.85,
  "probabilities": {
    "pokemon1": 0.85,
    "pokemon2": 0.15
  },
  "pokemon1": "pikachu",
  "pokemon2": "squirtle"
}
```

## Using the Predictor Directly

```python
from predict import PokemonBattlePredictor

predictor = PokemonBattlePredictor()
result = predictor.predict(
    pokemon1='pikachu',
    pokemon2='squirtle',
    weather='Rain',
    status_p1='None',
    status_p2='None',
    terrain='None',
    hazards='None'
)

print(result)
```

