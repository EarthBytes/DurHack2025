from flask import Flask, request, jsonify
from flask_cors import CORS
from predict import PokemonBattlePredictor
import pandas as pd

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})

# Initialise predictor
predictor = PokemonBattlePredictor()

@app.route('/')
def home():
    return "Pokemon Battle Predictor API is running! Visit /api/pokemon to see available Pokemon."

@app.route('/api/predict', methods=['POST'])
def predict_battle():
    try:
        data = request.get_json(force=True)

        if 'team1' in data and 'team2' in data:
            team1 = data.get('team1', [])
            team2 = data.get('team2', [])
            
            if not team1 or not team2:
                return jsonify({'error': 'Both teams must have at least one Pokemon'}), 400
            
            if len(team1) > 3 or len(team2) > 3:
                return jsonify({'error': 'Teams can have maximum 3 Pokemon'}), 400
            
            weather = data.get('weather', 'Clear')
            terrain = data.get('terrain', 'None')
            hazards = data.get('hazards', 'None')
            
            team1_score = 0
            team2_score = 0
            team1_wins = 0
            team2_wins = 0
            
            for p1 in team1:
                p1 = p1.lower()
                if p1 not in predictor.stats_dict:
                    return jsonify({'error': f'Invalid Pokemon: {p1}'}), 400
                
                for p2 in team2:
                    p2 = p2.lower()
                    if p2 not in predictor.stats_dict:
                        return jsonify({'error': f'Invalid Pokemon: {p2}'}), 400
                    
                    pred = predictor.predict(
                        pokemon1=p1,
                        pokemon2=p2,
                        weather=weather,
                        status_p1='None',
                        status_p2='None',
                        terrain=terrain,
                        hazards=hazards
                    )
                    
                    team1_score += pred['probabilities']['pokemon1']
                    team2_score += pred['probabilities']['pokemon2']
                    
                    if pred['winner'] == 'pokemon1':
                        team1_wins += 1
                    else:
                        team2_wins += 1
            
            total_matchups = len(team1) * len(team2)
            team1_avg_score = team1_score / total_matchups
            team2_avg_score = team2_score / total_matchups
            
            winner = 'team1' if team1_avg_score > team2_avg_score else 'team2'
            confidence = max(team1_avg_score, team2_avg_score)
            
            return jsonify({
                'winner': winner,
                'team1_score': round(team1_avg_score, 3),
                'team2_score': round(team2_avg_score, 3),
                'team1_wins': team1_wins,
                'team2_wins': team2_wins,
                'total_matchups': total_matchups,
                'confidence': round(confidence, 3),
                'probabilities': {
                    'team1': round(team1_avg_score, 3),
                    'team2': round(team2_avg_score, 3)
                }
            })
        
        else:
            pokemon1 = data.get('pokemon1', '').lower()
            pokemon2 = data.get('pokemon2', '').lower()
            weather = data.get('weather', 'Clear')
            status_p1 = data.get('status_p1', 'None')
            status_p2 = data.get('status_p2', 'None')
            terrain = data.get('terrain', 'None')
            hazards = data.get('hazards', 'None')

            if not pokemon1 or not pokemon2:
                return jsonify({'error': 'Both Pokemon must be selected'}), 400

            if pokemon1 == pokemon2:
                return jsonify({'error': 'Pokemon must be different'}), 400

            if pokemon1 not in predictor.stats_dict or pokemon2 not in predictor.stats_dict:
                return jsonify({'error': 'Invalid Pokemon name'}), 400

            result = predictor.predict(
                pokemon1=pokemon1,
                pokemon2=pokemon2,
                weather=weather,
                status_p1=status_p1,
                status_p2=status_p2,
                terrain=terrain,
                hazards=hazards
            )

            return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pokemon', methods=['GET'])
def get_pokemon_list():
    pokemon_list = sorted(list(predictor.stats_dict.keys()))
    return jsonify({'pokemon': pokemon_list})

@app.route('/api/pokemon/<name>', methods=['GET'])
def get_pokemon_stats(name):
    name = name.lower()
    if name not in predictor.stats_dict:
        return jsonify({'error': 'Pokemon not found'}), 404

    stats = predictor.stats_dict[name]
    
    base_stats_row = predictor.base_stats[predictor.base_stats['pokemon'] == name]
    if base_stats_row.empty:
        return jsonify({'error': 'Pokemon not found in base stats'}), 404
    
    base_stats = base_stats_row.iloc[0]
    
    type2_val = base_stats['type2']
    if pd.isna(type2_val) or type2_val == 'None' or str(type2_val).strip() == '':
        type2_val = None
    else:
        type2_val = str(type2_val).strip()

    return jsonify({
        'name': name,
        'type1': str(base_stats['type1']),
        'type2': type2_val,
        'stats': stats
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
