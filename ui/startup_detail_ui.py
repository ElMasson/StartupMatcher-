"""
Affichage des détails d'une startup
"""
import streamlit as st
from typing import Dict, List, Any
from config import FRENCH_TECH_COLORS
from ui.utils import display_startup_card, format_tags
from ui.custom_style import display_french_tech_footer, display_startup_card_styled, display_tag


def render_startup_detail():
    """
    Affiche la page de détails d'une startup
    """
    st.header("🔍 Détails de la startup")

    # Vérification de la présence d'une startup sélectionnée
    if "selected_startup" not in st.session_state or not st.session_state.selected_startup:
        st.info("Aucune startup sélectionnée. Veuillez d'abord sélectionner une startup.")

        # Bouton pour revenir aux résultats
        if st.button("Voir tous les résultats"):
            st.session_state.current_view = "results"
            st.experimental_rerun()

        # Bouton pour revenir au chat
        if st.button("Retour au chat"):
            st.session_state.current_view = "chat"
            st.experimental_rerun()

        return

    # Récupération de la startup sélectionnée
    startup = st.session_state.selected_startup

    # Boutons de navigation
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Retour aux résultats"):
            st.session_state.current_view = "results"
            st.experimental_rerun()

    with col2:
        if st.button("💬 Retour au chat"):
            st.session_state.current_view = "chat"
            st.experimental_rerun()

    # Affichage des détails de la startup avec le style French Tech
    with st.container():
        # Titre et description
        st.markdown(
            f"<h1 style='color: {FRENCH_TECH_COLORS['primary']};'>{startup.get('name', 'Startup sans nom')}</h1>",
            unsafe_allow_html=True)
        st.markdown(
            f"<div style='padding: 1rem; border-left: 4px solid {FRENCH_TECH_COLORS['primary']}; background-color: {FRENCH_TECH_COLORS['light_gray']}; margin-bottom: 1.5rem;'>{startup.get('description', 'Pas de description disponible.')}</div>",
            unsafe_allow_html=True)

        # Informations générales
        st.markdown(f"<h3 style='color: {FRENCH_TECH_COLORS['primary']};'>Informations générales</h3>",
                    unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"<p><strong>Domaine d'activité:</strong> {startup.get('domain', 'Non spécifié')}</p>",
                        unsafe_allow_html=True)
            st.markdown(f"<p><strong>Localisation:</strong> {startup.get('location', 'Non spécifiée')}</p>",
                        unsafe_allow_html=True)

            if startup.get("contact"):
                st.markdown(f"<p><strong>Contact:</strong> {startup.get('contact')}</p>", unsafe_allow_html=True)

        with col2:
            if startup.get("tags"):
                st.markdown(f"<p><strong>Technologies & Tags:</strong></p>", unsafe_allow_html=True)
                # Affichage des tags avec le style French Tech
                tag_html = "<div style='display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;'>"
                for tag in startup.get("tags", []):
                    tag_html += f'<span class="tag">{tag}</span>'
                tag_html += "</div>"
                st.markdown(tag_html, unsafe_allow_html=True)

            if startup.get("url"):
                st.markdown(
                    f"<p><strong>Site web:</strong> <a href='{startup.get('url')}' target='_blank' style='color: {FRENCH_TECH_COLORS['accent']};'>{startup.get('url')}</a></p>",
                    unsafe_allow_html=True)

        # Actions possibles
        st.subheader("Actions")

        col1, col2 = st.columns(2)

        with col1:
            if startup.get("url"):
                st.markdown(f"🌐 [Visiter le site web]({startup.get('url')})")

        with col2:
            if startup.get("contact") and "@" in startup.get("contact"):
                email = startup.get("contact")
                subject = f"Demande d'information - {startup.get('name', 'Startup')}"
                body = f"Bonjour,\n\nJe suis intéressé(e) par vos solutions et j'aimerais obtenir plus d'informations.\n\nCordialement,"

                mailto_link = f"mailto:{email}?subject={subject}&body={body}".replace(" ", "%20").replace("\n", "%0A")
                st.markdown(f"📧 [Contacter par email]({mailto_link})")

        # Poser une question sur cette startup
        st.subheader("Poser une question sur cette startup")

        question = st.text_input("Votre question:", key="startup_question")

        if st.button("Envoyer la question"):
            if question:
                # Retour au chat avec la question posée
                new_message = f"Dis-moi en plus sur {startup.get('name', 'cette startup')} : {question}"

                # Ajout du message à l'historique
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                st.session_state.messages.append({"role": "user", "content": new_message})
                st.session_state.current_view = "chat"
                st.experimental_rerun()
            else:
                st.warning("Veuillez entrer une question avant d'envoyer.")

    # Affichage du footer
    display_french_tech_footer()

    # Suggestions de questions
    with st.expander("Suggestions de questions"):
        suggestions = [
            f"Quels sont les avantages concurrentiels de {startup.get('name', 'cette startup')} ?",
            f"Comment {startup.get('name', 'cette startup')} pourrait m'aider pour un projet d'innovation ?",
            f"Quelles sont les technologies utilisées par {startup.get('name', 'cette startup')} ?",
            f"Est-ce que {startup.get('name', 'cette startup')} a des références clients ?",
            f"Quels sont les cas d'usage typiques de {startup.get('name', 'cette startup')} ?"
        ]

        for suggestion in suggestions:
            if st.button(suggestion, key=f"sugg_{hash(suggestion)}"):
                # Ajout de la suggestion à l'historique
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.session_state.current_view = "chat"
                st.experimental_rerun()