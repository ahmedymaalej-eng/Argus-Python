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

# --- CORPS PRINCIPAL ---
data = load_full_data()
targets_df = load_targets()

if not data.empty:
    # 1. SECTION KPI (Observatoire Macro)
    # -------------------------------------------------------------------
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("📡 Dernière Synchronisation", str(data['timestamp'].iloc[0])[11:19])
    with k2:
        st.metric("🎯 Cibles Actives", len(targets_df))
    with k3:
        # Calcul du meilleur deal (différence prix vs cible)
        if 'target_price' in data.columns and not data['target_price'].isna().all():
            data['deal_delta'] = data['target_price'] - data['price']
            best_deal = data['deal_delta'].max()
            best_prod = data.loc[data['deal_delta'].idxmax(), 'product_name'] if best_deal > 0 else "N/A"
            st.metric("🏆 Meilleure Opportunité", f"+{best_deal}€" if best_deal > 0 else "0€", help=best_prod)
        else:
            st.metric("🏆 Meilleure Opportunité", "Analyse en cours")
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
            st.subheader("Analyse de l'évolution des prix")
            # Filtrage dynamique par produit
            all_prods = data['product_name'].unique()
            selected_prod = st.selectbox("Sélectionner un produit pour l'analyse", options=all_prods, index=0)
            filtered_df = data[data['product_name'] == selected_prod]
            
            # Graphique Plotly Express
            fig = px.line(
                filtered_df, x='timestamp', y=['price', 'target_price'],
                color_discrete_map={'price': '#00ffcc', 'target_price': '#ff4b4b'},
                markers=True, template="plotly_dark",
                labels={"value": "Prix (€)", "timestamp": "Heure du Scan", "variable": "Type de Prix"}
            )
            # Personnalisation des lignes
            fig.update_traces(mode="lines+markers")
            fig.update_layout(
                hovermode="x unified",
                xaxis=dict(showgrid=False),
                yaxis=dict(title="Prix en Euros", gridcolor="#2d3748")
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab_hist:
            st.subheader("Journal exhaustif des scans")
            # Utilisation de formateurs pour colorer le verdict
            hist_df = data[['timestamp', 'product_name', 'price', 'source', 'verdict']]
            st.dataframe(hist_df, use_container_width=True, hide_index=True)

    # --- Colonne CONTRÔLE (Droite) ---
    with col_ctrl:
        st.subheader("🎮 Panneau de Commandement")
        
        # Bouton d'action principal
        if st.button("🚀 Lancer Scan IA", use_container_width=True):
            with st.spinner("Analyse du marché en cours..."):
                run_analysis()
            st.success("Cycle terminé !")
            st.rerun()

        st.divider()

        # Section de Configuration des Cibles
        st.subheader("🎯 Cibles de Veille")
        
        # 1. AJOUTER (Dans un expander)
        with st.expander("➕ Ajouter une nouvelle Cible", expanded=True):
            new_name = st.text_input("Nom du Produit", placeholder="ex: Sony PS5")
            new_price = st.number_input("Prix d'alerte (€)", min_value=0.0, step=10.0)
            
            # Sélecteur de sites
            selected_sites = st.multiselect(
                "Sources",
                options=["Amazon", "eBay"],
                default=["Amazon", "eBay"],
                help="Choisissez les sources de données pour ce produit."
            )
            
            if st.button("Activer la Surveillance", use_container_width=True):
                if new_name and new_price > 0 and selected_sites:
                    sites_str = ",".join(selected_sites)
                    db.add_target(new_name, new_price, sites_str)
                    st.toast(f"Cible activée : {new_name}", icon="✅")
                    st.rerun()
                elif not selected_sites:
                    st.warning("Choisissez au moins une source.")

        st.divider()

        # 2. GÉRER / SUPPRIMER
        if not targets_df.empty:
            st.subheader("📋 Gérer vos Cibles")
            for _, row in targets_df.iterrows():
                # On met chaque cible dans son petit conteneur
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**{row['name']}**")
                        # Formatage des sites
                        sites_badges = row['sites'].split(',')
                        badges_html = " ".join([f'<span style="background-color: #242c3d; padding: 2px 5px; border-radius: 4px; font-size: 0.7rem;">{s}</span>' for s in sites_badges])
                        st.markdown(f"{row['target_price']}€ | {badges_html}", unsafe_allow_html=True)
                    with c2:
                        # Bouton poubelle
                        if st.button("🗑️", key=f"del_{row['name']}"):
                            db.remove_target(row['name'])
                            st.rerun()
        else:
            st.info("Aucune cible de veille configurée.")

    st.divider()

    # 3. SECTION DIAGNOSTIC (En bas, plus discrète)
    # -------------------------------------------------------------------
    with st.expander("🛠️ Panneau de Diagnostic des Canaux", expanded=False):
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.image("https://img.icons8.com/?size=100&id=11387&format=png&color=00ffcc", width=40)
            st.markdown("**Notification Email**")
            if st.button("📩 Test Email", key="test_email"):
                # email_bot.send_email(...) # Désactivé pour le frontend
                st.info("Requête de test envoyée.")
        with col_d2:
            st.image("https://img.icons8.com/?size=100&id=32274&format=png&color=00ffcc", width=40)
            st.markdown("**Notification SMS**")
            if st.button("📱 Test SMS", key="test_sms"):
                # sms_bot.send_sms(...) # Désactivé pour le frontend
                st.info("Requête de test envoyée.")
        with col_d3:
            st.image("https://img.icons8.com/?size=100&id=63653&format=png&color=a0aec0", width=40)
            st.markdown("**Base de Données**")
            st.write(f"Version: SQL C2-Pro")
            if st.button("🧪 Inject Fake Data", key="test_fake"):
                db.save_price("Test C2-Eagle", 15.50, "Debug-Bot", "Excellent Deal ✅")
                st.rerun()

else:
    # -------------------------------------------------------------------
    # PAGE VIDE : INSTRUCTIONS DE DÉMARRAGE
    # -------------------------------------------------------------------
    col_info1, col_info2 = st.columns([1, 3])
    with col_info1:
        st.image("https://img.icons8.com/?size=100&id=121175&format=png&color=00ffcc", width=200) # Eagle Icon
    with col_info2:
        st.title("🦅 Bienvenue sur Argus IA : Poste de Commandement C2")
        st.markdown("""
        Votre système de veille de marché est **prêt pour l'engagement**. La base de données est actuellement vierge de toute cible.
        
        ### Instructions de déploiement :
        
        1.  **🎯 Définir une Cible** : Dans le panneau de droite, entrez le nom d'un produit, un prix d'alerte et sélectionnez vos sources.
        2.  **🚀 Lancer l'Analyse** : Une fois la cible activée, cliquez sur 'Lancer Scan IA' pour initier le premier cycle de collecte et de décision.
        3.  **Analyse** : Le tableau de bord se peuplera automatiquement de KPIs, de graphiques de tendances et de verdicts IA.
        
        ### Rappel de Configuration (Back-end) :
        * Assurez-vous que vos clés **Twilio** et **Resend** sont bien configurées dans leurs fichiers respectifs pour recevoir les alertes omicanales.
        * Vérifiez que votre base de données SQL a été mise à jour pour accepter le paramètre `sites` via la commande `ALTER TABLE`.
        
        """)

