"""
Point d'entrée principal de l'application
"""
import streamlit as st
import datetime
import os
from config import APP_NAME, FRENCH_TECH_COLORS
from ui.chat_ui import render_chat_interface
from ui.results_ui import render_results
from ui.startup_detail_ui import render_startup_detail
from ui.profile_ui import render_profile_page
from ui.admin_crawler_ui import render_crawler_admin
from ui.custom_style import apply_french_tech_style, display_french_tech_header, display_french_tech_footer
from auth.auth_handler import AuthHandler
from auth.auth_ui import render_login_page, render_user_menu
from crawler.startup_crawler import start_background_updates


def main():
    """
    Fonction principale de l'application
    """
    st.set_page_config(
        page_title="La French Tech Réunion - StartupMatcher",
        page_icon="https://lafrenchtech-lareunion.com/wp-content/uploads/2022/04/Logo_FT_LaReunion_Blanc.png.webp",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Année courante pour le footer
    if "current_year" not in st.session_state:
        st.session_state.current_year = datetime.datetime.now().year

    # Application du style La French Tech
    apply_french_tech_style()

    # Affichage de l'en-tête personnalisé
    display_french_tech_header()

    # Vérification des clés API requises
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_api_key:
        st.error("⚠️ La clé API Mistral n'est pas configurée. Veuillez ajouter MISTRAL_API_KEY dans le fichier .env")
        st.stop()

    # Démarrage des mises à jour périodiques en arrière-plan
    try:
        start_background_updates()
    except Exception as e:
        st.error(f"Erreur lors du démarrage des mises à jour en arrière-plan: {e}")
        st.info("L'application continuera à fonctionner, mais les mises à jour automatiques ne seront pas disponibles.")

    # Initialisation de la session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "selected_startups" not in st.session_state:
        st.session_state.selected_startups = []

    if "current_view" not in st.session_state:
        st.session_state.current_view = "chat"

    # Vérification de l'authentification pour l'accès à l'administration
    is_admin = False
    user = AuthHandler.get_current_user()
    if user:
        # Considérer comme administrateur certains utilisateurs (à ajuster selon vos besoins)
        admin_emails = [
            "admin@frenchtech-reunion.com",
            "contact@frenchtech-reunion.com"
        ]
        is_admin = user.get("email", "") in admin_emails

    # Navigation stylisée
    tabs = ["Chat", "Résultats", "Détails", "Profil"]

    # Ajout de l'onglet Admin pour les administrateurs
    if is_admin:
        tabs.append("Admin")

    css_tab = f"""
    <style>
    div[data-testid="stHorizontalBlock"] > div:first-child {{
        background-color: {FRENCH_TECH_COLORS["light_gray"]};
        border-radius: 10px;
        padding: 5px;
    }}
    </style>
    """
    st.markdown(css_tab, unsafe_allow_html=True)

    # Recherche de l'index courant
    tab_view_map = {
        "chat": "Chat",
        "results": "Résultats",
        "details": "Détails",
        "profile": "Profil",
        "admin": "Admin"
    }
    current_tab = tab_view_map.get(st.session_state.current_view, "Chat")

    # Si l'utilisateur n'est pas admin et que la vue est admin, rediriger vers chat
    if current_tab == "Admin" and not is_admin:
        current_tab = "Chat"
        st.session_state.current_view = "chat"

    current_tab_index = tabs.index(current_tab) if current_tab in tabs else 0

    tab_cols = st.columns(len(tabs))

    for i, (col, tab) in enumerate(zip(tab_cols, tabs)):
        with col:
            if i == current_tab_index:
                # Tab sélectionné
                st.markdown(f"""
                <div style="background-color: {FRENCH_TECH_COLORS['primary']}; color: white; padding: 10px; 
                border-radius: 5px; text-align: center; font-weight: bold; cursor: pointer;">
                {tab}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Tab non sélectionné
                if st.button(tab, key=f"tab_{tab.lower()}"):
                    # Convertir le nom de l'onglet en nom de vue
                    view_name = tab.lower()
                    st.session_state.current_view = view_name
                    st.rerun()

    # Affichage de la vue correspondante
    if st.session_state.current_view == "chat":
        render_chat_interface()
    elif st.session_state.current_view == "results":
        render_results()
    elif st.session_state.current_view == "details":
        render_startup_detail()
    elif st.session_state.current_view == "profile":
        render_profile_page()
    elif st.session_state.current_view == "admin" and is_admin:
        render_crawler_admin()
    else:
        # Redirection par défaut vers le chat
        st.session_state.current_view = "chat"
        st.rerun()


if __name__ == "__main__":
    main()