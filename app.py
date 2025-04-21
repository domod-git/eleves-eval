import streamlit as st
import pandas as pd
import os
from evaluation import get_student_report, add_absence, add_remarque
import json
import plotly.graph_objects as go
from llm_utils import get_simulated_scores_competences, get_simulated_scores_savoir_etre, get_ai_scores_competences, get_ai_scores_savoir_etre

st.title("Fiches d'évaluation - Physique")

# Contrôle fichiers et colonnes obligatoires
import pathlib
err = False
# Contrôle élèves
eleves_path = pathlib.Path('data/élèves_2024-2025.xlsx')
if not eleves_path.exists():
    st.warning("Veuillez placer un fichier élèves_2024-2025.xlsx dans le dossier data/.")
    err = True
else:
    try:
        eleves_df = pd.read_excel(eleves_path)
        eleves_df.columns = [col.strip() for col in eleves_df.columns]
        if not all(col in eleves_df.columns for col in ['Prénom','Nom']):
            st.warning("Le fichier élèves_2024-2025.xlsx doit contenir les colonnes 'Prénom' et 'Nom'.")
            err = True
        else:
            if 'Classe' in eleves_df.columns:
                eleves = [f"{row['Prénom']} {row['Nom']} – {row['Classe']}" for _, row in eleves_df.iterrows()]
            else:
                eleves = [f"{row['Prénom']} {row['Nom']}" for _, row in eleves_df.iterrows()]
            eleves = [''] + eleves
    except Exception as e:
        st.warning(f"Erreur lors de la lecture de élèves_2024-2025.xlsx : {e}")
        err = True
# Contrôle notes
notes_path = pathlib.Path('data/notes.xlsx')
if not notes_path.exists():
    st.warning("Veuillez placer un fichier notes.xlsx dans le dossier data/.")
    err = True
else:
    try:
        notes_df = pd.read_excel(notes_path)
        notes_df.columns = [col.strip() for col in notes_df.columns]
        if 'Nom' not in notes_df.columns:
            st.warning("Le fichier notes.xlsx doit contenir la colonne 'Nom'.")
            err = True
    except Exception as e:
        st.warning(f"Erreur lors de la lecture de notes.xlsx : {e}")
        err = True
# Si erreur, bloquer la suite
if err:
    st.stop()

eleve = st.selectbox("", eleves)

# Saisie absences (déplacé en haut)
with st.form("absence_form"):
    st.subheader("Absence")
    abs_date = st.date_input("Date")
    abs_type = st.selectbox("Type d'absence", ["Retard", "Évaluation", "Autre"])
    abs_duree = st.number_input("Durée (minutes)", min_value=0, max_value=240, value=0)
    abs_submit = st.form_submit_button("Ajouter absence")
    if abs_submit and eleve:
        add_absence(eleve, abs_date, abs_type, abs_duree)
        st.success("Absence ajoutée.")

# Affichage absences juste après le formulaire
if eleve:
    fiche = get_student_report(eleve)
    st.markdown("**Absences (total par type) :**")
    st.table([{k:v} for k,v in fiche['Absences'].items()])

# Saisie remarques (déplacé en haut)
with st.form("remarque_form"):
    st.subheader("Remarque")
    rem_date = st.date_input("Date remarque")
    domaines = [
        "Compréhension des concepts",
        "Résolution de problèmes",
        "Outils mathématiques",
        "Compétences expérimentales",
        "Autonomie",
        "Assiduité",
        "Participation",
        "Organisation",
        "Comportement",
        "Autre"
    ]
    rem_domaine = st.selectbox("Domaine", domaines)
    rem_text = st.text_area("Remarque")
    rem_submit = st.form_submit_button("Ajouter remarque")
    if rem_submit and eleve:
        add_remarque(eleve, rem_date, rem_domaine, rem_text)
        st.success("Remarque ajoutée.")

