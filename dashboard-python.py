import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Tableau de Bord Financier", layout="wide")

# Données mensuelles
monthly_data = {
    'Mois': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'],
    'CA': [1600, 1680, 1764, 1852, 1945, 2042, 2144, 2251, 2364, 2482, 2606, 2736],
    'Coûts': [1345.65, 1412.93, 1483.58, 1557.76, 1635.65, 1717.43, 1803.30, 1893.47, 1988.14, 2087.55, 2191.93, 2301.52],
    'Profit': [254.35, 267.07, 280.42, 294.24, 309.35, 324.57, 340.70, 357.53, 375.86, 394.45, 414.07, 434.48]
}

# Données du point mort
breakeven_data = {
    'Catégorie': ['Coûts fixes', 'Coûts variables', 'Marge'],
    'Montant': [6399, 9749, 3052]
}

# Création des DataFrames
df_monthly = pd.DataFrame(monthly_data)
df_breakeven = pd.DataFrame(breakeven_data)

# Fonction pour formater les montants en euros
def format_euro(amount):
    return f"{amount:,.2f} €".replace(",", " ").replace(".", ",")

# Titre principal
st.title("Tableau de Bord Financier")
st.markdown("---")

# KPIs en colonnes
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Chiffre d'Affaires Annuel",
        value=format_euro(sum(monthly_data['CA'])),
        delta="+5.2%"
    )

with col2:
    st.metric(
        label="Résultat Net",
        value=format_euro(2442),
        delta="12.7%"
    )

with col3:
    st.metric(
        label="Point Mort Mensuel",
        value=format_euro(1083),
        delta="13.54 commandes"
    )

st.markdown("---")

# Graphique CA vs Coûts
fig_revenue = go.Figure()

fig_revenue.add_trace(go.Scatter(
    x=df_monthly['Mois'],
    y=df_monthly['CA'],
    name="CA",
    line=dict(color="#2563eb", width=2)
))

fig_revenue.add_trace(go.Scatter(
    x=df_monthly['Mois'],
    y=df_monthly['Coûts'],
    name="Coûts",
    line=dict(color="#dc2626", width=2)
))

fig_revenue.update_layout(
    title="Évolution CA vs Coûts",
    xaxis_title="Mois",
    yaxis_title="Montant (€)",
    hovermode="x unified",
    height=500
)

st.plotly_chart(fig_revenue, use_container_width=True)

# Graphique Point Mort
fig_breakeven = px.bar(
    df_breakeven,
    x='Catégorie',
    y='Montant',
    title="Analyse du Point Mort",
    color_discrete_sequence=["#3b82f6"]
)

fig_breakeven.update_layout(
    height=400,
    yaxis_title="Montant (€)"
)

st.plotly_chart(fig_breakeven, use_container_width=True)

# Détails financiers en tableau
st.markdown("### Détails mensuels")
st.dataframe(
    df_monthly.style
    .format({
        'CA': format_euro,
        'Coûts': format_euro,
        'Profit': format_euro
    })
    .background_gradient(subset=['Profit'], cmap='RdYlGn'),
    use_container_width=True
)

# Ajout de filtres et contrôles interactifs
st.sidebar.header("Paramètres")

# Sélection de la période
periode = st.sidebar.select_slider(
    "Période d'analyse",
    options=monthly_data['Mois'],
    value=('Jan', 'Déc')
)

# Affichage des métriques supplémentaires
st.sidebar.markdown("### Métriques clés")
st.sidebar.info(f"Marge moyenne: {format_euro(df_monthly['Profit'].mean())}")
st.sidebar.info(f"CA moyen: {format_euro(df_monthly['CA'].mean())}")

# Notes et commentaires
with st.expander("📝 Notes et Analyses"):
    st.markdown("""
    - La croissance du CA est stable et positive
    - Le point mort est atteint au bout de 8.1 mois
    - La marge nette moyenne est de 12.7%
    """)
