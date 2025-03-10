"""
Affichage des résultats
"""
import streamlit as st
from typing import Dict, List, Any
from config import FRENCH_TECH_COLORS
from ui.utils import display_startup_card, display_startup_stats
from ui.custom_style import display_french_tech_footer, display_startup_card_styled, display_tag


def render_results():
    """
    Affiche la page des résultats détaillés
    """
    st.header("📊 Résultats détaillés")

    # Vérification de la présence de startups sélectionnées
    if "selected_startups" not in st.session_state or not st.session_state.selected_startups:
        st.info("Aucune startup sélectionnée. Veuillez d'abord effectuer une recherche.")

        # Bouton pour revenir au chat
        if st.button("Retour au chat"):
            st.session_state.current_view = "chat"
            st.experimental_rerun()

        return

    # Récupération des startups sélectionnées
    startups = st.session_state.selected_startups

    # Affichage des options de filtrage
    with st.sidebar:
        st.subheader("Filtres")

        # Récupération des tags uniques
        all_tags = set()
        for startup in startups:
            for tag in startup.get("tags", []):
                all_tags.add(tag)

        # Filtre par tags
        selected_tags = st.multiselect(
            "Filtrer par tags",
            options=sorted(list(all_tags))
        )

        # Récupération des domaines uniques
        domains = set(startup.get("domain", "") for startup in startups if startup.get("domain"))

        # Filtre par domaine
        selected_domain = st.selectbox(
            "Filtrer par domaine",
            options=["Tous"] + sorted(list(domains))
        )

        # Récupération des localisations uniques
        locations = set(startup.get("location", "") for startup in startups if startup.get("location"))

        # Filtre par localisation
        selected_location = st.selectbox(
            "Filtrer par localisation",
            options=["Toutes"] + sorted(list(locations))
        )

        # Bouton pour réinitialiser les filtres
        if st.button("Réinitialiser les filtres"):
            selected_tags = []
            selected_domain = "Tous"
            selected_location = "Toutes"

    # Application des filtres
    filtered_startups = startups

    # Filtre par tags
    if selected_tags:
        filtered_startups = [
            startup for startup in filtered_startups
            if any(tag in startup.get("tags", []) for tag in selected_tags)
        ]

    # Filtre par domaine
    if selected_domain != "Tous":
        filtered_startups = [
            startup for startup in filtered_startups
            if startup.get("domain") == selected_domain
        ]

    # Filtre par localisation
    if selected_location != "Toutes":
        filtered_startups = [
            startup for startup in filtered_startups
            if startup.get("location") == selected_location
        ]

    # Affichage du nombre de résultats
    st.write(f"**{len(filtered_startups)}** startup(s) correspondent à vos critères.")

    # Option pour retourner au chat
    if st.button("Retour au chat"):
        st.session_state.current_view = "chat"
        st.experimental_rerun()

    # Affichage des statistiques
    display_startup_stats(filtered_startups)

    # Affichage des startups filtrées
    st.subheader("Liste des startups")

    if not filtered_startups:
        st.info("Aucune startup ne correspond aux filtres sélectionnés.")
        return

    # Affichage de chaque startup
    for idx, startup in enumerate(filtered_startups):
        display_startup_card_styled(startup)

        # Bouton pour voir les détails
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Voir les détails", key=f"details_{startup.get('id', '')}_{idx}"):
                st.session_state.current_view = "details"
                st.session_state.selected_startup = startup
                st.experimental_rerun()

    # Affichage du footer
    display_french_tech_footer()