import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from Main import run_analysis
from Database import DatabaseManager

# --- CONFIGURATION DE HAUT NIVEAU C2 ---
st.set_page_config(
    page_title="Argus IA | Stratégie de Marché",
    layout="wide",
    page_icon="🦅"
)

db = DatabaseManager()

# --- FONCTIONS DE CHARGEMENT ---
def load_full_data():
    try:
        conn = sqlite3.connect("argus_project.db")
        df = pd.read_sql("SELECT * FROM price_history ORDER BY timestamp DESC", conn)
        df_targets = pd.read_sql("SELECT name, target_price FROM targets", conn)
        conn.close()
        if not df.empty and not df_targets.empty:
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

# --- STYLE VISUEL ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .main-button {
        background-color: #00ffcc !important;
        color: #0b0e14 !important;
        font-weight: bold !important;
        height: 3em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- RÉCUPÉRATION DES DONNÉES ---
targets_df = load_targets()
data = load_full_data()

# --- HEADER ---
st.title("🦅 Argus IA : Poste de Commandement")

# -------------------------------------------------------------------
# ZONE 1 : FORMULAIRE D'AJOUT (TOUJOURS EN HAUT SI VIDE)
# -------------------------------------------------------------------
if targets_df.empty:
    st.error("🚨 AUCUNE CIBLE ACTIVE : Le système attend vos ordres.")
else:
    st.success(f"✅ Surveillance active sur {len(targets_df)} produits.")

with st.container(border=True):
    st.subheader("🎯 CONFIGURER UNE VEILLE")
    c1, c2, c3 = st.columns([2, 1, 2])
    
    with c1:
        new_name = st.text_input("📦 Nom du Produit", placeholder="ex: iPad Pro M5")
    with c2:
        new_price = st.number_input("💰 Prix d'alerte (€)", min_value=0.0)
    with c3:
        selected_sites = st.multiselect("🌐 Sources", ["Amazon", "eBay"], default=["Amazon", "eBay"])
    
    if st.button("🚀 ACTIVER LA SURVEILLANCE MAINTENANT", use_container_width=True):
        if new_name and new_price > 0:
            sites_str = ",".join(selected_sites)
            db.add_target(new_name, new_price, sites_str)
            st.toast("Cible ajoutée avec succès !")
            st.rerun()
        else:
            st.warning("⚠️ Information manquante.")

st.divider()

# -------------------------------------------------------------------
# ZONE 2 : DASHBOARD (S'AFFICHE SI DONNÉES PRÉSENTES)
# -------------------------------------------------------------------
if not targets_df.empty:
    col_graph, col_stats = st.columns([3, 1])
    
    with col_graph:
        st.subheader("📈 Évolution des Prix & Tendances")
        if not data.empty:
            prod_list = data['product_name'].unique()
            sel_prod = st.selectbox("Filtrer par produit", prod_list)
            filtered_df = data[data['product_name'] == sel_prod]
            fig = px.line(filtered_df, x='timestamp', y='price', title=f"Historique : {sel_prod}", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⌛ En attente du premier cycle de scan pour générer les graphiques...")

    with col_stats:
        st.subheader("🎮 Actions")
        if st.button("🔍 Lancer Scan IA Manuel", use_container_width=True):
            with st.spinner("Analyse sémantique en cours..."):
                run_analysis()
            st.rerun()
        
        st.divider()
        st.subheader("📋 Liste des Cibles")
        st.table(targets_df[['name', 'target_price']])
