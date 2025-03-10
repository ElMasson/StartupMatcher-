"""
Application simplifiée qui ne dépend pas des bibliothèques hypothétiques
"""
import streamlit as st
import datetime
import os
from dotenv import load_dotenv
import random
import json
import time

# Chargement des variables d'environnement
load_dotenv()

# Configuration de l'application
st.set_page_config(
    page_title="La French Tech Réunion - StartupMatcher",
    page_icon="https://lafrenchtech-lareunion.com/wp-content/uploads/2019/08/cropped-favicon-32x32.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Couleurs de la French Tech
FRENCH_TECH_COLORS = {
    "primary": "#EF0D33",  # Rouge French Tech
    "secondary": "#1E1E1E",  # Noir
    "accent": "#3EAFF8",  # Bleu French Tech
    "light": "#FFFFFF",  # Blanc
    "light_gray": "#F5F5F5",  # Gris clair
    "dark_gray": "#555555"  # Gris foncé
}

# Styles CSS
st.markdown(f"""
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

    /* Chat messages */
    .chat-message {{
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }}

    .user-message {{
        background-color: var(--accent-color);
        color: white;
        border-top-right-radius: 0;
        align-self: flex-end;
        text-align: right;
    }}

    .assistant-message {{
        background-color: var(--light-gray);
        border-top-left-radius: 0;
        align-self: flex-start;
    }}

    /* Startup card */
    .startup-card {{
        border: 1px solid var(--light-gray);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: white;
    }}

    .startup-card:hover {{
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-color: var(--primary-color);
    }}

    .startup-name {{
        color: var(--primary-color);
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }}

    .tag {{
        background-color: var(--accent-color);
        color: white;
        border-radius: 12px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        margin-right: 0.5rem;
        display: inline-block;
    }}
</style>
""", unsafe_allow_html=True)

# En-tête
st.markdown(f"""
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
""", unsafe_allow_html=True)


# Données d'exemple pour les startups
def get_sample_startups():
    return [
        {
            "id": "startup-12345",
            "name": "EcoTech Réunion",
            "description": "Startup spécialisée dans les solutions écologiques et le développement durable à La Réunion.",
            "tags": ["Écologie", "Développement durable", "Énergie renouvelable"],
            "url": "https://ecotechreunion.com",
            "contact": "contact@ecotechreunion.com",
            "domain": "Écologie",
            "location": "Saint-Denis, La Réunion"
        },
        {
            "id": "startup-23456",
            "name": "DigitalOcean974",
            "description": "Accompagnement à la transformation numérique des entreprises réunionnaises.",
            "tags": ["Numérique", "Transformation digitale", "Conseil"],
            "url": "https://digitalocean974.re",
            "contact": "info@digitalocean974.re",
            "domain": "Numérique",
            "location": "Saint-Pierre, La Réunion"
        },
        {
            "id": "startup-34567",
            "name": "AgriTech Réunion",
            "description": "Solutions technologiques innovantes pour l'agriculture tropicale.",
            "tags": ["Agriculture", "IoT", "Data Science"],
            "url": "https://agritech-reunion.com",
            "contact": "contact@agritech-reunion.com",
            "domain": "Agriculture",
            "location": "Saint-Paul, La Réunion"
        },
        {
            "id": "startup-45678",
            "name": "MediSanté 974",
            "description": "Plateforme de télémédecine adaptée aux spécificités de La Réunion.",
            "tags": ["Santé", "E-santé", "Télémédecine"],
            "url": "https://medisante974.re",
            "contact": "contact@medisante974.re",
            "domain": "Santé",
            "location": "Saint-Denis, La Réunion"
        },
        {
            "id": "startup-56789",
            "name": "TourismTech Réunion",
            "description": "Développement d'applications et services numériques pour le tourisme local.",
            "tags": ["Tourisme", "Application mobile", "Expérience utilisateur"],
            "url": "https://tourismtech.re",
            "contact": "info@tourismtech.re",
            "domain": "Tourisme",
            "location": "Saint-Gilles, La Réunion"
        },
        {
            "id": "startup-67890",
            "name": "CyberSécurité Océan Indien",
            "description": "Services de cybersécurité pour les entreprises de la zone Océan Indien.",
            "tags": ["Cybersécurité", "Protection des données", "Audit"],
            "url": "https://cybersecurite-oi.com",
            "contact": "security@cybersecurite-oi.com",
            "domain": "Cybersécurité",
            "location": "Le Port, La Réunion"
        },
        {
            "id": "startup-78901",
            "name": "FinTech 974",
            "description": "Solutions financières innovantes adaptées au contexte insulaire.",
            "tags": ["Finance", "Blockchain", "Paiement mobile"],
            "url": "https://fintech974.com",
            "contact": "contact@fintech974.com",
            "domain": "Finance",
            "location": "Saint-Denis, La Réunion"
        },
        {
            "id": "startup-89012",
            "name": "LogisticPlus Réunion",
            "description": "Optimisation de la chaîne logistique pour les territoires insulaires.",
            "tags": ["Logistique", "Supply Chain", "Optimisation"],
            "url": "https://logisticplus.re",
            "contact": "info@logisticplus.re",
            "domain": "Logistique",
            "location": "Le Port, La Réunion"
        },
        {
            "id": "startup-90123",
            "name": "EduTech Océan Indien",
            "description": "Plateformes éducatives adaptées aux spécificités culturelles de l'Océan Indien.",
            "tags": ["Éducation", "E-learning", "Contenu local"],
            "url": "https://edutech-oi.com",
            "contact": "contact@edutech-oi.com",
            "domain": "Éducation",
            "location": "Saint-André, La Réunion"
        },
        {
            "id": "startup-01234",
            "name": "RenewEnergy Réunion",
            "description": "Développement de solutions énergétiques renouvelables adaptées au climat tropical.",
            "tags": ["Énergie", "Solaire", "Transition énergétique"],
            "url": "https://renewenergy-reunion.com",
            "contact": "info@renewenergy-reunion.com",
            "domain": "Énergie",
            "location": "Saint-Pierre, La Réunion"
        }
    ]


# Fonction simplifiée pour trouver des startups correspondant à une requête
def find_matching_startups(query, all_startups, top_k=5):
    # Recherche simple par mots-clés
    keywords = query.lower().split()

    # Calcul des scores pour chaque startup
    scored_startups = []
    for startup in all_startups:
        score = 0

        # Recherche dans le nom (plus de poids)
        name = startup.get("name", "").lower()
        for keyword in keywords:
            if keyword in name:
                score += 3

        # Recherche dans la description
        description = startup.get("description", "").lower()
        for keyword in keywords:
            if keyword in description:
                score += 2

        # Recherche dans les tags
        tags = [tag.lower() for tag in startup.get("tags", [])]
        for keyword in keywords:
            for tag in tags:
                if keyword in tag:
                    score += 2

        # Recherche dans le domaine
        domain = startup.get("domain", "").lower()
        for keyword in keywords:
            if keyword in domain:
                score += 1

        # Ajout de la startup avec son score
        scored_startups.append((startup, score))

    # Tri par score décroissant
    sorted_startups = sorted(scored_startups, key=lambda x: x[1], reverse=True)

    # Récupération des startups avec le meilleur score
    filtered_startups = [startup for startup, score in sorted_startups if score > 0]

    # Si aucune startup trouvée, retourner quelques startups aléatoires
    if not filtered_startups:
        random.shuffle(all_startups)
        return all_startups[:top_k]

    # Limitation du nombre de résultats
    return filtered_startups[:top_k]


# Fonction pour afficher une startup
def display_startup_card(startup):
    st.markdown(f"""
    <div class="startup-card">
        <div class="startup-name">{startup.get('name', 'Startup sans nom')}</div>
        <p>{startup.get('description', 'Pas de description disponible.')}</p>
        <div style="margin: 0.5rem 0;">
    """, unsafe_allow_html=True)

    # Affichage des tags
    for tag in startup.get('tags', [])[:3]:  # Limiter à 3 tags
        st.markdown(f'<span class="tag">{tag}</span>', unsafe_allow_html=True)

    st.markdown(f"""
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
            <div>
                <strong>Domaine:</strong> {startup.get('domain', 'Non spécifié')}<br>
                <strong>Localisation:</strong> {startup.get('location', 'Non spécifiée')}
            </div>
            <div>
                <a href="{startup.get('url', '#')}" target="_blank" style="color: {FRENCH_TECH_COLORS['accent']};">
                    Visiter le site web
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Fonction pour générer une réponse "IA"
def generate_response(user_query, matched_startups):
    # Simuler un délai de traitement
    time.sleep(1)

    if not matched_startups:
        return "Je n'ai pas trouvé de startups correspondant à votre recherche. Pourriez-vous préciser davantage votre besoin ?"

    # Construire une réponse basée sur les startups trouvées
    num_startups = len(matched_startups)
    startup_domains = set(startup.get("domain", "") for startup in matched_startups)

    response = f"J'ai trouvé {num_startups} startup{'s' if num_startups > 1 else ''} qui pourrai{'en' if num_startups > 1 else ''}t répondre à votre besoin"

    if startup_domains:
        response += f", principalement dans {'les domaines ' if len(startup_domains) > 1 else 'le domaine '}"
        response += f"{', '.join(sorted(list(startup_domains)))}."
    else:
        response += "."

    # Ajout de détails sur les startups
    response += "\n\nVoici un aperçu des startups les plus pertinentes :\n\n"

    for i, startup in enumerate(matched_startups[:3], 1):
        response += f"**{i}. {startup.get('name', '')}** - {startup.get('description', '')[:100]}...\n\n"

    if num_startups > 3:
        response += f"Et {num_startups - 3} autre{'s' if num_startups - 3 > 1 else ''} que vous pouvez consulter dans la liste ci-dessous."

    return response


# Initialisation des variables de session
if "messages" not in st.session_state:
    st.session_state.messages = []

if "startups" not in st.session_state:
    st.session_state.startups = get_sample_startups()

if "matched_startups" not in st.session_state:
    st.session_state.matched_startups = []

if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "logged_in": False,
        "name": "",
        "email": "",
        "company": ""
    }


# Gestion de l'authentification
def login_user():
    st.sidebar.title("Connexion")

    email = st.sidebar.text_input("Email", key="login_email")
    password = st.sidebar.text_input("Mot de passe", type="password", key="login_password")

    if st.sidebar.button("Se connecter", key="login_button"):
        # Simulation d'une vérification d'identifiants
        if email and password:
            st.session_state.user_info = {
                "logged_in": True,
                "name": "Utilisateur Test",
                "email": email,
                "company": "Entreprise Test"
            }
            st.sidebar.success("Connexion réussie!")
            st.rerun()
        else:
            st.sidebar.error("Veuillez saisir un email et un mot de passe.")


def signup_user():
    st.sidebar.title("Inscription")

    first_name = st.sidebar.text_input("Prénom", key="signup_first_name")
    last_name = st.sidebar.text_input("Nom", key="signup_last_name")
    email = st.sidebar.text_input("Email", key="signup_email")
    password = st.sidebar.text_input("Mot de passe", type="password", key="signup_password")
    company = st.sidebar.text_input("Entreprise", key="signup_company")
    role = st.sidebar.selectbox("Fonction",
                                options=["Acheteur", "Responsable innovation", "Directeur", "Chef de projet", "Autre"],
                                key="signup_role")

    terms = st.sidebar.checkbox("J'accepte les conditions d'utilisation", key="signup_terms")

    if st.sidebar.button("S'inscrire", key="signup_button"):
        if not all([first_name, last_name, email, password, company, role, terms]):
            st.sidebar.error("Veuillez remplir tous les champs et accepter les conditions d'utilisation.")
        else:
            st.session_state.user_info = {
                "logged_in": True,
                "name": f"{first_name} {last_name}",
                "email": email,
                "company": company,
                "role": role
            }
            st.sidebar.success("Inscription réussie!")
            (st.rerun())


def show_user_profile():
    st.sidebar.title("Mon Profil")

    st.sidebar.markdown(f"""
    **Nom:** {st.session_state.user_info['name']}  
    **Email:** {st.session_state.user_info['email']}  
    **Entreprise:** {st.session_state.user_info['company']}
    """)

    if st.sidebar.button("Se déconnecter", key="logout_button"):
        st.session_state.user_info = {
            "logged_in": False,
            "name": "",
            "email": "",
            "company": ""
        }
        st.rerun()


# Interface principale
if not st.session_state.user_info["logged_in"]:
    # Afficher les options de connexion/inscription
    auth_tab = st.sidebar.radio("", ["Connexion", "Inscription"], key="auth_tab")

    if auth_tab == "Connexion":
        login_user()
    else:
        signup_user()

    # Message de bienvenue
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <h1>Bienvenue sur StartupMatcher</h1>
        <p style="font-size: 1.2rem;">
            Connectez-vous ou inscrivez-vous pour découvrir les startups innovantes 
            de La Réunion qui correspondent à vos besoins.
        </p>
        <img src="https://lafrenchtech-lareunion.com/wp-content/uploads/2019/08/logo-lafrenchtech-lareunion.png" 
             alt="Logo La French Tech Réunion" style="max-width: 200px; margin: 2rem auto;">
    </div>
    """, unsafe_allow_html=True)

else:
    # Afficher le profil utilisateur
    show_user_profile()

    # Onglets principaux
    tab1, tab2 = st.tabs(["💬 Chat", "📊 Résultats"])

    with tab1:
        # Affichage de l'historique des messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div>{message["content"]}</div>
                    <div style="font-size: 0.8rem; margin-top: 0.5rem;">Vous</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <div>{message["content"]}</div>
                    <div style="font-size: 0.8rem; margin-top: 0.5rem;">Assistant</div>
                </div>
                """, unsafe_allow_html=True)

        # Zone de saisie du message
        user_query = st.text_input("Décrivez votre besoin:", key="unique_chat_input")

        if st.button("Envoyer", key="send_button"):
            if user_query:
                # Ajout du message utilisateur à l'historique
                st.session_state.messages.append({"role": "user", "content": user_query})

                # Recherche des startups correspondantes
                matched_startups = find_matching_startups(user_query, st.session_state.startups)
                st.session_state.matched_startups = matched_startups

                # Génération de la réponse
                with st.spinner("Recherche en cours..."):
                    response = generate_response(user_query, matched_startups)

                # Ajout de la réponse à l'historique
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Rechargement pour afficher les nouveaux messages
                st.rerun()

    with tab2:
        st.subheader("Startups correspondant à vos besoins")

        if not st.session_state.matched_startups:
            st.info("Aucune startup trouvée. Utilisez le chat pour décrire votre besoin.")
        else:
            # Affichage des startups trouvées
            for startup in st.session_state.matched_startups:
                display_startup_card(startup)

    # Pied de page
    st.markdown(f"""
    <footer style="margin-top: 3rem; border-top: 1px solid #ddd; padding-top: 1rem; color: #666; font-size: 0.8rem;">
        <div style="display: flex; justify-content: space-between;">
            <div>© {datetime.datetime.now().year} La French Tech Réunion - Tous droits réservés</div>
            <div>
                <a href="https://lafrenchtech-lareunion.com/" target="_blank" style="color: {FRENCH_TECH_COLORS['primary']};">
                    Site officiel
                </a>
            </div>
        </div>
    </footer>
    """, unsafe_allow_html=True)