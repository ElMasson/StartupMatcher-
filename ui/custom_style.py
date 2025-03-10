"""
Styles personnalisés pour l'application
"""
import streamlit as st
from config import FRENCH_TECH_COLORS


def apply_french_tech_style():
    """
    Applique le style La French Tech à l'application
    """
    french_tech_css = f"""
    <style>
        /* Couleurs principales */
        :root {{
            --primary-color: {FRENCH_TECH_COLORS["primary"]};
            --secondary-color: {FRENCH_TECH_COLORS["secondary"]};
            --accent-color: {FRENCH_TECH_COLORS["accent"]};
            --light-color: {FRENCH_TECH_COLORS["light"]};
            --light-gray: {FRENCH_TECH_COLORS["light_gray"]};
            --dark-gray: {FRENCH_TECH_COLORS["dark_gray"]};
        }}

        /* En-tête */
        .stApp header {{
            background-color: var(--secondary-color);
            border-bottom: 2px solid var(--primary-color);
        }}

        /* Titre principal */
        h1 {{
            color: var(--primary-color) !important;
            font-weight: 700 !important;
        }}

        /* Sous-titres */
        h2, h3 {{
            color: var(--secondary-color) !important;
            font-weight: 600 !important;
        }}

        /* Boutons */
        .stButton>button {{
            background-color: var(--primary-color) !important;
            color: var(--light-color) !important;
            border: none !important;
            border-radius: 5px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }}

        .stButton>button:hover {{
            background-color: var(--accent-color) !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
        }}

        /* Conteneurs */
        .stApp {{
            background-color: var(--light-color);
        }}

        /* Chat messages */
        .stChatMessage {{
            border-radius: 10px !important;
            border: 1px solid var(--light-gray);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}

        /* Avatar utilisateur */
        .stChatMessage.user .stChatMessageContent {{
            background-color: var(--accent-color) !important;
            color: var(--light-color) !important;
        }}

        /* Avatar assistant */
        .stChatMessage.assistant .stChatMessageContent {{
            background-color: var(--light-gray) !important;
            color: var(--secondary-color) !important;
            border-left: 3px solid var(--primary-color) !important;
        }}

        /* Navigation */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
            background-color: var(--light-gray);
            border-radius: 5px;
            padding: 0.2rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: var(--primary-color) !important;
            color: var(--light-color) !important;
        }}

        /* Barre latérale */
        [data-testid="stSidebar"] {{
            background-color: var(--light-gray) !important;
            border-right: 1px solid var(--light-gray);
        }}

        [data-testid="stSidebar"] h2 {{
            color: var(--primary-color) !important;
        }}

        /* Cards */
        .startup-card {{
            border: 1px solid var(--light-gray);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }}

        .startup-card:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border-color: var(--primary-color);
        }}

        /* Tags */
        .tag {{
            background-color: var(--accent-color);
            color: var(--light-color);
            padding: 0.2rem 0.6rem;
            border-radius: 15px;
            font-size: 0.8rem;
            margin-right: 0.5rem;
            display: inline-block;
            margin-bottom: 0.3rem;
        }}

        /* Footers */
        footer {{
            border-top: 1px solid var(--light-gray);
            padding-top: 1rem;
            color: var(--dark-gray);
            font-size: 0.85rem;
        }}
    </style>
    """

    # Injection du CSS
    st.markdown(french_tech_css, unsafe_allow_html=True)


def display_french_tech_header():
    """
    Affiche un en-tête personnalisé avec le logo La French Tech
    """
    logo_html = f"""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <img src="https://lafrenchtech-lareunion.com/wp-content/uploads/2019/08/logo-lafrenchtech-lareunion.png" 
             alt="Logo La French Tech Réunion" 
             style="height: 60px; margin-right: 1rem;">
        <div>
            <h2 style="color: {FRENCH_TECH_COLORS['primary']}; margin-bottom: 0;">StartupMatcher</h2>
            <p style="color: {FRENCH_TECH_COLORS['dark_gray']}; margin-top: 0;">
                Trouvez les startups innovantes qui correspondent à vos besoins
            </p>
        </div>
    </div>
    """

    st.markdown(logo_html, unsafe_allow_html=True)


def display_french_tech_footer():
    """
    Affiche un pied de page personnalisé
    """
    footer_html = f"""
    <footer>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2rem;">
            <div>
                <p>© {st.session_state.get('current_year', '2023')} La French Tech Réunion - Tous droits réservés</p>
            </div>
            <div>
                <a href="https://lafrenchtech-lareunion.com/" target="_blank" 
                   style="color: {FRENCH_TECH_COLORS['primary']}; text-decoration: none; margin: 0 1rem;">
                   Site officiel
                </a>
                <a href="https://lafrenchtech-lareunion.com/annuaire/" target="_blank" 
                   style="color: {FRENCH_TECH_COLORS['primary']}; text-decoration: none; margin: 0 1rem;">
                   Annuaire complet
                </a>
            </div>
        </div>
    </footer>
    """

    st.markdown(footer_html, unsafe_allow_html=True)


def display_tag(tag, key=None):
    """
    Affiche un tag avec le style French Tech

    Args:
        tag: Texte du tag
        key: Clé unique pour le composant (optionnel)
    """
    tag_html = f"""
    <span class="tag" key="{key or tag}">{tag}</span>
    """

    st.markdown(tag_html, unsafe_allow_html=True)


def display_startup_card_styled(startup, detailed=False):
    """
    Affiche une carte startup stylisée

    Args:
        startup: Données de la startup
        detailed: Affichage détaillé ou non
    """
    name = startup.get("name", "Startup sans nom")
    description = startup.get("description", "Pas de description disponible.")
    tags = startup.get("tags", [])
    domain = startup.get("domain", "Non spécifié")
    location = startup.get("location", "Non spécifiée")
    url = startup.get("url", "")
    contact = startup.get("contact", "")

    card_html = f"""
    <div class="startup-card">
        <h3 style="color: {FRENCH_TECH_COLORS['primary']}; margin-top: 0;">{name}</h3>
        <p>{description}</p>

        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0;">
    """

    # Ajout des tags
    for tag in tags[:5]:  # Limiter à 5 tags maximum
        card_html += f'<span class="tag">{tag}</span>'

    if len(tags) > 5:
        card_html += f'<span class="tag">+{len(tags) - 5}</span>'

    card_html += """
        </div>

        <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
            <div>
    """

    # Informations de base
    if domain:
        card_html += f'<p><strong>Domaine:</strong> {domain}</p>'

    if location:
        card_html += f'<p><strong>Localisation:</strong> {location}</p>'

    card_html += """
            </div>
            <div>
    """

    # Informations de contact
    if detailed and contact:
        card_html += f'<p><strong>Contact:</strong> {contact}</p>'

    if url:
        card_html += f'<p><a href="{url}" target="_blank" style="color: {FRENCH_TECH_COLORS["accent"]};">Visiter le site web</a></p>'

    card_html += """
            </div>
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)