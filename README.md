# Fiches d'évaluation individuelles - Physique

Ce projet permet de générer des fiches d'évaluation pour chaque élève à partir de notes Excel, d'absences et de remarques, avec synthèse automatique et prévision de moyenne.

## Structure du projet

- `data/notes.xlsx` : Fichier source des notes (à fournir)
- `data/absences.json` : Absences enregistrées
- `data/remarques.json` : Remarques enregistrées
- `app.py` : Interface Streamlit
- `evaluation.py` : Fonctions métier
- `llm_utils.py` : Synthèse des remarques via LLM

## Installation

```sh
pip install -r requirements.txt
```

## Lancement

```sh
streamlit run app.py
```

## Fonctionnalités
- Import des notes Excel
- Saisie absences/remarques
- Fiche élève complète : notes, absences, remarques, synthèse, prévision
- Visualisation interactive (radar, tables)
- Export PDF

## Déploiement sur Streamlit Community Cloud

1. **Préparez votre dépôt GitHub** :
   - Incluez tous les fichiers Python (`app.py`, `evaluation.py`, etc.), `requirements.txt` et ce `README.md`.
   - Ajoutez des fichiers Excel de démo anonymisés dans `data/` si besoin.
   - Ne versionnez pas de données sensibles ou personnelles (voir `.gitignore`).
2. **Rendez-vous sur https://streamlit.io/cloud** et connectez votre compte GitHub.
3. **Créez une nouvelle app** en sélectionnant ce dépôt et le fichier `app.py`.
4. **Déployez** : l'application est accessible partout via un lien web.

### Conseils pour les fichiers de données
- Les fichiers Excel (`notes.xlsx`, `élèves_2024-2025.xlsx`) doivent être présents dans le dossier `data/` pour la démo.
- Pour un usage réel, ajoutez une fonctionnalité d'upload dans l'interface Streamlit pour charger vos propres fichiers.

### Structure recommandée du dépôt

```
/ (racine)
├── app.py
├── evaluation.py
├── llm_utils.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    ├── notes.xlsx
    ├── élèves_2024-2025.xlsx
    ├── absences.json
    └── remarques.json
```

---

Pour toute question ou contribution, ouvrez une issue ou une pull request sur GitHub.
