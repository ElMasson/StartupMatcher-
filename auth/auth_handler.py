"""
Gestion de l'authentification
"""
import logging
import streamlit as st
from typing import Dict, Any, Optional, Tuple
from auth.utils import (
    validate_signup_data, create_user, verify_login,
    generate_token, verify_token, find_user_by_email
)

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AuthHandler:
    """
    Gestionnaire d'authentification
    """

    @staticmethod
    def initialize_session():
        """
        Initialise les variables de session liées à l'authentification
        """
        if "user" not in st.session_state:
            st.session_state.user = None

        if "auth_token" not in st.session_state:
            st.session_state.auth_token = None

        if "auth_status" not in st.session_state:
            st.session_state.auth_status = None

        if "auth_message" not in st.session_state:
            st.session_state.auth_message = None

    @staticmethod
    def check_authentication() -> bool:
        """
        Vérifie si l'utilisateur est authentifié

        Returns:
            True si l'utilisateur est authentifié, False sinon
        """
        # Initialisation des variables de session
        AuthHandler.initialize_session()

        # Si l'utilisateur est déjà authentifié dans la session
        if st.session_state.user:
            return True

        # Vérification du token s'il existe
        if st.session_state.auth_token:
            user = verify_token(st.session_state.auth_token)
            if user:
                st.session_state.user = user
                return True

        return False

    @staticmethod
    def signup(data: Dict[str, str]) -> Tuple[bool, str]:
        """
        Inscription d'un nouvel utilisateur

        Args:
            data: Données d'inscription

        Returns:
            Tuple (succès, message)
        """
        # Validation des données
        validation_error = validate_signup_data(data)
        if validation_error:
            return False, validation_error

        # Vérification si l'email existe déjà
        if find_user_by_email(data["email"]):
            return False, "Cette adresse email est déjà utilisée."

        try:
            # Création de l'utilisateur
            user = create_user(data)

            # Génération du token
            token = generate_token(user["id"])

            # Mise à jour de la session
            st.session_state.user = user
            st.session_state.auth_token = token
            st.session_state.auth_status = "success"
            st.session_state.auth_message = "Inscription réussie."

            logger.info(f"Nouvel utilisateur inscrit: {user['email']}")

            return True, "Inscription réussie."

        except Exception as e:
            logger.error(f"Erreur lors de l'inscription: {e}")
            return False, f"Une erreur est survenue lors de l'inscription: {str(e)}"

    @staticmethod
    def signin(email: str, password: str) -> Tuple[bool, str]:
        """
        Connexion d'un utilisateur

        Args:
            email: Adresse email
            password: Mot de passe

        Returns:
            Tuple (succès, message)
        """
        if not email or not password:
            return False, "Veuillez saisir votre email et votre mot de passe."

        try:
            # Vérification des identifiants
            user = verify_login(email, password)

            if not user:
                return False, "Email ou mot de passe incorrect."

            # Génération du token
            token = generate_token(user["id"])

            # Mise à jour de la session
            st.session_state.user = user
            st.session_state.auth_token = token
            st.session_state.auth_status = "success"
            st.session_state.auth_message = "Connexion réussie."

            logger.info(f"Utilisateur connecté: {user['email']}")

            return True, "Connexion réussie."

        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            return False, f"Une erreur est survenue lors de la connexion: {str(e)}"

    @staticmethod
    def signout() -> Tuple[bool, str]:
        """
        Déconnexion de l'utilisateur

        Returns:
            Tuple (succès, message)
        """
        try:
            # Réinitialisation de la session
            st.session_state.user = None
            st.session_state.auth_token = None
            st.session_state.auth_status = None
            st.session_state.auth_message = None

            logger.info("Utilisateur déconnecté")

            return True, "Déconnexion réussie."

        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            return False, f"Une erreur est survenue lors de la déconnexion: {str(e)}"

    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """
        Récupère les informations de l'utilisateur actuellement connecté

        Returns:
            Informations de l'utilisateur ou None si non connecté
        """
        if AuthHandler.check_authentication():
            return st.session_state.user
        return None

    @staticmethod
    def require_auth(page_func):
        """
        Décorateur pour protéger une page avec authentification

        Args:
            page_func: Fonction de rendu de la page

        Returns:
            Fonction wrapper
        """

        def wrapper(*args, **kwargs):
            if AuthHandler.check_authentication():
                return page_func(*args, **kwargs)
            else:
                from auth.auth_ui import render_login_page
                render_login_page()

        return wrapper