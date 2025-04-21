import json
import pandas as pd
from llm_utils import synthesize_remarks
from sklearn.linear_model import LinearRegression
import numpy as np
import os

def get_student_report(prenom_nom_classe):
    notes_df = pd.read_excel('data/notes.xlsx')
    notes_df.columns = [col.strip() for col in notes_df.columns]
    # Extraire Prénom, Nom depuis 'Prénom Nom – Classe' ou 'Prénom Nom'
    if '–' in prenom_nom_classe:
        prenom_nom = prenom_nom_classe.split('–')[0].strip()
    else:
        prenom_nom = prenom_nom_classe.strip()
    if ' ' in prenom_nom:
        prenom, nom = prenom_nom.split(' ', 1)
    else:
        prenom, nom = '', prenom_nom
    notes_df['Nom'] = notes_df['Nom'].astype(str).str.strip()
    notes_df['Prénom'] = notes_df['Prénom'].astype(str).str.strip()
    match = notes_df[(notes_df['Nom'] == nom) & (notes_df['Prénom'] == prenom)]
    absences = load_json('data/absences.json')
    remarques = load_json('data/remarques.json')
    if match.empty:
        notes = None
        moy = None
    else:
        notes = match.iloc[0].to_dict()
        moy = np.mean([v for k,v in notes.items() if k != 'Nom' and isinstance(v, (int, float))])
    abs_eleve = [a for a in absences if a['nom']==nom]
    rem_eleve = [r for r in remarques if r['nom']==nom]
    abs_synth = synth_absences(abs_eleve)
    synth_rem = synthesize_remarks(rem_eleve)
    pred = predict_moyenne(notes_df, nom)
    if notes is None:
        return {
            'Nom': nom,
            'Notes': None,
            'Moyenne actuelle': None,
            'Absences': abs_synth,
            'Synthèse remarques': synth_rem,
            'Prévision moyenne finale': None
        }
    else:
        return {
            'Nom': nom,
            'Notes': {k:v for k,v in notes.items() if k != 'Nom'},
            'Moyenne actuelle': round(moy,2),
            'Absences': abs_synth,
            'Synthèse remarques': synth_rem,
            'Prévision moyenne finale': pred
        }

def add_absence(nom, date, typ, duree):
    absences = load_json('data/absences.json')
    absences.append({'nom': nom, 'date': str(date), 'type': typ, 'duree': duree})
    save_json('data/absences.json', absences)

def add_remarque(nom, date, domaine, texte):
    remarques = load_json('data/remarques.json')
    remarques.append({'nom': nom, 'date': str(date), 'domaine': domaine, 'texte': texte})
    save_json('data/remarques.json', remarques)

def synth_absences(abs_liste):
    from collections import Counter
    c = Counter([a['type'] for a in abs_liste])
    return dict(c)

def predict_moyenne(notes_df, nom):
    # Simple régression sur les moyennes des autres élèves
    try:
        X = np.arange(len(notes_df)).reshape(-1,1)
        y = notes_df.drop('Nom', axis=1).mean(axis=1)
        model = LinearRegression().fit(X, y)
        idx = notes_df[notes_df['Nom']==nom].index[0]
        pred = model.predict(np.array([[idx+5]]))  # projection future
        return round(float(pred[0]),2)
    except Exception:
        return None

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
