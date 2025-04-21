import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
import random

def synthesize_remarks(remarques):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Clé API Gemini manquante."
    if not remarques:
        return "Aucune remarque."
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = (
        "Voici des remarques d'évaluation d'un élève en physique. "
        "Rédige une synthèse professionnelle, concise et bienveillante à destination des parents :\n\n"
    )
    for r in remarques:
        prompt += f"- [{r['date']}] ({r['domaine']}) : {r['texte']}\n"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Erreur Gemini : {e}"

def get_simulated_scores_competences():
    """Retourne des scores simulés (1 à 6) pour les compétences disciplinaires."""
    categories = [
        "Compréhension des concepts",
        "Résolution de problèmes",
        "Outils mathématiques",
        "Compétences expérimentales"
    ]
    return {cat: random.randint(1, 6) for cat in categories}

def get_simulated_scores_savoir_etre():
    """Retourne des scores simulés (1 à 6) pour le savoir-être et l'attitude."""
    categories = [
        "Autonomie",
        "Assiduité",
        "Participation",
        "Organisation",
        "Comportement"
    ]
    return {cat: random.randint(1, 6) for cat in categories}

import json as _json

def get_ai_scores_competences(nom, remarques):
    """
    Utilise Gemini pour générer des scores (1 à 6) pour les compétences disciplinaires à partir des remarques de l'élève.
    Retourne un dict {cat: score}
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {cat: 0 for cat in [
            "Compréhension des concepts",
            "Résolution de problèmes",
            "Outils mathématiques",
            "Compétences expérimentales"
        ]}
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = (
        f"Voici des remarques d'évaluation pour l'élève {nom} en physique. "
        "Attribue une note de 1 (faible) à 6 (excellent) pour chacune des compétences suivantes, uniquement sous forme de JSON :\n"
        "{\n"
        "  'Compréhension des concepts': <score>,\n"
        "  'Résolution de problèmes': <score>,\n"
        "  'Outils mathématiques': <score>,\n"
        "  'Compétences expérimentales': <score>\n"
        "}\n"
        "N'ajoute aucun commentaire.\n"
    )
    for r in remarques:
        prompt += f"- [{r['date']}] ({r['domaine']}) : {r['texte']}\n"
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Extraction du JSON
        json_str = text[text.find('{'):text.rfind('}')+1]
        return _json.loads(json_str.replace("'", '"'))
    except Exception as e:
        return {cat: 0 for cat in [
            "Compréhension des concepts",
            "Résolution de problèmes",
            "Outils mathématiques",
            "Compétences expérimentales"
        ]}

def get_ai_scores_savoir_etre(nom, remarques):
    """
    Utilise Gemini pour générer des scores (1 à 6) pour le savoir-être à partir des remarques de l'élève.
    Retourne un dict {cat: score}
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {cat: 0 for cat in [
            "Autonomie",
            "Assiduité",
            "Participation",
            "Organisation",
            "Comportement"
        ]}
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = (
        f"Voici des remarques d'évaluation pour l'élève {nom} en physique. "
        "Attribue une note de 1 (faible) à 6 (excellent) pour chacune des attitudes suivantes, uniquement sous forme de JSON :\n"
        "{\n"
        "  'Autonomie': <score>,\n"
        "  'Assiduité': <score>,\n"
        "  'Participation': <score>,\n"
        "  'Organisation': <score>,\n"
        "  'Comportement': <score>\n"
        "}\n"
        "N'ajoute aucun commentaire.\n"
    )
    for r in remarques:
        prompt += f"- [{r['date']}] ({r['domaine']}) : {r['texte']}\n"
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        json_str = text[text.find('{'):text.rfind('}')+1]
        return _json.loads(json_str.replace("'", '"'))
    except Exception as e:
        return {cat: 0 for cat in [
            "Autonomie",
            "Assiduité",
            "Participation",
            "Organisation",
            "Comportement"
        ]}
