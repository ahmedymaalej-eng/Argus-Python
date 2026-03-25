import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from Main import run_analysis
from Database import DatabaseManager

# --- CONFIGURATION C2 ---
st.set_page_config(
    page_title="Argus IA | Poste de Commandement",
    layout="wide",
    page_icon="🦅"
)

db = DatabaseManager()

# --- CHARGEMENT DES DONNÉES ---
def load_data():
    try:
        conn = sqlite3.connect("argus_project.db")
        df_history = pd.read_sql("SELECT * FROM price_history ORDER BY timestamp DESC", conn)
        df_targets = pd.read_sql("SELECT * FROM targets", conn)
        conn.close()
        return df_history, df_targets
    except:
        return pd.DataFrame(), pd.DataFrame()

history_df, targets_df = load_data()

# --- INTERFACE HAUTE VISIBILITÉ ---
st.title("🦅 Argus IA : Poste de Commandement")

# ZONE 1 : FORMULAIRE DE CONFIRMATION (TOUJOURS EN HAUT)
with st.container(border=True):
    st.subheader("🎯 ACTIVER UNE NOUVELLE SURVEILLANCE")
    col1, col2 = st.columns(2)
    
    with col1:
        nom = st.text_input("📦 Nom du Produit", placeholder="ex: iPad Pro M5")
        prix = st.number_input("💰 Prix d'alerte (€)", min_value=0.0, step=10.0)
    
    with col2:
        sites = st.multiselect(
            "🌐 Sources de Scan",
            options=["Amazon", "eBay"],
            default=["Amazon", "eBay"]
        )
    
    st.write("") # Espace
    
    # LE BOUTON DE CONFIRMATION
    if st.button("🚀 CONFIRMER ET LANCER LA SURVEILLANCE", use_container_width=True):
        if nom and prix > 0:
            sites_str = ",".join(sites)
            db.add_target(nom, prix, sites_str)
            st.success(f"✅ Cible '{nom}' activée !")
            st.balloons()
            st.rerun()
        else:
            st.error("⚠️ Veuillez remplir le nom et le prix avant de confirmer.")

st.divider()

# ZONE 2 : DASHBOARD (S'AFFICHE SI CIBLES PRÉSENTES)
if not targets_df.empty:
    col_vis, col_ctrl = st.columns([3, 1])
    
    with col_vis:
        st.subheader("📈 Tendances & Analyse")
        if not history_df.empty:
            sel_prod = st.selectbox("Sélectionner un produit", history_df['product_name'].unique())
            fig = px.line(history_df[history_df['product_name'] == sel_prod], 
                         x='timestamp', y='price', template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⌛ En attente du premier cycle de scan...")

    with col_ctrl:
        st.subheader("🎮 Contrôles")
        if st.button("🔍 Scan IA Manuel", use_container_width=True):
            with st.spinner("Analyse en cours..."):
                run_analysis()
            st.rerun()
        
        st.divider()
        st.subheader("📋 Liste des Cibles")
        st.dataframe(targets_df[['name', 'target_price']], hide_index=True)
else:
    st.info("💡 Utilisez le formulaire ci-dessus pour configurer votre première cible.")
