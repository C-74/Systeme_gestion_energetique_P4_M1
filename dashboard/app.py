import streamlit as st

st.set_page_config(page_title="Dashboard Énergétique", layout="wide")

st.title("⚡ Système de Gestion Énergétique Intelligent")
st.markdown("Bienvenue sur la plateforme de supervision énergétique du bâtiment.")

st.sidebar.header("Navigation")
menu = st.sidebar.radio("Aller vers :", ["Vue d'ensemble", "Capteurs (Virtuels)", "Indicateurs de Performance", "Optimisation"])

if menu == "Vue d'ensemble":
    st.subheader("Vue d'ensemble")
    st.info("L'intégration des données de capteurs sera affichée ici prochainement.")

elif menu == "Capteurs (Virtuels)":
    st.subheader("Supervision des Capteurs")
    st.write("- Consommation")
    st.write("- Production Solaire")
    st.write("- Stockage (Batteries)")

elif menu == "Indicateurs de Performance":
    st.subheader("Indicateurs de Performance Énergétique (KPIs)")
    st.write("Calcul et analyse des indicateurs à venir.")

elif menu == "Optimisation":
    st.subheader("Modèles d'Optimisation")
    st.write("Propositions d'optimisation de la consommation énergétique à venir.")
