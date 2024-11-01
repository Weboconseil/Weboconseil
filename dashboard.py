import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Configuration de la page avec cache
st.set_page_config(
    page_title="Tableau de Bord Financier",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Activation du cache pour les fonctions de données
@st.cache_data
def load_monthly_data():
    """Charge les données mensuelles avec mise en cache"""
    return pd.DataFrame({
        'Mois': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'],
        'CA': [1600, 1680, 1764, 1852, 1945, 2042, 2144, 2251, 2364, 2482, 2606, 2736],
        'Coûts': [1345.65, 1412.93, 1483.58, 1557.76, 1635.65, 1717.43, 1803.30, 1893.47, 1988.14, 2087.55, 2191.93, 2301.52],
        'Profit': [254.35, 267.07, 280.42, 294.24, 309.35, 324.57, 340.70, 357.53, 375.86, 394.45, 414.07, 434.48]
    })

@st.cache_data
def load_breakeven_data():
    """Charge les données du point mort avec mise en cache"""
    return pd.DataFrame({
        'Catégorie': ['Coûts fixes', 'Coûts variables', 'Marge'],
        'Montant': [6399, 9749, 3052]
    })

# Fonction pour formater les montants en euros
def format_euro(amount):
    """Formate un nombre en euros avec séparateurs appropriés"""
    try:
        return f"{float(amount):,.2f} €".replace(",", " ").replace(".", ",")
    except (ValueError, TypeError):
        return "0,00 €"

# Chargement des données
try:
    df_monthly = load_monthly_data()
    df_breakeven = load_breakeven_data()
except Exception as e:
    st.error(f"Erreur lors du chargement des données: {str(e)}")
    st.stop()

# Application du style CSS personnalisé
st.markdown("""
    <style>
    .stMetric .metric-label { font-size: 16px; font-weight: 600; }
    .stMetric .metric-value { font-size: 24px; font-weight: bold; }
    .stMetric .metric-delta { font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# Titre principal avec style
st.markdown("<h1 style='text-align: center;'>Tableau de Bord Financier</h1>", unsafe_allow_html=True)
st.markdown("---")

# KPIs en colonnes avec gestion d'erreurs
try:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Chiffre d'Affaires Annuel",
            value=format_euro(df_monthly['CA'].sum()),
            delta="+5.2%"
        )

    with col2:
        st.metric(
            label="Résultat Net",
            value=format_euro(df_monthly['Profit'].sum()),
            delta=f"{(df_monthly['Profit'].sum() / df_monthly['CA'].sum() * 100):.1f}%"
        )

    with col3:
        point_mort = df_breakeven['Montant'].iloc[0] / 12
        st.metric(
            label="Point Mort Mensuel",
            value=format_euro(point_mort),
            delta=f"{point_mort / (df_monthly['CA'].mean() / 30):.2f} jours"
        )
except Exception as e:
    st.error(f"Erreur lors du calcul des KPIs: {str(e)}")

st.markdown("---")

# Fonction pour créer le graphique CA vs Coûts
@st.cache_data
def create_revenue_chart(df):
    """Crée le graphique CA vs Coûts avec mise en cache"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Mois'],
        y=df['CA'],
        name="CA",
        line=dict(color="#2563eb", width=2)
    ))

    fig.add_trace(go.Scatter(
        x=df['Mois'],
        y=df['Coûts'],
        name="Coûts",
        line=dict(color="#dc2626", width=2)
    ))

    fig.update_layout(
        title="Évolution CA vs Coûts",
        xaxis_title="Mois",
        yaxis_title="Montant (€)",
        hovermode="x unified",
        height=500,
        template="plotly_white"
    )
    
    return fig

# Affichage des graphiques avec gestion d'erreurs
try:
    st.plotly_chart(create_revenue_chart(df_monthly), use_container_width=True)

    # Graphique Point Mort
    fig_breakeven = px.bar(
        df_breakeven,
        x='Catégorie',
        y='Montant',
        title="Analyse du Point Mort",
        color_discrete_sequence=["#3b82f6"],
        template="plotly_white"
    )

    fig_breakeven.update_layout(
        height=400,
        yaxis_title="Montant (€)"
    )

    st.plotly_chart(fig_breakeven, use_container_width=True)
except Exception as e:
    st.error(f"Erreur lors de la création des graphiques: {str(e)}")

# Tableau des détails avec gestion d'erreurs
try:
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
except Exception as e:
    st.error(f"Erreur lors de l'affichage du tableau: {str(e)}")

# Sidebar avec filtres
with st.sidebar:
    st.header("Paramètres")
    
    try:
        # Sélection de la période
        debut, fin = st.select_slider(
            "Période d'analyse",
            options=df_monthly['Mois'].tolist(),
            value=(df_monthly['Mois'].iloc[0], df_monthly['Mois'].iloc[-1])
        )

        # Métriques filtrées
        mask = (df_monthly['Mois'] >= debut) & (df_monthly['Mois'] <= fin)
        filtered_data = df_monthly[mask]

        st.markdown("### Métriques clés")
        st.info(f"Marge moyenne: {format_euro(filtered_data['Profit'].mean())}")
        st.info(f"CA moyen: {format_euro(filtered_data['CA'].mean())}")
        
        # Taux de croissance
        growth_rate = ((filtered_data['CA'].iloc[-1] / filtered_data['CA'].iloc[0]) - 1) * 100
        st.info(f"Taux de croissance: {growth_rate:.1f}%")
    except Exception as e:
        st.error(f"Erreur dans la sidebar: {str(e)}")

# Notes et analyses dans un expander
with st.expander("📝 Notes et Analyses"):
    st.markdown("""
    ### Points clés
    - La croissance du CA est stable et positive
    - Le point mort est atteint au bout de 8.1 mois
    - La marge nette moyenne est de 12.7%
    
    ### Recommandations
    1. Surveiller l'évolution des coûts variables
    2. Optimiser les coûts fixes pour améliorer la rentabilité
    3. Maintenir la trajectoire de croissance du CA
    """)
