"""
Interface utilisateur pour l'authentification
"""
import streamlit as st
from typing import Dict, Any
from auth.auth_handler import AuthHandler
from config import FRENCH_TECH_COLORS
from ui.custom_style import display_french_tech_footer


def render_login_page():
    """
    Affiche la page de connexion/inscription
    """
    # Initialisation de l'état d'authentification
    AuthHandler.initialize_session()

    # Conteneur principal
    auth_container = st.container()

    with auth_container:
        # Onglets pour switcher entre connexion et inscription
        tab1, tab2 = st.tabs(["Connexion", "Inscription"])

        # Formulaire de connexion
        with tab1:
            render_signin_form()

        # Formulaire d'inscription
        with tab2:
            render_signup_form()

    # Affichage des messages d'erreur ou de succès
    if st.session_state.auth_status == "error" and st.session_state.auth_message:
        st.error(st.session_state.auth_message)
        # Réinitialisation du message après affichage
        st.session_state.auth_message = None

    elif st.session_state.auth_status == "success" and st.session_state.auth_message:
        st.success(st.session_state.auth_message)
        # Réinitialisation du message après affichage
        st.session_state.auth_message = None

    # Footer
    display_french_tech_footer()


def render_signin_form():
    """
    Affiche le formulaire de connexion
    """
    st.markdown(f"<h2 style='color: {FRENCH_TECH_COLORS['primary']}'>Connexion</h2>", unsafe_allow_html=True)

    # Formulaire de connexion
    with st.form("signin_form"):
        # Champs du formulaire
        email = st.text_input("Email", key="signin_email")
        password = st.text_input("Mot de passe", type="password", key="signin_password")

        # Bouton de connexion
        submitted = st.form_submit_button("Se connecter")

        if submitted:
            # Tentative de connexion
            success, message = AuthHandler.signin(email, password)

            if success:
                st.session_state.auth_status = "success"
                st.session_state.auth_message = message
                st.experimental_rerun()
            else:
                st.session_state.auth_status = "error"
                st.session_state.auth_message = message
                st.experimental_rerun()


def render_signup_form():
    """
    Affiche le formulaire d'inscription
    """
    st.markdown(f"<h2 style='color: {FRENCH_TECH_COLORS['primary']}'>Inscription</h2>", unsafe_allow_html=True)

    # Formulaire d'inscription
    with st.form("signup_form"):
        # Informations personnelles
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("Prénom", key="signup_first_name")
        with col2:
            last_name = st.text_input("Nom", key="signup_last_name")

        # Email et mot de passe
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Mot de passe", type="password", key="signup_password",
                                 help="Le mot de passe doit contenir au moins 8 caractères, dont une majuscule, une minuscule et un chiffre.")

        # Informations professionnelles
        company = st.text_input("Entreprise", key="signup_company")

        # Rôle dans l'entreprise
        role_options = [
            "Acheteur",
            "Responsable innovation",
            "Directeur",
            "Chef de projet",
            "Autre"
        ]
        role = st.selectbox("Votre fonction", options=role_options, key="signup_role")

        # Conditions d'utilisation
        terms_agreed = st.checkbox("J'accepte les conditions d'utilisation", key="signup_terms")

        # Bouton d'inscription
        submitted = st.form_submit_button("S'inscrire")

        if submitted:
            if not terms_agreed:
                st.session_state.auth_status = "error"
                st.session_state.auth_message = "Vous devez accepter les conditions d'utilisation."
                st.experimental_rerun()
                return

            # Collecte des données du formulaire
            signup_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": password,
                "company": company,
                "role": role
            }

            # Tentative d'inscription
            success, message = AuthHandler.signup(signup_data)

            if success:
                st.session_state.auth_status = "success"
                st.session_state.auth_message = message
                st.experimental_rerun()
            else:
                st.session_state.auth_status = "error"
                st.session_state.auth_message = message
                st.experimental_rerun()


def render_user_profile():
    """
    Affiche le profil de l'utilisateur connecté
    """
    user = AuthHandler.get_current_user()

    if not user:
        st.warning("Vous n'êtes pas connecté.")
        return

    st.markdown(f"<h2 style='color: {FRENCH_TECH_COLORS['primary']}'>Profil utilisateur</h2>", unsafe_allow_html=True)

    # Affichage des informations de l'utilisateur
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Nom:** {user['first_name']} {user['last_name']}")
        st.markdown(f"**Email:** {user['email']}")

    with col2:
        st.markdown(f"**Entreprise:** {user['company']}")
        st.markdown(f"**Fonction:** {user['role']}")

    # Bouton de déconnexion
    if st.button("Se déconnecter"):
        success, message = AuthHandler.signout()

        if success:
            st.session_state.auth_status = "success"
            st.session_state.auth_message = message
            st.experimental_rerun()
        else:
            st.session_state.auth_status = "error"
            st.session_state.auth_message = message


def render_user_menu():
    """
    Affiche un menu utilisateur dans la barre latérale
    """
    user = AuthHandler.get_current_user()

    if user:
        st.sidebar.markdown(
            f"<div style='padding: 10px; background-color: {FRENCH_TECH_COLORS['light_gray']}; border-radius: 5px;'>",
            unsafe_allow_html=True)
        st.sidebar.markdown(f"**Connecté en tant que:**")
        st.sidebar.markdown(f"{user['first_name']} {user['last_name']}")
        st.sidebar.markdown(f"*{user['company']}*")

        if st.sidebar.button("Mon profil"):
            st.session_state.current_view = "profile"
            st.experimental_rerun()

        if st.sidebar.button("Se déconnecter"):
            AuthHandler.signout()
            st.experimental_rerun()

        st.sidebar.markdown("</div>", unsafe_allow_html=True)