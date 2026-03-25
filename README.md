# 🦅 Project Argus : Smart AI Market Monitoring
**Analyse de Marché Dynamique & Intelligence Sémantique (NLP)**

---

## 🇫🇷 Français

### 📝 Présentation
Argus est une plateforme de surveillance de prix intelligente conçue pour automatiser la veille commerciale. Contrairement aux outils classiques, Argus intègre un moteur de **Traitement du Langage Naturel (NLP)** pour analyser le sentiment des avis clients, garantissant que l'utilisateur ne reçoit des alertes que pour des produits jugés fiables par la communauté.

### 🚀 Fonctionnalités Clés
* **Scraping Multi-Sources** : Extraction asynchrone (Multithreading) des données depuis eBay, Amazon et autres.
* **Analyse de Sentiment IA** : Utilisation de `TextBlob` pour générer un verdict qualitatif sur chaque produit.
* **Dashboard Professionnel** : Interface interactive via `Streamlit` avec graphiques Plotly en temps réel.
* **Système de Notification Omnicanal** : Alertes instantanées par SMS (Twilio) et Email (Resend/SMTP).
* **Persistence SQL** : Historisation complète des prix et des verdicts IA via SQLite.

### 🛠️ Stack Technique
* **Langage** : Python 3.12+
* **Data & IA** : BeautifulSoup4, TextBlob, Pandas, Plotly.
* **Infrastructure** : Concurrent Futures (Threads), SQLite3.
* **Interface & DevOps** : Streamlit, Git, GitHub Codespaces.

---

## 🇺🇸 English

### 📝 Overview
Argus is an intelligent price monitoring platform designed to automate market research. Unlike traditional tools, Argus features a **Natural Language Processing (NLP)** engine to analyze customer review sentiments, ensuring users receive alerts only for products deemed reliable by the community.

### 🚀 Key Features
* **Multi-Source Scraping**: Asynchronous data extraction (Multithreading) from eBay, Amazon, and more.
* **AI Sentiment Analysis**: Leveraging `TextBlob` to generate a qualitative verdict for every tracked product.
* **Professional Dashboard**: Interactive UI built with `Streamlit`, featuring real-time Plotly charts.
* **Omnichannel Notifications**: Instant alerts via SMS (Twilio) and Email (Resend/SMTP).
* **SQL Persistence**: Full history of prices and AI verdicts stored via SQLite.

### 🛠️ Tech Stack
* **Language**: Python 3.12+
* **Data & AI**: BeautifulSoup4, TextBlob, Pandas, Plotly.
* **Infrastructure**: Concurrent Futures (Threads), SQLite3.
* **Interface & DevOps**: Streamlit, Git, GitHub Codespaces.

---

## ⚙️ Installation & Setup

1. **Variables d'environnement / Environment Variables** :
   ```bash
   export TWILIO_ACCOUNT_SID='your_sid'
   export TWILIO_AUTH_TOKEN='your_token'
   export TWILIO_PHONE_NUMBER='your_twilio_num'
   export MY_PHONE_NUMBER='your_phone'
