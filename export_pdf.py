import pdfkit
import os
from evaluation import get_student_report

def export_student_pdf(
    nom,
    output_dir="exports",
    export_mesures=True,
    export_notes=True,
    export_absences=True,
    export_remarques=True,
    export_prevision=True,
    export_radar=True
):
    fiche = get_student_report(nom)
    # Charger les mesures particulières
    mesures_path = os.path.join("data", "mesures.json")
    mesures = []
    if os.path.exists(mesures_path):
        import json
        with open(mesures_path, "r", encoding="utf-8") as f:
            mesures = json.load(f)
    mesures_eleve = next((m['mesures'] for m in mesures if m['nom'] == nom), "")
    # Construction HTML dynamique
    html = f"""
    <html><head><meta charset='utf-8'><style>
    body {{ font-family: Arial, sans-serif; }}
    h2 {{ color: #2e6c80; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 6px; }}
    th {{ background: #f2f2f2; }}
    img.radar {{ display: block; margin: 20px auto; max-width: 350px; }}
    </style></head><body>
    <h2>Fiche d'évaluation - {fiche['Nom']}</h2>
    """
    # Ajout radar compétences disciplinaires
    if export_radar:
        import base64
        import io
        from llm_utils import get_simulated_scores_competences, get_simulated_scores_savoir_etre
        import plotly.graph_objects as go
        # Radar compétences
        scores_comp = get_simulated_scores_competences()
        categories_comp = list(scores_comp.keys())
        values_comp = list(scores_comp.values())
        values_comp += values_comp[:1]
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
        buf = io.BytesIO()
        fig_comp.write_image(buf, format='png')
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        html += f'<h3>Compétences disciplinaires</h3><img class="radar" src="data:image/png;base64,{img_b64}"/>'
        # Radar savoir-être
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
        buf = io.BytesIO()
        fig_se.write_image(buf, format='png')
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        html += f'<h3>Savoir-être et attitude face au travail</h3><img class="radar" src="data:image/png;base64,{img_b64}"/>'
    if export_mesures and mesures_eleve:
        html += f"<h3>Mesures particulières</h3><p>{mesures_eleve}</p>"
    if export_notes:
        html += "<h3>Notes</h3>"
        html += "<table><tr><th>Épreuve</th><th>Note</th></tr>"
        html += ''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in fiche['Notes'].items())
        html += "</table>"
        html += f"<p><b>Moyenne actuelle :</b> {fiche['Moyenne actuelle']}</p>"
    if export_absences:
        html += "<h3>Absences</h3>"
        html += "<table><tr><th>Type</th><th>Total</th></tr>"
        html += ''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in fiche['Absences'].items())
        html += "</table>"
    if export_remarques:
        html += f"<h3>Synthèse des remarques</h3><p>{fiche['Synthèse remarques']}</p>"
    if export_prevision:
        html += f"<h3>Prévision de la moyenne finale</h3><p>{fiche['Prévision moyenne finale']}</p>"
    html += "</body></html>"
    pdf_path = os.path.join(output_dir, f"{fiche['Nom'].replace(' ', '_')}.pdf")
    config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdfkit.from_string(html, pdf_path, configuration=config)
    return pdf_path
