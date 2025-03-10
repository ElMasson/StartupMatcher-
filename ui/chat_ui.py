"""
Interface de chat
"""
import streamlit as st
from typing import Dict, List, Any
from agent.agent_handler import AgentHandler
from ui.utils import display_message, display_startup_list
from ui.custom_style import display_french_tech_footer, display_startup_card_styled
from config import FRENCH_TECH_COLORS


def render_chat_interface():
    """
    Affiche l'interface de chat
    """
    st.header("💬 Discutez avec l'assistant")

    # Initialisation de l'agent handler si nécessaire
    if "agent_handler" not in st.session_state:
        st.session_state.agent_handler = AgentHandler()

    # Initialisation de l'historique des messages si nécessaire
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage des messages précédents
    for message in st.session_state.messages:
        display_message(message)

    # Zone de saisie du message - utilisation d'une clé unique pour éviter les conflits
    chat_input_key = f"chat_input_{id(render_chat_interface)}"

    # Vérification si l'input existe déjà dans la session
    if chat_input_key not in st.session_state:
        st.session_state[chat_input_key] = ""

    # Utilisation de st.text_input au lieu de st.chat_input pour éviter les conflits
    user_input = st.text_input(
        "Posez votre question :",
        key=chat_input_key,
        value=st.session_state[chat_input_key]
    )

    # Bouton d'envoi
    if st.button("Envoyer", key=f"send_button_{id(render_chat_interface)}"):
        if user_input:
            # Réinitialisation de l'input
            prompt = user_input
            st.session_state[chat_input_key] = ""

            # Ajout du message utilisateur à l'historique
            st.session_state.messages.append({"role": "user", "content": prompt})
            display_message({"role": "user", "content": prompt})

            # Traitement du message par l'agent
            with st.spinner("Réflexion en cours..."):
                # Conversion de l'historique des messages pour l'agent
                history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages[:-1]  # Exclure le message actuel
                ]

                # Appel à l'agent pour traiter le message
                response = st.session_state.agent_handler.process_user_message(prompt, history)

                # Extraction du contenu de la réponse
                response_content = response.get("content", "Je n'ai pas pu traiter votre demande.")

                # Ajout de la réponse à l'historique
                st.session_state.messages.append({"role": "assistant", "content": response_content})

                # Affichage de la réponse
                display_message({"role": "assistant", "content": response_content})

                # Si la réponse contient des startups, les stocker pour affichage ultérieur
                if response.get("has_startups", False) and "startups" in response:
                    st.session_state.selected_startups = response["startups"]

                    # Affichage de la liste des startups
                    with st.expander("Voir les startups recommandées", expanded=True):
                        st.markdown(f"<h3 style='color: {FRENCH_TECH_COLORS['primary']}'>Startups recommandées</h3>",
                                    unsafe_allow_html=True)
                        for startup in response["startups"]:
                            display_startup_card_styled(startup)

                    # Option pour basculer vers la vue détaillée des résultats
                    if st.button("Voir tous les résultats en détail", key="view_detail_button"):
                        st.session_state.current_view = "results"
                        st.experimental_rerun()

            # Forcer le rafraîchissement pour afficher la réponse
            st.experimental_rerun()

    # Bouton pour rafraîchir les données des startups
    with st.sidebar:
        st.subheader("Options")
        if st.button("Rafraîchir les données des startups", key="refresh_button"):
            with st.spinner("Mise à jour des données en cours..."):
                st.session_state.agent_handler.get_startup_data(force_refresh=True)
                st.success("Données mises à jour avec succès !")

        # Aide sur les commandes disponibles
        with st.expander("Aide - Exemples de questions"):
            st.markdown(f"""
            <h3 style='color: {FRENCH_TECH_COLORS['primary']}'>Exemples de questions à poser :</h3>

            <ul>
              <li>"Trouve-moi des startups dans le domaine de l'IA à La Réunion"</li>
              <li>"Quelles startups travaillent sur des solutions durables ?"</li>
              <li>"J'ai besoin d'une solution pour optimiser ma logistique, que proposez-vous ?"</li>
              <li>"Peux-tu me proposer une combinaison de startups pour un projet d'agriculture connectée ?"</li>
              <li>"Donne-moi plus de détails sur [nom de la startup]"</li>
            </ul>
            """, unsafe_allow_html=True)

    # Affichage du footer
    display_french_tech_footer()