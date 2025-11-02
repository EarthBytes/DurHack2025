import pandas as pd
import numpy as np
import joblib
import os

# Set paths
MODEL_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

class PokemonBattlePredictor:
    def __init__(self):
        self.model = joblib.load(os.path.join(MODEL_DIR, 'pokemon_battle_model.pkl'))
        self.label_encoders = joblib.load(os.path.join(MODEL_DIR, 'label_encoders.pkl'))
        self.feature_columns = joblib.load(os.path.join(MODEL_DIR, 'feature_columns.pkl'))
        
        self.base_stats = pd.read_csv(os.path.join(DATA_DIR, 'base_stats.csv'))
        self.stats_dict = {}
        for _, row in self.base_stats.iterrows():
            type2_val = row['type2']
            if pd.isna(type2_val) or type2_val == 'None' or str(type2_val).strip() == '':
                type2_val = None
            else:
                type2_val = str(type2_val).strip()
            
            self.stats_dict[row['pokemon']] = {
                'hp': int(row['hp']),
                'attack': int(row['attack']),
                'defense': int(row['defense']),
                'sp_attack': int(row['sp_attack']),
                'sp_defense': int(row['sp_defense']),
                'speed': int(row['speed']),
                'total': int(row['total']),
                'type1': row['type1'],
                'type2': type2_val
            }
        
        type_adv_df = pd.read_csv(os.path.join(DATA_DIR, 'type_advantage.csv'))
        self.type_advantages = {}
        for _, row in type_adv_df.iterrows():
            self.type_advantages[(row['attacker'], row['defender'])] = int(row['advantage'])
    
    def get_type_advantage(self, attacker_type1, attacker_type2, defender_type1, defender_type2):
        total = 0
        
        if (attacker_type1, defender_type1) in self.type_advantages:
            total += self.type_advantages[(attacker_type1, defender_type1)]
        if defender_type2 and (attacker_type1, defender_type2) in self.type_advantages:
            total += self.type_advantages[(attacker_type1, defender_type2)]
        
        if attacker_type2:
            if (attacker_type2, defender_type1) in self.type_advantages:
                total += self.type_advantages[(attacker_type2, defender_type1)]
            if defender_type2 and (attacker_type2, defender_type2) in self.type_advantages:
                total += self.type_advantages[(attacker_type2, defender_type2)]
        
        if total > 0:
            return 1
        elif total < 0:
            return -1
        else:
            return 0
    
    def predict(self, pokemon1, pokemon2, weather='Clear', status_p1='None', 
                status_p2='None', terrain='None', hazards='None'):
        p1_stats = self.stats_dict[pokemon1]
        p2_stats = self.stats_dict[pokemon2]
        
        hp_diff = p1_stats['hp'] - p2_stats['hp']
        attack_diff = p1_stats['attack'] - p2_stats['attack']
        defense_diff = p1_stats['defense'] - p2_stats['defense']
        sp_attack_diff = p1_stats['sp_attack'] - p2_stats['sp_attack']
        sp_defense_diff = p1_stats['sp_defense'] - p2_stats['sp_defense']
        speed_diff = p1_stats['speed'] - p2_stats['speed']
        total_diff = p1_stats['total'] - p2_stats['total']
        
        type_advantage = self.get_type_advantage(
            p1_stats['type1'], p1_stats['type2'],
            p2_stats['type1'], p2_stats['type2']
        )
        
        features = {
            'p1_hp': p1_stats['hp'],
            'p1_attack': p1_stats['attack'],
            'p1_defense': p1_stats['defense'],
            'p1_sp_attack': p1_stats['sp_attack'],
            'p1_sp_defense': p1_stats['sp_defense'],
            'p1_speed': p1_stats['speed'],
            'p1_total': p1_stats['total'],
            'p2_hp': p2_stats['hp'],
            'p2_attack': p2_stats['attack'],
            'p2_defense': p2_stats['defense'],
            'p2_sp_attack': p2_stats['sp_attack'],
            'p2_sp_defense': p2_stats['sp_defense'],
            'p2_speed': p2_stats['speed'],
            'p2_total': p2_stats['total'],
            'hp_diff': hp_diff,
            'attack_diff': attack_diff,
            'defense_diff': defense_diff,
            'sp_attack_diff': sp_attack_diff,
            'sp_defense_diff': sp_defense_diff,
            'speed_diff': speed_diff,
            'total_diff': total_diff,
            'type_advantage': type_advantage,
            'weather': weather,
            'status_p1': status_p1,
            'status_p2': status_p2,
            'terrain': terrain,
            'hazards': hazards
        }
        
        feature_df = pd.DataFrame([features])
        
        for feature in ['weather', 'status_p1', 'status_p2', 'terrain', 'hazards']:
            le = self.label_encoders[feature]
            if features[feature] in le.classes_:
                feature_df[feature] = le.transform([features[feature]])[0]
            else:
                feature_df[feature] = 0
        
        feature_df = feature_df[self.feature_columns]
        
        prediction = self.model.predict(feature_df)[0]
        probabilities = self.model.predict_proba(feature_df)[0]
        
        return {
            'winner': 'pokemon1' if prediction == 1 else 'pokemon2',
            'winner_name': pokemon1 if prediction == 1 else pokemon2,
            'confidence': float(max(probabilities)),
            'probabilities': {
                'pokemon1': float(probabilities[1]),
                'pokemon2': float(probabilities[0])
            },
            'pokemon1': pokemon1,
            'pokemon2': pokemon2
        }

if __name__ == '__main__':
    predictor = PokemonBattlePredictor()
    result = predictor.predict('pikachu', 'squirtle', weather='Rain', status_p1='None', status_p2='None')
    print(result)

