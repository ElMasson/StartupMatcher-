"""
Crawler spécifique pour le site de La French Tech Réunion
"""
import logging
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any, Optional
import time
import random
import hashlib
import urllib.parse
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrenchTechReunionCrawler:
    """
    Crawler spécifique pour le site La French Tech Réunion
    """

    def __init__(self, base_url="https://lafrenchtech-lareunion.com/annuaire/"):
        """
        Initialisation du crawler

        Args:
            base_url: URL de l'annuaire
        """
        self.base_url = base_url
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
        Récupère une page web avec système de retry

        Args:
            url: URL de la page
            retry_count: Nombre de tentatives

        Returns:
            Objet BeautifulSoup ou None en cas d'erreur
        """
        for attempt in range(retry_count):
            try:
                logger.info(f"Tentative de récupération de la page {url} (tentative {attempt + 1}/{retry_count})")

                # Ajout d'un délai pour éviter d'être bloqué
                time.sleep(random.uniform(1.0, 3.0))

                response = self.session.get(url, headers=self.headers, timeout=15)

                # Afficher l'état de la réponse pour le débogage
                logger.info(f"Statut de la réponse: {response.status_code}")

                # Stocker les 1000 premiers caractères pour le débogage
                content_preview = response.text[:1000] if response.text else "Contenu vide"
                logger.info(f"Aperçu du contenu: {content_preview}")

                response.raise_for_status()

                # Vérifier que le contenu est bien du HTML
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    logger.warning(f"Le contenu n'est pas du HTML: {content_type}")
                    return None

                return BeautifulSoup(response.text, "html.parser")

            except requests.RequestException as e:
                logger.error(f"Erreur lors de la tentative {attempt + 1}: {e}")
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    logger.info(f"Nouvelle tentative dans {wait_time:.2f} secondes...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Échec après {retry_count} tentatives pour {url}")
                    return None

        return None

    def crawl_startups(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les startups de l'annuaire en parcourant toutes les pages

        Returns:
            Liste des startups
        """
        startups = []

        # Commencer par la page principale de l'annuaire
        current_page = 1
        max_pages = 10  # Maximum de pages à parcourir pour éviter une boucle infinie

        while current_page <= max_pages:
            # Construire l'URL de la page actuelle
            if current_page == 1:
                page_url = self.base_url
            else:
                page_url = f"{self.base_url}page/{current_page}/"

            logger.info(f"Récupération de la page {current_page}: {page_url}")
            soup = self.get_page(page_url)

            if not soup:
                logger.error(f"Impossible de récupérer la page {current_page}")
                # Si on ne peut pas récupérer cette page, on suppose qu'on a atteint la dernière page
                break

            # Recherche des éléments de l'annuaire
            found_elements = False
            startup_elements = []

            # Tentatives avec plusieurs sélecteurs courants
            for selector in [
                "article",
                "div.startup",
                "div.directory-item",
                "div.annuaire-item",
                ".elementor-post",
                ".elementor-grid-item",
                ".elementor-widget-wrap",
                ".elementor-element",
                ".startup-item",
                ".company-item",
                ".directory-listing .item",
                ".elementor-posts-container article"
            ]:
                elements = soup.select(selector)
                if elements:
                    logger.info(f"Trouvé {len(elements)} éléments avec le sélecteur '{selector}' sur la page {current_page}")
                    startup_elements = elements
                    found_elements = True
                    break

            # Recherche de liens vers des startups spécifiques
            startup_links = []

            # Si on n'a pas trouvé d'éléments directs, chercher des liens
            if not found_elements:
                logger.info(f"Recherche de liens vers des startups sur la page {current_page}")

                # Chercher tous les liens qui pourraient pointer vers des startups individuelles
                links = soup.select("a")

                for link in links:
                    href = link.get("href", "")
                    text = link.get_text(strip=True)

                    # Filtrer les liens qui ressemblent à des liens vers des startups
                    if href and href.startswith(("http://", "https://")) and text and len(text) > 3:
                        # Éviter les liens vers des pages qui ne sont clairement pas des startups
                        if not any(skip in href.lower() for skip in ["wordpress", "wp-", "admin", "login", "facebook", "twitter", "linkedin"]):
                            startup_links.append(href)

            # Si on a trouvé des éléments directs sur la page
            if found_elements and startup_elements:
                for element in startup_elements:
                    # D'abord essayer d'extraire le lien vers la page détaillée
                    detail_link = None
                    link_element = element.select_one("a[href]")

                    if link_element and link_element.has_attr("href"):
                        href = link_element["href"]
                        # S'assurer que c'est une URL complète
                        if not href.startswith(("http://", "https://")):
                            href = urllib.parse.urljoin(page_url, href)
                        detail_link = href

                    # Si on a un lien vers la page détaillée, l'utiliser pour obtenir plus d'informations
                    if detail_link:
                        logger.info(f"Visite de la page détaillée: {detail_link}")
                        detail_soup = self.get_page(detail_link)

                        if detail_soup:
                            startup_data = self.extract_startup_data_from_page(detail_soup, detail_link)
                            if startup_data:
                                startups.append(startup_data)
                                continue

                    # Si on n'a pas pu obtenir de détails, extraire les données de base
                    startup_data = self.extract_startup_data(element)
                    if startup_data:
                        startups.append(startup_data)

            # Si on a trouvé des liens vers des startups, les visiter
            elif startup_links:
                for link in startup_links[:10]:  # Limiter à 10 liens par page pour éviter de surcharger
                    logger.info(f"Visite de la page de startup: {link}")
                    startup_soup = self.get_page(link)

                    if startup_soup:
                        startup_data = self.extract_startup_data_from_page(startup_soup, link)
                        if startup_data:
                            startups.append(startup_data)

            # Vérifier si une page suivante existe
            next_page_exists = False

            # Vérifier si le bouton "page suivante" existe
            next_link_elements = soup.select("a.next, a.next-page, a.pagination-next, .nav-links a.next, a[rel='next']")
            if next_link_elements:
                next_page_exists = True

            # Vérifier aussi si un lien vers la page n+1 existe
            page_links = soup.select("a.page-numbers, .pagination a, .nav-links a")
            for link in page_links:
                if link.get_text(strip=True) == str(current_page + 1):
                    next_page_exists = True
                    break

            # Si aucun élément de pagination n'a été trouvé, mais qu'on a trouvé des éléments sur cette page,
            # essayer quand même la page suivante (car la pagination peut être implémentée de façon non standard)
            if not next_page_exists and (found_elements or startup_links):
                # Essayer de passer à la page suivante quand même, mais seulement si on a trouvé quelque chose sur cette page
                next_page_exists = True

            # Passer à la page suivante ou terminer
            if next_page_exists:
                current_page += 1
                # Pause pour éviter de surcharger le serveur
                time.sleep(random.uniform(1.5, 3.0))
            else:
                logger.info(f"Aucune page suivante détectée après la page {current_page}")
                break

        logger.info(f"Récupération terminée: {len(startups)} startups trouvées sur {current_page} pages")
        return startups

    def extract_startup_data(self, element) -> Optional[Dict[str, Any]]:
        """
        Extrait les données d'une startup à partir d'un élément HTML

        Args:
            element: Élément BeautifulSoup contenant les données

        Returns:
            Dictionnaire des données ou None si impossible à extraire
        """
        startup_data = {}

        # Essayer d'extraire le nom
        name_element = element.select_one("h2, h3, h4, .entry-title, .startup-name, .title")
        if name_element:
            name = name_element.get_text(strip=True)
            startup_data["name"] = name
            # Générer un ID basé sur le nom
            name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
            startup_data["id"] = f"startup-{name_hash}"
        else:
            # Si on ne trouve pas de nom, ce n'est probablement pas une startup
            return None

        # Essayer d'extraire la description
        description_element = element.select_one("p, .description, .excerpt, .content, .summary")
        if description_element:
            startup_data["description"] = description_element.get_text(strip=True)
        else:
            startup_data["description"] = "Aucune description disponible"

        # Essayer d'extraire l'URL
        url_element = element.select_one("a[href*='http'], .website, .url")
        if url_element and url_element.has_attr("href"):
            startup_data["url"] = url_element["href"]
        else:
            startup_data["url"] = ""

        # Essayer d'extraire les tags ou le domaine
        tags_element = element.select_one(".tags, .categories, .domain, .sector")
        if tags_element:
            tags_text = tags_element.get_text(strip=True)
            tags = [tag.strip() for tag in tags_text.split(",")]
            startup_data["tags"] = tags

            # Utiliser le premier tag comme domaine si présent
            if tags:
                startup_data["domain"] = tags[0]
            else:
                startup_data["domain"] = "Technologie"
        else:
            startup_data["tags"] = []
            startup_data["domain"] = "Technologie"

        # Essayer d'extraire la localisation
        location_element = element.select_one(".location, .address")
        if location_element:
            startup_data["location"] = location_element.get_text(strip=True)
        else:
            startup_data["location"] = "La Réunion"

        # Essayer d'extraire le contact (email)
        contact_element = element.select_one("a[href^='mailto:'], .email, .contact")
        if contact_element:
            if contact_element.has_attr("href") and contact_element["href"].startswith("mailto:"):
                startup_data["contact"] = contact_element["href"][7:]  # Enlever "mailto:"
                startup_data["email"] = contact_element["href"][7:]
            else:
                startup_data["contact"] = contact_element.get_text(strip=True)

                # Essayer d'extraire un email du texte
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', startup_data["contact"])
                if email_match:
                    startup_data["email"] = email_match.group(0)
        else:
            startup_data["contact"] = ""

        # Valeurs par défaut pour les champs manquants
        if "email" not in startup_data:
            startup_data["email"] = ""

        startup_data["phone"] = ""
        startup_data["ceo"] = ""
        startup_data["year_founded"] = ""
        startup_data["employee_count"] = ""
        startup_data["logo_url"] = ""

        # Vérifier si on a au moins les informations minimales
        if "name" in startup_data and "description" in startup_data:
            return startup_data
        else:
            return None

    def extract_startup_data_from_page(self, soup, url: str) -> Optional[Dict[str, Any]]:
        """
        Extrait les données d'une startup depuis sa page dédiée

        Args:
            soup: Objet BeautifulSoup de la page
            url: URL de la page

        Returns:
            Dictionnaire des données ou None si impossible à extraire
        """
        startup_data = {}

        # Essayer d'extraire le nom (généralement dans le titre principal)
        title_element = soup.select_one("h1, .entry-title, .page-title")
        if title_element:
            name = title_element.get_text(strip=True)
            startup_data["name"] = name
            # Générer un ID basé sur le nom
            name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
            startup_data["id"] = f"startup-{name_hash}"
        else:
            # Si on ne trouve pas de nom dans un h1, chercher dans les h2
            title_element = soup.select_one("h2")
            if title_element:
                name = title_element.get_text(strip=True)
                startup_data["name"] = name
                name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
                startup_data["id"] = f"startup-{name_hash}"
            else:
                # Si on ne trouve toujours pas de nom, ce n'est probablement pas une page de startup
                return None

        # Essayer d'extraire la description (paragraphes après le titre)
        # Prendre le premier paragraphe ou div avec du texte substantiel après le h1/h2
        description_candidates = soup.select("p, .description, .content")
        for candidate in description_candidates:
            text = candidate.get_text(strip=True)
            if len(text) > 50:  # On cherche un texte assez long pour être une description
                startup_data["description"] = text
                break

        if "description" not in startup_data:
            startup_data["description"] = "Aucune description disponible"

        # L'URL est celle de la page
        startup_data["url"] = url

        # Essayer d'extraire les tags ou catégories
        tags_elements = soup.select(".tags a, .categories a, .domain a, .sector a, .tag, .category")
        if tags_elements:
            tags = [tag.get_text(strip=True) for tag in tags_elements]
            startup_data["tags"] = [tag for tag in tags if tag]  # Filtrer les tags vides

            # Utiliser le premier tag comme domaine si présent
            if startup_data["tags"]:
                startup_data["domain"] = startup_data["tags"][0]
            else:
                startup_data["domain"] = "Technologie"
        else:
            startup_data["tags"] = []
            startup_data["domain"] = "Technologie"

        # Essayer d'extraire la localisation
        location_element = soup.select_one(".location, .address, .city")
        if location_element:
            startup_data["location"] = location_element.get_text(strip=True)
        else:
            # Rechercher un texte qui ressemble à une adresse
            for element in soup.select("p, div"):
                text = element.get_text(strip=True)
                if "réunion" in text.lower() and (
                    "saint-" in text.lower() or
                    "sainte-" in text.lower() or
                    "st-" in text.lower() or
                    "ste-" in text.lower()
                ):
                    startup_data["location"] = text
                    break
            else:
                startup_data["location"] = "La Réunion"

        # Essayer d'extraire les contacts
        contacts = []

        # Email
        email_elements = soup.select("a[href^='mailto:'], .email")
        for element in email_elements:
            if element.has_attr("href") and element["href"].startswith("mailto:"):
                email = element["href"][7:]  # Enlever "mailto:"
                contacts.append(f"Email: {email}")
                startup_data["email"] = email
                break

        # Si on n'a pas trouvé d'email explicite, chercher dans le texte
        if "email" not in startup_data:
            for element in soup.select("p, div, span"):
                text = element.get_text()
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                if email_match:
                    email = email_match.group(0)
                    contacts.append(f"Email: {email}")
                    startup_data["email"] = email
                    break
            else:
                startup_data["email"] = ""

        # Téléphone
        phone_elements = soup.select("a[href^='tel:'], .phone, .tel")
        for element in phone_elements:
            if element.has_attr("href") and element["href"].startswith("tel:"):
                phone = element["href"][4:]  # Enlever "tel:"
                contacts.append(f"Téléphone: {phone}")
                startup_data["phone"] = phone
                break
            else:
                text = element.get_text(strip=True)
                if text:
                    contacts.append(f"Téléphone: {text}")
                    startup_data["phone"] = text
                    break

        # Si on n'a pas trouvé de téléphone explicite, chercher un format de numéro dans le texte
        if "phone" not in startup_data:
            for element in soup.select("p, div, span"):
                text = element.get_text()
                # Recherche de formats téléphoniques courants à La Réunion
                phone_match = re.search(r'(?:\+262|0262)\s?[0-9]{2}\s?[0-9]{2}\s?[0-9]{2}', text)
                if phone_match:
                    phone = phone_match.group(0)
                    contacts.append(f"Téléphone: {phone}")
                    startup_data["phone"] = phone
                    break
            else:
                startup_data["phone"] = ""

        # Combiner tous les contacts trouvés
        if contacts:
            startup_data["contact"] = " | ".join(contacts)
        else:
            startup_data["contact"] = ""

        # Valeurs par défaut pour les champs manquants
        startup_data["ceo"] = ""
        startup_data["year_founded"] = ""
        startup_data["employee_count"] = ""

        # Chercher une image de logo
        logo_element = soup.select_one(".logo img, .startup-logo img, .company-logo img")
        if logo_element and logo_element.has_attr("src"):
            logo_url = logo_element["src"]
            # Convertir en URL absolue si nécessaire
            if not logo_url.startswith(("http://", "https://")):
                logo_url = urllib.parse.urljoin(url, logo_url)
            startup_data["logo_url"] = logo_url
        else:
            startup_data["logo_url"] = ""

        return startup_data

    def get_startup_details(self, startup_url: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails d'une startup à partir de son URL

        Args:
            startup_url: URL de la page de la startup

        Returns:
            Dictionnaire des données ou None si impossible à récupérer
        """
        logger.info(f"Récupération des détails de la startup: {startup_url}")
        soup = self.get_page(startup_url)

        if not soup:
            logger.error(f"Impossible de récupérer la page de la startup: {startup_url}")
            return None

        return self.extract_startup_data_from_page(soup, startup_url)

    def run(self) -> List[Dict[str, Any]]:
        """
        Exécute le crawler complet

        Returns:
            Liste des startups récupérées
        """
        try:
            logger.info("Démarrage du crawler La French Tech Réunion")

            # Récupération des startups de l'annuaire (avec pagination)
            startups = self.crawl_startups()

            if not startups:
                logger.warning("Aucune startup trouvée dans l'annuaire paginé, recherche de contenus alternatifs")

                # Si aucune startup n'a été trouvée, essayer de trouver des liens vers des pages individuelles
                soup = self.get_page(self.base_url)
                if soup:
                    # Trouver tous les liens du site
                    links = []
                    for a in soup.select("a[href]"):
                        href = a.get("href", "")
                        if href and href.startswith(("http://lafrenchtech-lareunion.com", "https://lafrenchtech-lareunion.com", "/")):
                            if not href.startswith(("http://", "https://")):
                                href = urllib.parse.urljoin(self.base_url, href)
                            links.append(href)

                    # Éliminer les duplications
                    links = list(set(links))

                    # Filtrer les liens qui sont probablement des pages de startups
                    startup_keywords = ["startup", "entreprise", "societe", "company", "innovation", "annuaire"]
                    potential_startup_links = []

                    for link in links:
                        if any(keyword in link.lower() for keyword in startup_keywords):
                            potential_startup_links.append(link)

                    logger.info(f"Trouvé {len(potential_startup_links)} liens potentiels vers des startups")

                    # Visiter chaque lien pour récupérer les détails
                    for link in potential_startup_links[:30]:  # Augmenté à 30 liens
                        startup_data = self.get_startup_details(link)
                        if startup_data:
                            startups.append(startup_data)

            # Dédupliquer les startups (au cas où on aurait trouvé la même startup plusieurs fois)
            unique_startups = []
            seen_ids = set()

            for startup in startups:
                if startup.get("id") not in seen_ids:
                    seen_ids.add(startup.get("id"))
                    unique_startups.append(startup)

            # Ajouter une date de mise à jour à chaque startup
            for startup in unique_startups:
                startup["last_updated"] = datetime.now().isoformat()

            logger.info(f"Récupération terminée: {len(unique_startups)} startups uniques trouvées")
            return unique_startups

        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du crawler: {e}", exc_info=True)
            return []