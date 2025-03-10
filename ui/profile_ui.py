"""
Interface utilisateur pour le profil utilisateur
"""
import streamlit as st
from typing import Dict, Any
from auth.auth_handler import AuthHandler
from auth.utils import update_user_profile
from config import FRENCH_TECH_COLORS
from ui.custom_style import display_french_tech_footer


def render_profile_page():
    """
    Affiche la page de profil utilisateur
    """
    user = AuthHandler.get_current_user()

    if not user:
        st.warning("Vous devez être connecté pour accéder à cette page.")
        return

    st.markdown(f"<h1 style='color: {FRENCH_TECH_COLORS['primary']}'>Mon Profil</h1>", unsafe_allow_html=True)

    # Affichage des onglets
    tab1, tab2 = st.tabs(["Informations personnelles", "Modifier mon profil"])

    # Onglet des informations personnelles
    with tab1:
        render_user_info(user)

    # Onglet de modification du profil
    with tab2:
        render_edit_profile_form(user)

    # Affichage des messages d'erreur ou de succès
    if st.session_state.get("profile_status") == "error" and st.session_state.get("profile_message"):
        st.error(st.session_state.profile_message)
        # Réinitialisation du message après affichage
        st.session_state.profile_message = None

    elif st.session_state.get("profile_status") == "success" and st.session_state.get("profile_message"):
        st.success(st.session_state.profile_message)
        # Réinitialisation du message après affichage
        st.session_state.profile_message = None

    # Bouton pour revenir au chat
    if st.button("Retour au chat"):
        st.session_state.current_view = "chat"
        st.experimental_rerun()

    # Footer
    display_french_tech_footer()


def render_user_info(user: Dict[str, Any]):
    """
    Affiche les informations de l'utilisateur

    Args:
        user: Données de l'utilisateur
    """
    st.markdown(f"<h3 style='color: {FRENCH_TECH_COLORS['primary']}'>Informations personnelles</h3>",
                unsafe_allow_html=True)

    # Conteneur principal
    with st.container():
        # Informations de base
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"<div class='user-info-card'><strong>Nom:</strong> {user['first_name']} {user['last_name']}</div>",
                unsafe_allow_html=True)
            st.markdown(f"<div class='user-info-card'><strong>Email:</strong> {user['email']}</div>",
                        unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div class='user-info-card'><strong>Entreprise:</strong> {user['company']}</div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='user-info-card'><strong>Fonction:</strong> {user['role']}</div>",
                        unsafe_allow_html=True)

        # Informations supplémentaires
        st.markdown("<hr/>", unsafe_allow_html=True)

        if "created_at" in user:
            st.markdown(f"<div class='user-info-card'><strong>Compte créé le:</strong> {user['created_at'][:10]}</div>",
                        unsafe_allow_html=True)

        if "last_login" in user and user["last_login"]:
            st.markdown(
                f"<div class='user-info-card'><strong>Dernière connexion:</strong> {user['last_login'][:10]}</div>",
                unsafe_allow_html=True)


def render_edit_profile_form(user: Dict[str, Any]):
    """
    Affiche le formulaire de modification du profil

    Args:
        user: Données de l'utilisateur
    """
    st.markdown(f"<h3 style='color: {FRENCH_TECH_COLORS['primary']}'>Modifier mon profil</h3>", unsafe_allow_html=True)

    # Formulaire de modification du profil
    with st.form("edit_profile_form"):
        # Informations personnelles
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("Prénom", value=user.get("first_name", ""), key="edit_first_name")
        with col2:
            last_name = st.text_input("Nom", value=user.get("last_name", ""), key="edit_last_name")

        # Email (non modifiable)
        st.text_input("Email", value=user.get("email", ""), disabled=True, key="edit_email")

        # Informations professionnelles
        company = st.text_input("Entreprise", value=user.get("company", ""), key="edit_company")

        # Rôle dans l'entreprise
        role_options = [
            "Acheteur",
            "Responsable innovation",
            "Directeur",
            "Chef de projet",
            "Autre"
        ]
        role = st.selectbox("Votre fonction", options=role_options,
                            index=role_options.index(user.get("role", "Autre")) if user.get(
                                "role") in role_options else 0, key="edit_role")

        # Modifier mot de passe
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("**Modifier votre mot de passe** (laissez vide pour conserver l'actuel)", unsafe_allow_html=False)

        password = st.text_input("Nouveau mot de passe", type="password", key="edit_password",
                                 help="Le mot de passe doit contenir au moins 8 caractères, dont une majuscule, une minuscule et un chiffre.")

        password_confirm = st.text_input("Confirmer le nouveau mot de passe", type="password",
                                         key="edit_password_confirm")

        # Bouton de mise à jour
        submitted = st.form_submit_button("Mettre à jour mon profil")

        if submitted:
            # Vérification de la confirmation du mot de passe
            if password and password != password_confirm:
                st.session_state.profile_status = "error"
                st.session_state.profile_message = "Les mots de passe ne correspondent pas."
                st.experimental_rerun()
                return

            # Collecte des données du formulaire
            updated_data = {
                "first_name": first_name,
                "last_name": last_name,
                "company": company,
                "role": role
            }

            # Ajout du mot de passe uniquement s'il est fourni
            if password:
                updated_data["password"] = password

            # Mise à jour du profil
            updated_user = update_user_profile(user["id"], updated_data)

            if updated_user:
                # Mise à jour de la session
                st.session_state.user = updated_user
                st.session_state.profile_status = "success"
                st.session_state.profile_message = "Votre profil a été mis à jour avec succès."
            else:
                st.session_state.profile_status = "error"
                st.session_state.profile_message = "Une erreur est survenue lors de la mise à jour de votre profil."

            st.experimental_rerun()