if eleve:
    fiche = get_student_report(eleve)
    # MESURES PARTICULIERES (affichage, édition, suppression)

    if fiche['Notes'] is None:
        st.info("Aucune note saisie pour cet élève pour le moment.")
    else:
        st.markdown("**Notes :**")
        notes = fiche['Notes']
        cols = st.columns(len(notes))
        for i, (k, v) in enumerate(notes.items()):
            label = k.replace('Note', 'TE')
            with cols[i]:
                st.markdown(f"**{label}**")
                if isinstance(v, (int, float)):
                    st.markdown(f"{round(v,1)}")
                else:
                    st.markdown(str(v))
        if fiche['Moyenne actuelle'] is not None:
            st.markdown(f"**Moyenne actuelle :** :blue[{fiche['Moyenne actuelle']}]")
        else:
            st.info("Aucune moyenne calculée pour cet élève pour le moment.")
        st.markdown(f"**Prévision de la moyenne finale :** :orange[{fiche['Prévision moyenne finale']}]")

    # --- RADAR COMPETENCES DISCIPLINAIRES ---
    st.markdown("### Compétences disciplinaires")
    remarques_path = os.path.join("data", "remarques.json")
    if os.path.exists(remarques_path):
        with open(remarques_path, "r", encoding="utf-8") as f:
            all_remarques = json.load(f)
        rem_eleve = [r for r in all_remarques if r['nom']==eleve]
    else:
        rem_eleve = []
    # Utilise l'IA si remarques disponibles, sinon scores simulés
    if rem_eleve:
        scores_comp = get_ai_scores_competences(eleve, rem_eleve)
    else:
        scores_comp = get_simulated_scores_competences()
    categories_comp = list(scores_comp.keys())
    values_comp = list(scores_comp.values())
    values_comp += values_comp[:1]  # Boucle pour le radar
    categories_comp += categories_comp[:1]
    fig_comp = go.Figure(
        data=[go.Scatterpolar(r=values_comp, theta=categories_comp, fill='toself', name='Compétences',
                              fillcolor='rgba(44, 160, 44, 0.5)', line=dict(color='green', width=3), marker=dict(color='green', size=8))],
        layout=go.Layout(
            polar=dict(radialaxis=dict(visible=True, range=[1,6], color='#222', gridcolor='#888', linecolor='#222'),
                        angularaxis=dict(color='#222', gridcolor='#888', linecolor='#222')),
            showlegend=False,
            paper_bgcolor='#fff',
            plot_bgcolor='#fff',
        )
    )
    st.plotly_chart(fig_comp, use_container_width=True)
    # --- RADAR SAVOIR-ETRE & ATTITUDE ---
    st.markdown("### Savoir-être et attitude face au travail")
    if rem_eleve:
        scores_se = get_ai_scores_savoir_etre(eleve, rem_eleve)
    else:
        scores_se = get_simulated_scores_savoir_etre()
    categories_se = list(scores_se.keys())
    values_se = list(scores_se.values())
    values_se += values_se[:1]
    categories_se += categories_se[:1]
    fig_se = go.Figure(
        data=[go.Scatterpolar(r=values_se, theta=categories_se, fill='toself', name='Savoir-être',
                              fillcolor='rgba(31, 119, 180, 0.5)', line=dict(color='blue', width=3), marker=dict(color='blue', size=8))],
        layout=go.Layout(
            polar=dict(radialaxis=dict(visible=True, range=[1,6], color='#222', gridcolor='#888', linecolor='#222'),
                        angularaxis=dict(color='#222', gridcolor='#888', linecolor='#222')),
            showlegend=False,
            paper_bgcolor='#fff',
            plot_bgcolor='#fff',
        )
    )
    st.plotly_chart(fig_se, use_container_width=True)
    # --- MESURES PARTICULIÈRES (affichage, édition, suppression) ---
    st.markdown("---")
    st.markdown("### Mesures particulières")
    mesures_path = os.path.join("data", "mesures.json")
    if not os.path.exists(mesures_path):
        mesures = []
    else:
        with open(mesures_path, "r", encoding="utf-8") as f:
            mesures = json.load(f)
    mesures_eleve = next((m['mesures'] for m in mesures if m['nom'] == eleve), "")
    # Suggestions courtes
    suggestions = [
        "Dyslexie",
        "Dyscalculie",
        "Temps supplémentaire",
        "Outils numériques"
    ]
    mesures_sel = []
    cols = st.columns(2)
    for i, s in enumerate(suggestions):
        if cols[i%2].checkbox(s, value=(s in mesures_eleve)):
            mesures_sel.append(s)
    autres_mesures = st.text_area(
        "Autres mesures particulières (compléments ou précisions)",
        value=mesures_eleve if mesures_eleve not in suggestions else "",
        key=f"mesures_{eleve}"
    )
    all_mesures = ", ".join(mesures_sel + ([autres_mesures] if autres_mesures.strip() else []))
    col_save, col_del = st.columns([2,1])
    if col_save.button("Enregistrer les mesures"):
        found = False
        for m in mesures:
            if m['nom'] == eleve:
                m['mesures'] = all_mesures
                found = True
        if not found:
            mesures.append({'nom': eleve, 'mesures': all_mesures})
        with open(mesures_path, "w", encoding="utf-8") as f:
            json.dump(mesures, f, ensure_ascii=False, indent=2)
        st.success("Mesures particulières enregistrées.")
    if col_del.button("Supprimer les mesures"):
        mesures = [m for m in mesures if m['nom'] != eleve]
        with open(mesures_path, "w", encoding="utf-8") as f:
            json.dump(mesures, f, ensure_ascii=False, indent=2)
        st.success("Mesures particulières supprimées.")
        mesures_eleve = ""
        all_mesures = ""
    if all_mesures:
        st.info(all_mesures)
    st.markdown("---")

    # Synthèse des remarques juste avant PDF
    prenom = eleve.split()[0] if eleve else "l'élève"
    synthese = fiche['Synthèse remarques'].replace("[Nom de l'élève]", prenom)
    import re
    synthese = re.sub(r'\b[Ii]l\b|\b[Ee]lle\b', "l'élève", synthese)
    synthese = re.sub(r"qu[’']l'élève", f"que {prenom}", synthese)
    st.markdown("**Synthèse des remarques :**")
    st.info(synthese)
    st.markdown(f"**Prévision de la moyenne finale :** :orange[{fiche['Prévision moyenne finale']}]")

    # Choix des rubriques à exporter
    st.markdown("**Rubriques à exporter en PDF :**")
    exp_mesures = st.checkbox("Mesures particulières", value=True)
    exp_notes = st.checkbox("Notes et moyenne", value=True)
    exp_abs = st.checkbox("Absences", value=True)
    exp_rem = st.checkbox("Synthèse des remarques", value=True)
    exp_prev = st.checkbox("Prévision de la moyenne finale", value=True)
    # Export PDF
    if st.button("Exporter la fiche PDF"):
        from export_pdf import export_student_pdf
        pdf_path = export_student_pdf(
            eleve,
            export_mesures=exp_mesures,
            export_notes=exp_notes,
            export_absences=exp_abs,
            export_remarques=exp_rem,
            export_prevision=exp_prev
        )
        with open(pdf_path, "rb") as f:
            st.download_button("Télécharger le PDF", f, file_name=os.path.basename(pdf_path), mime="application/pdf")


