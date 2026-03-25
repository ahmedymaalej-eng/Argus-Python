import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from Main import run_analysis
from Database import DatabaseManager

# --- CONFIGURATION DE HAUT NIVEAU C2 ---
st.set_page_config(
    page_title="Argus IA | Stratégie de Marché C2",
    layout="wide",
    page_icon="🦅"
)

db = DatabaseManager()

# --- CHARGEMENT DES DONNÉES (SÉCURISÉ) ---
@st.cache_data(ttl=60)
def load_full_data():
    try:
        conn = sqlite3.connect("argus_project.db")
        # Récupération de l'historique
        df = pd.read_sql("SELECT * FROM price_history ORDER BY timestamp DESC", conn)
        # Récupération des cibles
        df_targets = pd.read_sql("SELECT name, target_price FROM targets", conn)
        conn.close()
        
        if not df.empty and not df_targets.empty:
            # Fusion pour corréler les prix actuels et les objectifs
            df = df.merge(df_targets, left_on='product_name', right_on='name', how='left')
        return df
    except Exception as e:
        return pd.DataFrame()

def load_targets():
    try:
        conn = sqlite3.connect("argus_project.db")
        df = pd.read_sql("SELECT name, target_price, sites FROM targets", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# --- STYLE CSS AVANCÉ ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #f0f2f6; }
    [data-testid="stMetric"] {
        background-color: #171c26;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d3748;
    }
    .stButton>button {
        background-color: #00ffcc !important;
        color: #0b0e14 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        height: 3em !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE D'AFFICHAGE ---
targets_df = load_targets()
data_df = load_full_data()

st.title("🦅 Argus IA : Poste de Commandement C2")

# -------------------------------------------------------------------
# ZONE 1 : CONFIGURATION (TOUJOURS EN HAUT POUR IPAD)
# -------------------------------------------------------------------
with st.container(border=True):
    st.subheader("🎯 ACTIVER UNE SURVEILLANCE")
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        new_name = st.text_input("📦 Nom du Produit", placeholder="ex: iPad Pro M5")
        new_price = st.number_input("💰 Prix d'alerte (€)", min_value=0.0, step=10.0)
    
    with col_c2:
        selected_sites = st.multiselect(
            "🌐 Sources de Scan",
            options=["Amazon", "eBay"],
            default=["Amazon", "eBay"]
        )
    
    # BOUTON DE CONFIRMATION
    if st.button("🚀 CONFIRMER ET LANCER LA SURVEILLANCE"):
        if new_name and new_price > 0:
            sites_str = ",".join(selected_sites)
            db.add_target(new_name, new_price, sites_str)
            st.success(f"✅ Cible '{new_name}' enregistrée !")
            st.rerun()
        else:
            st.warning("⚠️ Veuillez remplir le nom et le prix.")

st.divider()

# -------------------------------------------------------------------
# ZONE 2 : DASHBOARD (SI DES CIBLES EXISTENT)
# -------------------------------------------------------------------
if not targets_df.empty:
    k1, k2, k3 = st.columns(3)
    k1.metric("🎯 Cibles", len(targets_df))
    k2.metric("🧠 État IA", "Actif")
    k3.metric("📡 Scan", "Opérationnel")

    col_graph, col_list = st.columns([2, 1])
    
    with col_graph:
        if not data_df.empty:
            prod = st.selectbox("Analyse Graphique", data_df['product_name'].unique())
            fig = px.line(data_df[data_df['product_name'] == prod], 
                         x='timestamp', y='price', template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⌛ En attente de données historiques...")

    with col_list:
        st.subheader("📋 Liste des veilles")
        st.dataframe(targets_df[['name', 'target_price']], hide_index=True)
        if st.button("🔍 Scan IA Manuel"):
            with st.spinner("Analyse..."):
                run_analysis()
            st.rerun()
else:
    st.info("💡 Le système est prêt. Ajoutez votre première cible ci-dessus.")

# --- HEADER & TITRE MAJESTUEUX ---
col_head1, col_head2 = st.columns([1, 10])
with col_head1:
    # Icône Eagle Pro (Lien robuste)
    st.image("https://img.icons8.com/?size=100&id=121175&format=png&color=00ffcc", width=80) 
with col_head2:
    st.title("Argus IA : Poste de Commandement C2")
    st.caption("鷹 (Argus) - Système autonome de surveillance et de décision prédictive")

st.divider()

# --- RÉCUPÉRATION DES DONNÉES ---
data = load_full_data()
targets_df = load_targets()

if not data.empty:
    # 1. SECTION KPI (Observatoire Macro-Économique)
    # -------------------------------------------------------------------
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        # Extraction propre de l'heure du dernier scan
        last_scan = str(data['timestamp'].iloc[0])[11:19] if not data.empty else "--:--:--"
        st.metric("📡 Dernière Synchro", last_scan)
        
    with k2:
        st.metric("🎯 Cibles Actives", len(targets_df))
        
    with k3:
        # Calcul sécurisé du meilleur deal (Prix actuel vs Cible)
        if 'target_price' in data.columns and not data['target_price'].isna().all():
            # On calcule la différence positive (Cible - Prix actuel)
            data['deal_delta'] = data['target_price'] - data['price']
            best_deal_idx = data['deal_delta'].idxmax()
            best_deal_val = data.loc[best_deal_idx, 'deal_delta']
            best_prod_name = data.loc[best_deal_idx, 'product_name']
            
            if best_deal_val > 0:
                st.metric("🏆 Meilleur Deal", f"+{best_deal_val:.2f}€", help=f"Produit : {best_prod_name}")
            else:
                st.metric("🏆 Meilleur Deal", "0€", help="Aucun prix sous la cible")
        else:
            st.metric("🏆 Meilleur Deal", "Analyse...")
            
    with k4:
        st.metric("🧠 État Système", "Opérationnel ✅")

    st.divider()

    # 2. SECTION ANALYTIQUE ET CONTRÔLE
    # -------------------------------------------------------------------
    col_vis, col_ctrl = st.columns([3, 1])

    with col_vis:
        tab_graph, tab_hist = st.tabs(["📈 Tendances", "🔍 Journal"])
        
        with tab_graph:
            st.subheader("Évolution Temporelle")
            all_prods = data['product_name'].unique()
            selected_prod = st.selectbox("Sélectionner une unité", options=all_prods)
            
            filtered_df = data[data['product_name'] == selected_prod].copy()
            
            # Graphique Haute Fidélité
            fig = px.line(
                filtered_df, 
                x='timestamp', 
                y=['price', 'target_price'],
                labels={"value": "Euros (€)", "timestamp": "Temps", "variable": "Légende"},
                markers=True,
                template="plotly_dark",
                color_discrete_map={'price': '#00ffcc', 'target_price': '#ff4b4b'}
            )
            
            fig.update_layout(
                hovermode="x unified",
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#2d3748"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab_hist:
            st.subheader("Historique des Scans")
            # Nettoyage des colonnes pour l'affichage
            display_cols = ['timestamp', 'product_name', 'price', 'source', 'verdict']
            st.dataframe(data[display_cols], use_container_width=True, hide_index=True)

    with col_ctrl:
        st.subheader("🎮 Actions")
        # Bouton de scan manuel intégré
        if st.button("🚀 LANCER SCAN IA", use_container_width=True):
            with st.spinner("Engagement du protocole..."):
                run_analysis()
            st.success("Analyse terminée")
            st.rerun()

       # --- Colonne CONTRÔLE (Droite) ---
    with col_ctrl:
        st.subheader("🎮 Panneau de Commandement")
        
        # Bouton d'action principal (Haute visibilité)
        if st.button("🚀 Lancer Scan IA", use_container_width=True):
            with st.spinner("Analyse du marché en cours..."):
                run_analysis()
            st.success("Cycle terminé !")
            st.rerun()

        st.divider()

        # Section de Configuration des Cibles
        st.subheader("🎯 Cibles de Veille")
        
        # 1. AJOUTER (Dans un expander pour gagner de l'espace sur iPad)
        with st.expander("➕ Ajouter une nouvelle Cible", expanded=True):
            new_name = st.text_input("Nom du Produit", placeholder="ex: Sony PS5", key="input_name")
            new_price = st.number_input("Prix d'alerte (€)", min_value=0.0, step=10.0, key="input_price")
            
            # Sélecteur de sites
            selected_sites = st.multiselect(
                "Sources",
                options=["Amazon", "eBay", "LeBonCoin"],
                default=["Amazon", "eBay"],
                help="Choisissez les vecteurs de recherche pour ce produit.",
                key="input_sites"
            )
            
            if st.button("Activer la Surveillance", use_container_width=True, key="btn_activate"):
                if new_name and new_price > 0 and selected_sites:
                    sites_str = ",".join(selected_sites)
                    db.add_target(new_name, new_price, sites_str)
                    st.toast(f"Cible activée : {new_name}", icon="✅")
                    st.rerun()
                elif not selected_sites:
                    st.warning("Choisissez au moins une source.")
                else:
                    st.error("Données incomplètes.")

        st.divider()

        # 2. GÉRER / SUPPRIMER (Affichage dynamique)
        if not targets_df.empty:
            st.subheader("📋 Gérer vos Cibles")
            for index, row in targets_df.iterrows():
                # Création d'un badge visuel pour chaque cible
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**{row['name']}**")
                        # Formatage élégant des sources
                        sites_badges = row['sites'].split(',')
                        badges_html = " ".join([
                            f'<span style="background-color: #242c3d; color: #00ffcc; padding: 2px 8px; '
                            f'border-radius: 12px; font-size: 0.75rem; border: 1px solid #2d3748;">{s.strip()}</span>' 
                            for s in sites_badges
                        ])
                        st.markdown(f"{row['target_price']}€ | {badges_html}", unsafe_allow_html=True)
                    with c2:
                        # Bouton de suppression avec clé unique pour éviter les conflits Streamlit
                        if st.button("🗑️", key=f"del_{row['name']}_{index}"):
                            db.remove_target(row['name'])
                            st.rerun()
        else:
            st.info("Aucune cible de veille configurée.")

    st.divider()

    # 3. SECTION DIAGNOSTIC (Maintenance du Système)
    # -------------------------------------------------------------------
    with st.expander("🛠️ Diagnostic & Canaux de Transmission", expanded=False):
        st.caption("Vérification de l'intégrité des modules de notification")
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            st.image("https://img.icons8.com/?size=100&id=11387&format=png&color=00ffcc", width=40)
            st.markdown("**Email**")
            if st.button("📩 Test", key="test_email", use_container_width=True):
                st.info("Requête transmise à Resend.")
                
        with col_d2:
            st.image("https://img.icons8.com/?size=100&id=32274&format=png&color=00ffcc", width=40)
            st.markdown("**SMS**")
            if st.button("📱 Test", key="test_sms", use_container_width=True):
                st.info("Requête transmise à Twilio.")
                
        with col_d3:
            st.image("https://img.icons8.com/?size=100&id=63653&format=png&color=a0aec0", width=40)
            st.markdown("**Base SQL**")
            st.caption("Version C2-Eagle")
            if st.button("🧪 Inject", key="test_fake", use_container_width=True):
                db.save_price("Debug-Eagle", 99.99, "System-Check", "Initialisation ✅")
                st.rerun()
