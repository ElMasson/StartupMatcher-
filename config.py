"""
Configuration globale de l'application
"""
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration générale
APP_NAME = "French Tech Réunion - StartupMatcher"
VERSION = "1.0.0"

# Configuration du branding La French Tech
FRENCH_TECH_COLORS = {
    "primary": "#EF0D33",     # Rouge French Tech
    "secondary": "#1E1E1E",   # Noir
    "accent": "#3EAFF8",      # Bleu French Tech
    "light": "#FFFFFF",       # Blanc
    "light_gray": "#F5F5F5",  # Gris clair
    "dark_gray": "#555555"    # Gris foncé
}

# URLs
STARTUP_URL = "https://lafrenchtech-lareunion.com/annuaire/"

# Configuration de Firecrawl
FIRECRAWL_CONFIG = {
    "url": STARTUP_URL,
    "selectors": {
        "startup_card": ".startup-item, .startup-card, .directory-item, .company-item",
        "startup_name": ".startup-name, .directory-title, .company-name, h3, h2",
        "startup_description": ".startup-description, .directory-excerpt, .company-description, .description, p",
        "startup_url": ".startup-url, .directory-website, .company-website, a.website, a[href*='http']",
        "startup_contact": ".startup-contact, .directory-email, .company-email, .contact-info, a[href*='mailto']",
        "startup_tags": ".startup-tags, .directory-categories, .company-tags, .tags, .categories",
        "startup_domain": ".startup-domain, .directory-sector, .company-sector, .domain, .sector",
        "startup_location": ".startup-location, .directory-location, .company-location, .location"
    },
    "max_pages": 15,  # Augmenté pour capturer plus de pages
    "cache": {
        "enabled": True,
        "max_age_days": 1,  # Un jour de validité pour le cache standard
        "max_age_error_hours": 1,  # Une heure en cas d'erreur
        "max_age_fallback_hours": 4  # Quatre heures en mode fallback
    }
}

# Configuration de Docling
DOCLING_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "embedding_model": "text-embedding-3-small"
}

# Configuration du LLM
LLM_CONFIG = {
    "model": os.getenv("LLM_MODEL", "mistral-large-latest"),
    "temperature": 0.2,
    "max_tokens": 4000
}

# Configuration des agents
AGENT_CONFIG = {
    "system_prompt": """Vous êtes un agent spécialisé dans la mise en relation entre des acheteurs 
    de grands groupes ou de collectivités et des startups innovantes. Votre mission est d'analyser 
    les besoins exprimés et de recommander les startups les plus pertinentes.""",
    "allow_delegation": True,
    "verbose": True,
    "step_callback": False
}