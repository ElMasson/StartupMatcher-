"""
Fonctions utilitaires pour l'interface utilisateur
"""
import streamlit as st
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def format_tags(tags: List[str]) -> str:
    """
    Formate une liste de tags pour l'affichage

    Args:
        tags: Liste des tags

    Returns:
        Tags formatés
    """
    if not tags:
        return ""

    return ", ".join(tags)


def display_message(message: Dict[str, str]):
    """
    Affiche un message dans l'interface de chat

    Args:
        message: Message à afficher
    """
    role = message.get("role", "")
    content = message.get("content", "")

    if role == "user":
        st.chat_message("user").markdown(content)
    else:
        st.chat_message("assistant").markdown(content)


def display_startup_card(startup: Dict[str, Any], detailed: bool = False):
    """
    Affiche une carte d'information pour une startup

    Args:
        startup: Données de la startup
        detailed: Affichage détaillé ou non
    """
    with st.container():
        st.subheader(startup.get("name", "Startup sans nom"))

        # Description
        st.markdown(startup.get("description", "Pas de description disponible."))

        # Informations complémentaires
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Domaine:** {startup.get('domain', 'Non spécifié')}")
            st.markdown(f"**Localisation:** {startup.get('location', 'Non spécifiée')}")

        with col2:
            st.markdown(f"**Tags:** {format_tags(startup.get('tags', []))}")
            if startup.get("url"):
                st.markdown(f"**Site web:** [{startup.get('url')}]({startup.get('url')})")

        # Détails supplémentaires si demandé
        if detailed and startup.get("contact"):
            st.markdown(f"**Contact:** {startup.get('contact')}")

        # Boutons d'action
        col1, col2, col3 = st.columns(3)

        with col1:
            # Bouton pour voir les détails
            if not detailed:
                if st.button("Voir les détails", key=f"details_{startup.get('id', '')}"):
                    st.session_state.current_view = "details"
                    st.session_state.selected_startup = startup
                    st.experimental_rerun()

        with col2:
            # Bouton pour contacter
            if startup.get("contact") and detailed:
                st.markdown(f"📧 **Email:** {startup.get('contact')}")

        with col3:
            # Bouton pour visiter le site
            if startup.get("url"):
                st.markdown(f"🌐 [Visiter le site]({startup.get('url')})")

        st.markdown("---")


def display_startup_list(startups: List[Dict[str, Any]], title: str = "Startups trouvées"):
    """
    Affiche une liste de startups

    Args:
        startups: Liste des startups à afficher
        title: Titre de la section
    """
    st.subheader(title)

    if not startups:
        st.info("Aucune startup trouvée.")
        return

    # Affichage des startups
    for startup in startups:
        display_startup_card(startup)


def display_startup_stats(startups: List[Dict[str, Any]]):
    """
    Affiche des statistiques sur un ensemble de startups

    Args:
        startups: Liste des startups
    """
    if not startups:
        st.info("Aucune donnée disponible pour les statistiques.")
        return

    st.subheader("Statistiques")

    # Préparation des données
    domains = {}
    locations = {}
    tags = {}

    for startup in startups:
        # Comptage des domaines
        domain = startup.get("domain", "Non spécifié")
        domains[domain] = domains.get(domain, 0) + 1

        # Comptage des localisations
        location = startup.get("location", "Non spécifiée")
        locations[location] = locations.get(location, 0) + 1

        # Comptage des tags
        for tag in startup.get("tags", []):
            tags[tag] = tags.get(tag, 0) + 1

    col1, col2 = st.columns(2)

    with col1:
        # Graphique des domaines
        domains_df = pd.DataFrame({"Domaine": list(domains.keys()), "Nombre": list(domains.values())})
        fig1 = px.pie(domains_df, values="Nombre", names="Domaine", title="Répartition par domaine d'activité")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Graphique des localisations
        locations_df = pd.DataFrame({"Localisation": list(locations.keys()), "Nombre": list(locations.values())})
        fig2 = px.bar(locations_df, x="Localisation", y="Nombre", title="Répartition géographique")
        st.plotly_chart(fig2, use_container_width=True)

    # Graphique des tags (top 10)
    top_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]
    tags_df = pd.DataFrame({"Tag": [t[0] for t in top_tags], "Nombre": [t[1] for t in top_tags]})
    fig3 = px.bar(tags_df, x="Tag", y="Nombre", title="Top 10 des technologies/tags")
    st.plotly_chart(fig3, use_container_width=True)