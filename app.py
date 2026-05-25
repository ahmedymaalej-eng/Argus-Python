import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from Main import run_analysis
from Database import DatabaseManager

# --- INITIALISATION & CONFIGURATION DE HAUT NIVEAU ---
st.set_page_config(
    page_title="Argus IA | Stratégie de Marché C2",
    layout="wide",
    page_icon="🦅"
)

# Initialisation du gestionnaire de base de données
db = DatabaseManager()

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=60) # Cache de 1 min pour optimiser les performances
def load_full_data():
    try:
        # Correction : Utilisation du nom de fichier exact "argus-project.db"
        conn = sqlite3.connect("argus_project.db")
        df = pd.read_sql("SELECT * FROM price_history ORDER BY timestamp DESC", conn)
        df_targets = pd.read_sql("SELECT name, target_price FROM targets", conn)
        conn.close()
        
        # Fusion pour corréler le prix actuel et le prix cible dans Plotly
        if not df.empty and not df_targets.empty:
            df = df.merge(df_targets, left_on='product_name', right_on='name', how='left')
        return df
    except Exception as e:
        return pd.DataFrame()

def load_targets():
    try:
        # CORRECTION CRUCIALE : Remplacement de "_" par "-" pour la cohérence
        conn = sqlite3.connect("argus-project.db")
        df = pd.read_sql("SELECT name, target_price, sites FROM targets", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

# --- STYLE CSS AVANCÉ (Interface Sombre & Professionnelle) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #f0f2f6; }
    h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    
    [data-testid="stMetric"] {
        background-color: #171c26;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d3748;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] { color: #00ffcc !important; font-size: 2.2rem !important; }
    [data-testid="stMetricLabel"] { color: #a0aec0 !important; font-size: 1rem !important;}

    [data-testid="stSidebar"] { background-color: #11151c; border-right: 1px solid #2d3748; }
    
    .stButton>button {
        background-color: #00ffcc;
        color: #0b0e14;     
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #00cccc; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & TITRE ---
col_head1, col_head2 = st.columns([1, 10])
with col_head1:
    st.image("https://img.icons8.com/?size=100&id=121175&format=png&color=00ffcc", width=80)
with col_head2:
    st.title("Argus IA : Poste de Commandement C2")
    st.caption("鷹 (Argus) - Système autonome de surveillance et de décision prédictive")

st.divider()

# --- CORPS PRINCIPAL ---
data = load_full_data()
targets_df = load_targets()

# 1. SECTION KPI
k1, k2, k3, k4 = st.columns(4)
with k1:
    last_sync = str(data['timestamp'].iloc[0])[11:19] if not data.empty else "--:--:--"
    st.metric("📡 Dernière Synchronisation", last_sync)
with k2:
    st.metric("🎯 Cibles Actives", len(targets_df))
with k3:
    best_val = "0€"
    if not data.empty and 'target_price' in data.columns:
        # Correction du nom de colonne pour correspondre au DataFrame (prix -> price)
        data['deal_delta'] = data['target_price'] - data['price']
        if data['deal_delta'].max() > 0:
            best_val = f"+{data['deal_delta'].max():.2f}€"
    st.metric("🏆 Meilleure Opportunité", best_val)
with k4:
    st.metric("🧠 Santé de la Veille", "Opérationnelle ✅")

st.divider()

# 2. SECTION ANALYTIQUE
col_vis, col_ctrl = st.columns([3, 1])

with col_vis:
    tab_graph, tab_hist = st.tabs(["📈 Tendances Temporelles", "🔍 Historique Complet"])
    
    with tab_graph:
        if not data.empty:
            all_prods = data['product_name'].unique()
            selected_prod = st.selectbox("Sélectionner un produit", options=all_prods)
            filtered_df = data[data['product_name'] == selected_prod].sort_values('timestamp')
            
            fig = px.line(filtered_df, x='timestamp', y=['price', 'target_price'],
                         title=f"Évolution pour {selected_prod}",
                         template="plotly_dark", color_discrete_sequence=['#00ffcc', '#ff4b4b'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Les graphiques apparaîtront ici dès le premier scan.")

    with tab_hist:
        if not data.empty:
            st.dataframe(data[['timestamp', 'product_name', 'price', 'verdict']], use_container_width=True)
        else:
            st.warning("Journal vide : Aucun historique détecté.")

with col_ctrl:
    st.subheader("🎮 Commandes")
    if st.button("🚀 Lancer Scan IA", use_container_width=True):
        with st.spinner("Analyse en cours..."):
            run_analysis()
        st.success("Analyse terminée")
        st.rerun()

    st.divider()
    
    with st.expander("🎯 Nouvelle Cible", expanded=True):
        n_name = st.text_input("Produit", key="fast_name")
        n_price = st.number_input("Prix d'alerte", min_value=0.0, key="fast_price")
        if st.button("Activer la veille", use_container_width=True):
            if n_name and n_price > 0:
                db.add_target(n_name, n_price, "Amazon,eBay")
                st.success(f"Cible '{n_name}' engagée")
                st.rerun()