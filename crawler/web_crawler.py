"""
Implémentation d'un crawler web robuste pour La French Tech Réunion
"""
import logging
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any, Optional
import time
import random
import urllib.parse

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Crawler:
    """
    Crawler web robuste pour le site de La French Tech Réunion
    """

    def __init__(self, base_url: str, selectors: Dict[str, str], max_pages: int = 10, delay_range: tuple = (1.0, 3.0)):
        """
        Initialisation du crawler

        Args:
            base_url: URL de base à crawler
            selectors: Sélecteurs CSS pour extraire les données
            max_pages: Nombre maximum de pages à crawler
            delay_range: Plage de délai entre les requêtes (min, max) en secondes
        """
        self.base_url = base_url
        self.selectors = selectors
        self.max_pages = max_pages
        self.delay_range = delay_range
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }

    def get_page(self, url: str, retry_count: int = 3) -> Optional[BeautifulSoup]:
        """
        Récupère le contenu d'une page web avec système de retry

        Args:
            url: URL de la page
            retry_count: Nombre de tentatives en cas d'échec

        Returns:
            Objet BeautifulSoup ou None en cas d'erreur
        """
        for attempt in range(retry_count):
            try:
                logger.info(f"Tentative de récupération de la page {url} (tentative {attempt + 1}/{retry_count})")
                response = self.session.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()

                # Vérification que le contenu est bien du HTML
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    logger.warning(f"Le contenu n'est pas du HTML: {content_type}")
                    return None

                return BeautifulSoup(response.text, "html.parser")

            except requests.RequestException as e:
                logger.error(f"Erreur lors de la tentative {attempt + 1}: {e}")
                if attempt < retry_count - 1:
                    # Attente exponentielle entre les tentatives
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    logger.info(f"Nouvelle tentative dans {wait_time:.2f} secondes...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Échec après {retry_count} tentatives pour {url}")
                    return None

        return None

    def extract_startup_data(self, element: BeautifulSoup) -> Dict[str, Any]:
        """
        Extrait les données d'une startup à partir d'un élément HTML

        Args:
            element: Élément HTML contenant les données de la startup

        Returns:
            Données extraites
        """
        data = {}

        # Extraction des données selon les sélecteurs
        for key, selector in self.selectors.items():
            if key == "startup_card":
                continue

            # Tentative d'extraction avec le sélecteur
            selected = element.select(selector)
            if selected:
                if key == "startup_name":
                    data["name"] = selected[0].get_text(strip=True)

                elif key == "startup_description":
                    data["description"] = selected[0].get_text(strip=True)

                elif key == "startup_url":
                    url = selected[0].get("href", "")
                    # Vérification si l'URL est relative et conversion en URL absolue si nécessaire
                    if url and not url.startswith(('http://', 'https://')):
                        url = urllib.parse.urljoin(self.base_url, url)
                    data["url"] = url

                elif key == "startup_contact":
                    contact_text = selected[0].get_text(strip=True)
                    # Extraction d'email si présent
                    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', contact_text)
                    if email_match:
                        data["contact"] = email_match.group(0)
                    else:
                        data["contact"] = contact_text

                elif key == "startup_tags":
                    # Extraction des tags
                    tags_text = selected[0].get_text(strip=True)
                    tags = [tag.strip() for tag in tags_text.split(",")]
                    # Nettoyage des tags vides
                    tags = [tag for tag in tags if tag]
                    data["tags"] = tags

                elif key == "startup_domain":
                    data["domain"] = selected[0].get_text(strip=True)

                elif key == "startup_location":
                    data["location"] = selected[0].get_text(strip=True)

        # Génération d'un ID unique basé sur le nom
        if "name" in data:
            import hashlib
            name_hash = hashlib.md5(data["name"].encode()).hexdigest()[:8]
            data["id"] = f"startup-{name_hash}"

        # Si aucun domaine spécifié, tenter de le déduire des tags
        if "domain" not in data and "tags" in data and data["tags"]:
            # Utiliser le premier tag comme domaine par défaut
            data["domain"] = data["tags"][0]

        # Localisation par défaut si non spécifiée
        if "location" not in data:
            data["location"] = "La Réunion"

        # Normalisation des données
        for key in ["name", "description", "url", "contact", "domain", "location"]:
            if key in data and isinstance(data[key], str):
                data[key] = data[key].strip()

        return data

    def crawl(self) -> List[Dict[str, Any]]:
        """
        Exécute le crawl et extrait les données des startups

        Returns:
            Liste des données des startups
        """
        startups_data = []

        # Page initiale
        current_url = self.base_url
        pages_crawled = 0

        while current_url and pages_crawled < self.max_pages:
            logger.info(f"Crawling de la page {pages_crawled + 1}: {current_url}")

            soup = self.get_page(current_url)
            if not soup:
                break

            # Extraction des cartes de startups
            startup_cards = soup.select(self.selectors.get("startup_card", ".startup-card"))
            logger.info(f"Trouvé {len(startup_cards)} startups sur cette page")

            # Extraction des données pour chaque startup
            for card in startup_cards:
                startup_data = self.extract_startup_data(card)
                if startup_data and "name" in startup_data:  # Vérification que les données essentielles sont présentes
                    startups_data.append(startup_data)
                    logger.info(f"Startup extraite: {startup_data.get('name', 'Sans nom')}")

            # Recherche de la page suivante avec gestion des différents formats de pagination
            next_page = None

            # Différents types de sélecteurs de pagination à essayer
            pagination_selectors = [
                "a.next-page",
                "a.pagination-next",
                ".pagination a[aria-label='Next']",
                ".nav-links a.next",
                ".pagination-next a",
                ".pagination a:contains('Suivant')",
                "a:contains('Suivant')",
                "a[rel='next']"
            ]

            for selector in pagination_selectors:
                next_page = soup.select_one(selector)
                if next_page and "href" in next_page.attrs:
                    break

            if next_page and "href" in next_page.attrs:
                # Construction de l'URL complète si nécessaire
                next_url = next_page["href"]
                if not next_url.startswith(("http://", "https://")):
                    next_url = urllib.parse.urljoin(current_url, next_url)

                current_url = next_url
            else:
                # Aucun lien "suivant" trouvé
                logger.info("Aucun lien vers une page suivante trouvé. Fin du crawling.")
                current_url = None

            pages_crawled += 1

            # Pause pour éviter de surcharger le serveur
            if current_url:
                delay = random.uniform(self.delay_range[0], self.delay_range[1])
                logger.info(f"Pause de {delay:.2f} secondes avant la prochaine page...")
                time.sleep(delay)

        logger.info(f"Crawling terminé. {len(startups_data)} startups trouvées au total.")
        return startups_data

    def get_sample_data(self) -> List[Dict[str, Any]]:
        """
        Génère des données d'exemple pour les startups (comme fallback)

        Returns:
            Liste des données d'exemple
        """
        logger.info("Génération de données d'exemple pour les startups...")

        # Définition des données d'exemple
        sample_data = [
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

        return sample_data