import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from Main import run_analysis
from Notifier import EmailNotifier
from SMSNotifier import SMSNotifier
from Database import DatabaseManager

# --- INITIALISATION & CONFIGURATION DE HAUT NIVEAU ---
st.set_page_config(
    page_title="Argus IA | Stratégie de Marché C2",
    layout="wide",
    page_icon="🦅"
)

db = DatabaseManager()
# sms_bot = SMSNotifier() # Désactivé pour le frontend
# email_bot = EmailNotifier() # Désactivé pour le frontend

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=60) # Cache de 1 min pour les perfs
def load_full_data():
    try:
        conn = sqlite3.connect("argus_project.db")
        # On récupère tout
        df = pd.read_sql("SELECT * FROM price_history ORDER BY timestamp DESC", conn)
        # On récupère les targets pour afficher le seuil dans le graphique
        df_targets = pd.read_sql("SELECT name, target_price FROM targets", conn)
        conn.close()
        
        # Merge pour avoir le prix cible dans le même DF pour plotly
        df = df.merge(df_targets, left_on='product_name', right_on='name', how='left')
        return df
    except Exception:
        return pd.DataFrame()

def load_targets():
    try:
        conn = sqlite3.connect("argus_project.db")
        df = pd.read_sql("SELECT name, target_price, sites FROM targets", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# --- STYLE CSS AVANCÉ (Visibilité & Hiérarchie) ---
st.markdown("""
    <style>
    /* 1. Global & Fond */
    .stApp { background-color: #0b0e14; color: #f0f2f6; }
    h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    
    /* 2. Style des Blocs de KPI (Haut de page) */
    [data-testid="stMetric"] {
        background-color: #171c26;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d3748;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] { color: #00ffcc !important; font-size: 2.2rem !important; }
    [data-testid="stMetricLabel"] { color: #a0aec0 !important; font-size: 1rem !important;}

    /* 3. Blocs de Configuration (Barre latérale et Cibles) */
    [data-testid="stSidebar"] { background-color: #11151c; border-right: 1px solid #2d3748; }
    [data-testid="stExpander"], div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] > div.stContainer {
        background-color: #171c26;
        border-radius: 12px;
        border: 1px solid #2d3748;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* 4. Tableau & Dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        border: 1px solid #2d3748;
    }
    [data-testid="stTable"] td { color: #f0f2f6 !important; }

    /* 5. Éléments Interactifs (Boutons, Inputs) */
    .stButton>button {
        background-color: #00ffcc;
        color: #0b0e14;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #00cccc; border: none; }
    
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] {
        background-color: #242c3d !important;
        color: #ffffff !important;
        border: 1px solid #4a5568 !important;
        border-radius: 8px;
    }
    
    /* 6. Verdict Tags (Couleurs IA) */
    .tag-deal { background-color: #065f46; color: #a7f3d0; padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;}
    .tag-wait { background-color: #7c2d12; color: #ffedd5; padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;}
    .tag-na { background-color: #3f3f46; color: #d1d5db; padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;}

    </style>
    """, unsafe_allow_html=True)

# --- HEADER & TITRE MAJESTUEUX ---
col_head1, col_head2 = st.columns([1, 10])
with col_head1:
    st.image("https://img.icons8.com/?size=100&id=121175&format=png&color=00ffcc", width=80) # Icone Eagle Pro
with col_head2:
    st.title("Argus IA : Poste de Commandement C2")
    st.caption("鷹 (Argus) - Système autonome de surveillance et de décision prédictive sur les marchés")

st.divider()
# --- CORPS PRINCIPAL (STRUCTURE TOUJOURS ACTIVE) ---
data = load_full_data()
targets_df = load_targets()

# 1. SECTION KPI (Observatoire Macro)
# -------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    # Valeur par défaut si data est vide
    last_sync = str(data['timestamp'].iloc[0])[11:19] if not data.empty else "--:--:--"
    st.metric("📡 Dernière Synchronisation", last_sync)
with k2:
    st.metric("🎯 Cibles Actives", len(targets_df))
with k3:
    # Calcul sécurisé du deal
    best_val = "0€"
    if not data.empty and 'target_price' in data.columns:
        data['deal_delta'] = data['target_price'] - data['price']
        if data['deal_delta'].max() > 0:
            best_val = f"+{data['deal_delta'].max():.2f}€"
    st.metric("🏆 Meilleure Opportunité", best_val)
with k4:
    st.metric("🧠 Santé de la Veille", "Opérationnelle ✅")

st.divider()

# 2. SECTION ANALYTIQUE ET CONTRÔLE
# -------------------------------------------------------------------
col_vis, col_ctrl = st.columns([3, 1])

# --- Colonne VISUALISATION (Gauche) ---
with col_vis:
    tab_graph, tab_hist = st.tabs(["📈 Tendances Temporelles", "🔍 Historique Complet"])
    
    with tab_graph:
        if not data.empty:
            all_prods = data['product_name'].unique()
            selected_prod = st.selectbox("Sélectionner un produit", options=all_prods)
            filtered_df = data[data['product_name'] == selected_prod]
            
            fig = px.line(filtered_df, x='timestamp', y=['price', 'target_price'],
                         template="plotly_dark", color_discrete_sequence=['#00ffcc', '#ff4b4b'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Affichage d'un graphique vide élégant
            st.info("📊 Les graphiques apparaîtront ici dès le premier scan.")
            st.image("https://img.icons8.com/?size=100&id=103328&format=png&color=2d3748", width=100)

    with tab_hist:
        if not data.empty:
            st.dataframe(data[['timestamp', 'product_name', 'price', 'verdict']], use_container_width=True)
        else:
            st.warning("Journal vide : Aucun historique détecté.")

# --- Colonne CONTRÔLE (Droite) ---
with col_ctrl:
    st.subheader("🎮 Commandes")
    if st.button("🚀 Lancer Scan IA", use_container_width=True):
        with st.spinner("Analyse..."):
            run_analysis()
        st.rerun()

    st.divider()
    
    # Formulaire d'ajout toujours présent
    with st.expander("🎯 Nouvelle Cible", expanded=True):
        n_name = st.text_input("Produit", key="fast_name")
        n_price = st.number_input("Prix d'alerte", min_value=0.0, key="fast_price")
        if st.button("Activer la veille", use_container_width=True):
            if n_name and n_price > 0:
                db.add_target(n_name, n_price, "Amazon,eBay")
                st.success("Cible engagée")
                st.rerun()