# Liste et suppression des remarques
remarques_path = os.path.join("data", "remarques.json")
if os.path.exists(remarques_path):
    with open(remarques_path, "r", encoding="utf-8") as f:
        remarques = json.load(f)
    rem_eleve = [r for r in remarques if r['nom']==eleve]
    if rem_eleve:
        st.markdown("**Remarques enregistrées :**")
        for i, r in enumerate(rem_eleve):
            col1, col2, col3 = st.columns([2,2,6])
            col1.write(r['date'])
            col2.write(r['domaine'])
            col3.write(r['texte'])
            # Affichage des boutons SOUS la remarque, centrés et sur une seule ligne
            # CSS pour forcer largeur, taille et empêcher retour à la ligne sur les boutons
            st.markdown(f"""
            <style>
            div[data-testid='stHorizontalBlock'] button[data-testid^='baseButton'] {{
                min-width: 120px !important;
                max-width: 140px !important;
                font-size: 1.1em;
                white-space: nowrap;
            }}
            </style>
            """, unsafe_allow_html=True)
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([3,1,1,3])
            with btn_col2:
                if st.button("Suppr.", key=f"delrem_{i}"):
                    remarques.remove(r)
                    with open(remarques_path, "w", encoding="utf-8") as f:
                        json.dump(remarques, f, ensure_ascii=False, indent=2)
                    st.success("Remarque supprimée.")
                    st.rerun()
            with btn_col3:
                if st.button("Modif.", key=f"editrem_{i}"):
                    st.session_state[f"edit_{i}"] = True
            if st.session_state.get(f"edit_{i}"):
                new_nom = st.text_input("Nom", value=r['nom'], key=f"edit_nom_{i}")
                new_date = st.text_input("Date", value=r['date'], key=f"edit_date_{i}")
                new_domaine = st.text_input("Domaine", value=r['domaine'], key=f"edit_dom_{i}")
                new_texte = st.text_area("Remarque", value=r['texte'], key=f"edit_txt_{i}")
                if st.button("Enregistrer", key=f"saveedit_{i}"):
                    r['nom'] = new_nom
                    r['date'] = new_date
                    r['domaine'] = new_domaine
                    r['texte'] = new_texte
                    with open(remarques_path, "w", encoding="utf-8") as f:
                        json.dump(remarques, f, ensure_ascii=False, indent=2)
                    st.success("Remarque modifiée.")
                    st.session_state[f"edit_{i}"] = False
                    st.rerun()
                if st.button("Annuler", key=f"canceledit_{i}"):
                    st.session_state[f"edit_{i}"] = False
                    st.rerun()
