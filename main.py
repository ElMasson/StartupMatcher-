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
from ui.custom_style import apply_french_tech_style, display_french_tech_header, display_french_tech_footer
from auth.auth_handler import AuthHandler
from auth.auth_ui import render_login_page, render_user_menu


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

    # Initialisation de la session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "selected_startups" not in st.session_state:
        st.session_state.selected_startups = []

    if "current_view" not in st.session_state:
        st.session_state.current_view = "chat"

    # Navigation stylisée
    tabs = ["Chat", "Résultats", "Détails"]

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

    tab_cols = st.columns(len(tabs))
    current_tab_index = tabs.index(st.session_state.current_view.capitalize())

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
                    st.session_state.current_view = tab.lower()
                    st.experimental_rerun()

        # Affichage de la vue correspondante
        if st.session_state.current_view == "chat":
            render_chat_interface()
        elif st.session_state.current_view == "results":
            render_results()
        elif st.session_state.current_view == "details":
            render_startup_detail()
        elif st.session_state.current_view == "profile":
            render_profile_page()


if __name__ == "__main__":
    main()