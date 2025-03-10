"""
Interface d'administration des startups
"""
import streamlit as st
import pandas as pd
import json
import os
import time
import uuid
from datetime import datetime
import hashlib

from ui.custom_style import display_french_tech_footer
from config import FRENCH_TECH_COLORS

# Chemin du fichier de sauvegarde des startups
STARTUPS_FILE = "data/startups_manual.json"

def ensure_data_dir():
    """S'assure que le dossier de données existe"""
    os.makedirs("data", exist_ok=True)

def load_startups():
    """Charge les startups depuis le fichier ou renvoie une liste vide"""
    ensure_data_dir()
    if os.path.exists(STARTUPS_FILE):
        try:
            with open(STARTUPS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            st.error(f"Erreur lors du chargement des startups: {e}")
            return []
    return []

def save_startups(startups):
    """Sauvegarde les startups dans le fichier"""
    ensure_data_dir()
    with open(STARTUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(startups, f, ensure_ascii=False, indent=2)

def generate_id(name):
    """Génère un ID unique pour une startup basé sur son nom"""
    name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
    return f"startup-{name_hash}"

def create_empty_startup():
    """Crée une structure vide pour une nouvelle startup"""
    return {
        "id": "",
        "name": "",
        "description": "",
        "tags": [],
        "url": "",
        "contact": "",
        "email": "",
        "phone": "",
        "ceo": "",
        "domain": "",
        "location": "La Réunion",
        "logo_url": "",
        "year_founded": "",
        "employee_count": "",
        "last_updated": datetime.now().isoformat()
    }

def update_startup(startups, startup_data):
    """Met à jour ou ajoute une startup dans la liste"""
    # Si la startup a un ID, on la recherche pour la mettre à jour
    if startup_data.get("id"):
        for i, s in enumerate(startups):
            if s.get("id") == startup_data.get("id"):
                # Mise à jour de la startup existante
                startups[i] = startup_data
                return startups

    # Sinon, c'est une nouvelle startup, on génère un ID et on l'ajoute
    startup_data["id"] = generate_id(startup_data.get("name", str(uuid.uuid4())))
    startups.append(startup_data)
    return startups

def delete_startup(startups, startup_id):
    """Supprime une startup de la liste par son ID"""
    return [s for s in startups if s.get("id") != startup_id]

def render_startup_admin():
    """Affiche la page d'administration des startups"""
    st.header("📋 Administration des Startups")

    # Chargement des startups
    startups = load_startups()

    # Tabs pour différentes fonctionnalités
    tab1, tab2, tab3 = st.tabs(["Liste des startups", "Ajouter une startup", "Import/Export"])

    with tab1:
        render_startup_list(startups)

    with tab2:
        render_add_startup_form(startups)

    with tab3:
        render_import_export(startups)

    # Footer
    display_french_tech_footer()


def render_startup_list(startups):
    """Affiche la liste des startups avec options de modification"""
    st.subheader("Liste des startups enregistrées")

    # Boutons d'action
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Rafraîchir les données", type="primary"):
            with st.spinner("Récupération des données en cours..."):
                try:
                    from crawler.startup_crawler import get_startup_data
                    fresh_startups = get_startup_data(force_refresh=True)

                    if fresh_startups:
                        # Recharger les startups pour afficher les nouvelles
                        reloaded_startups = load_startups()
                        st.success(f"Données mises à jour avec succès! {len(fresh_startups)} startups récupérées.")

                        # Si aucune startup n'était déjà chargée, recharger la page
                        if not startups:
                            st.rerun()
                    else:
                        st.warning("Aucune startup n'a pu être récupérée. Vérifiez les logs pour plus d'informations.")
                except Exception as e:
                    st.error(f"Erreur lors de la mise à jour des données: {e}")

    with col2:
        if st.button("🏠 Retour au chat", key="return_to_chat"):
            st.session_state.current_view = "chat"  # Réinitialiser la vue pour retourner au chat
            st.rerun()

    st.markdown("---")

    if not startups:
        st.info(
            "Aucune startup enregistrée. Utilisez le bouton 'Rafraîchir les données' pour récupérer les startups de La French Tech Réunion.")
        return

    # Affichage des statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre de startups", len(startups))
    with col2:
        domains = set(s.get("domain", "") for s in startups if s.get("domain"))
        st.metric("Domaines d'activité", len(domains))
    with col3:
        locations = set(s.get("location", "") for s in startups if s.get("location"))
        st.metric("Localisations", len(locations))

    # Filtres de recherche
    search_col1, search_col2 = st.columns([2, 1])

    with search_col1:
        search_query = st.text_input("Rechercher une startup", key="search_startup")

    with search_col2:
        domain_filter = st.selectbox(
            "Filtrer par domaine",
            options=["Tous"] + sorted(list(domains)),
            key="domain_filter"
        )

    # Filtrer les startups
    filtered_startups = startups

    if search_query:
        search_lower = search_query.lower()
        filtered_startups = [
            s for s in filtered_startups
            if search_lower in s.get("name", "").lower() or
               search_lower in s.get("description", "").lower() or
               search_lower in " ".join(s.get("tags", [])).lower()
        ]

    if domain_filter != "Tous":
        filtered_startups = [
            s for s in filtered_startups
            if s.get("domain") == domain_filter
        ]

    # Affichage des startups filtrées
    if not filtered_startups:
        st.warning("Aucune startup ne correspond aux critères de recherche.")
        return

    st.markdown(f"Affichage de **{len(filtered_startups)}** startups sur **{len(startups)}** au total")

    # Affichage de chaque startup
    for startup in filtered_startups:
        with st.expander(
                f"{startup.get('name', 'Startup sans nom')} ({startup.get('domain', 'Domaine non spécifié')})"):
            # Affichage des informations
            st.markdown(f"**Description:** {startup.get('description', 'Non spécifiée')}")

            # Affichage en colonnes
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Domaine:** {startup.get('domain', 'Non spécifié')}")
                st.markdown(f"**Localisation:** {startup.get('location', 'Non spécifiée')}")
                st.markdown(f"**Tags:** {', '.join(startup.get('tags', []))}")
                st.markdown(f"**URL:** {startup.get('url', 'Non spécifiée')}")

            with col2:
                st.markdown(f"**CEO:** {startup.get('ceo', 'Non spécifié')}")
                st.markdown(f"**Contact:** {startup.get('contact', 'Non spécifié')}")
                st.markdown(f"**Email:** {startup.get('email', 'Non spécifié')}")
                st.markdown(f"**Téléphone:** {startup.get('phone', 'Non spécifié')}")
                st.markdown(f"**Fondée en:** {startup.get('year_founded', 'Non spécifié')}")
                st.markdown(f"**Nombre d'employés:** {startup.get('employee_count', 'Non spécifié')}")

            # Dernière mise à jour
            last_updated = startup.get("last_updated", "")
            if last_updated:
                try:
                    date_obj = datetime.fromisoformat(last_updated)
                    formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                    st.caption(f"Dernière mise à jour: {formatted_date}")
                except:
                    st.caption(f"Dernière mise à jour: {last_updated}")

            # Boutons d'action
            edit_col, delete_col = st.columns([1, 1])

            with edit_col:
                if st.button("Modifier", key=f"edit_{startup.get('id')}"):
                    st.session_state.edit_startup = startup
                    st.session_state.startup_admin_view = "edit"
                    st.rerun()

            with delete_col:
                if st.button("Supprimer", key=f"delete_{startup.get('id')}"):
                    if st.session_state.get("confirm_delete") == startup.get("id"):
                        # Confirmation déjà demandée, on supprime
                        startups = delete_startup(startups, startup.get("id"))
                        save_startups(startups)
                        st.success(f"Startup '{startup.get('name')}' supprimée avec succès.")
                        st.session_state.confirm_delete = None
                        time.sleep(1)
                        st.rerun()
                    else:
                        # Demande de confirmation
                        st.session_state.confirm_delete = startup.get("id")
                        st.warning(
                            f"Êtes-vous sûr de vouloir supprimer '{startup.get('name')}'? Cliquez à nouveau sur Supprimer pour confirmer.")

def render_edit_startup_form(startups, startup):
    """Affiche le formulaire d'édition d'une startup"""
    st.markdown("---")
    st.subheader(f"Modifier la startup: {startup.get('name')}")

    # Création du formulaire
    with st.form(key="edit_startup_form"):
        # Champs de base
        name = st.text_input("Nom de la startup *", value=startup.get("name", ""))
        description = st.text_area("Description *", value=startup.get("description", ""))

        # Champs en colonnes
        col1, col2 = st.columns(2)

        with col1:
            domain = st.text_input("Domaine d'activité *", value=startup.get("domain", ""))
            location = st.text_input("Localisation", value=startup.get("location", "La Réunion"))
            tags_str = st.text_input("Tags (séparés par des virgules)", value=", ".join(startup.get("tags", [])))
            url = st.text_input("Site web", value=startup.get("url", ""))

        with col2:
            ceo = st.text_input("CEO", value=startup.get("ceo", ""))
            contact = st.text_input("Contact", value=startup.get("contact", ""))
            email = st.text_input("Email", value=startup.get("email", ""))
            phone = st.text_input("Téléphone", value=startup.get("phone", ""))
            year_founded = st.text_input("Année de fondation", value=startup.get("year_founded", ""))
            employee_count = st.text_input("Nombre d'employés", value=startup.get("employee_count", ""))

        # Champs supplémentaires
        logo_url = st.text_input("URL du logo", value=startup.get("logo_url", ""))

        # Boutons
        col1, col2 = st.columns([1, 1])

        with col1:
            cancel = st.form_submit_button("Annuler")

        with col2:
            submit = st.form_submit_button("Enregistrer")

        if submit:
            # Vérification des champs obligatoires
            if not name or not description or not domain:
                st.error("Les champs Nom, Description et Domaine sont obligatoires.")
            else:
                # Mise à jour des données
                updated_startup = {
                    "id": startup.get("id", ""),
                    "name": name,
                    "description": description,
                    "domain": domain,
                    "location": location,
                    "tags": [tag.strip() for tag in tags_str.split(",") if tag.strip()],
                    "url": url,
                    "ceo": ceo,
                    "contact": contact,
                    "email": email,
                    "phone": phone,
                    "year_founded": year_founded,
                    "employee_count": employee_count,
                    "logo_url": logo_url,
                    "last_updated": datetime.now().isoformat()
                }

                # Mise à jour de la liste
                updated_startups = update_startup(startups, updated_startup)
                save_startups(updated_startups)

                st.success(f"Startup '{name}' mise à jour avec succès.")

                # Réinitialisation de l'état
                st.session_state.startup_admin_view = "list"
                st.session_state.edit_startup = None

                time.sleep(1)
                st.rerun()

        if cancel:
            # Réinitialisation de l'état
            st.session_state.startup_admin_view = "list"
            st.session_state.edit_startup = None
            st.rerun()

def render_add_startup_form(startups):
    """Affiche le formulaire d'ajout d'une startup"""
    st.subheader("Ajouter une nouvelle startup")

    # Création du formulaire
    with st.form(key="add_startup_form"):
        # Champs de base
        name = st.text_input("Nom de la startup *")
        description = st.text_area("Description *")

        # Champs en colonnes
        col1, col2 = st.columns(2)

        with col1:
            domain = st.text_input("Domaine d'activité *")
            location = st.text_input("Localisation", value="La Réunion")
            tags_str = st.text_input("Tags (séparés par des virgules)")
            url = st.text_input("Site web")

        with col2:
            ceo = st.text_input("CEO")
            contact = st.text_input("Contact")
            email = st.text_input("Email")
            phone = st.text_input("Téléphone")
            year_founded = st.text_input("Année de fondation")
            employee_count = st.text_input("Nombre d'employés")

        # Champs supplémentaires
        logo_url = st.text_input("URL du logo")

        # Bouton de soumission
        submit = st.form_submit_button("Ajouter la startup")

        if submit:
            # Vérification des champs obligatoires
            if not name or not description or not domain:
                st.error("Les champs Nom, Description et Domaine sont obligatoires.")
            else:
                # Création de la nouvelle startup
                new_startup = {
                    "name": name,
                    "description": description,
                    "domain": domain,
                    "location": location,
                    "tags": [tag.strip() for tag in tags_str.split(",") if tag.strip()],
                    "url": url,
                    "ceo": ceo,
                    "contact": contact,
                    "email": email,
                    "phone": phone,
                    "year_founded": year_founded,
                    "employee_count": employee_count,
                    "logo_url": logo_url,
                    "last_updated": datetime.now().isoformat()
                }

                # Ajout à la liste
                updated_startups = update_startup(startups, new_startup)
                save_startups(updated_startups)

                st.success(f"Startup '{name}' ajoutée avec succès.")
                time.sleep(1)
                st.rerun()

def render_import_export(startups):
    """Affiche les options d'import et d'export des données"""
    st.subheader("Import / Export des données")

    # Section d'export
    st.markdown("### Exporter les données")

    # Créer un DataFrame pour visualisation
    if startups:
        # Récupérer tous les champs présents dans toutes les startups
        all_fields = set()
        for startup in startups:
            all_fields.update(startup.keys())

        # Créer un DataFrame avec des valeurs par défaut
        df_data = []
        for startup in startups:
            row = {field: startup.get(field, "") for field in all_fields}
            df_data.append(row)

        df = pd.DataFrame(df_data)

        # Afficher un aperçu
        st.write("Aperçu des données:")
        st.dataframe(df.head(10))

        # Exporter en CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="Télécharger en CSV",
            data=csv,
            file_name="startups_export.csv",
            mime="text/csv"
        )

        # Exporter en JSON
        json_str = json.dumps(startups, ensure_ascii=False, indent=2)
        st.download_button(
            label="Télécharger en JSON",
            data=json_str,
            file_name="startups_export.json",
            mime="application/json"
        )
    else:
        st.info("Aucune startup à exporter.")

    # Section d'import
    st.markdown("---")
    st.markdown("### Importer des données")

    col1, col2 = st.columns([1, 1])

    with col1:
        # Importer les données d'exemple
        if st.button("📥 Importer les données d'exemple"):
            try:
                # Charger le fichier d'exemple
                example_path = "data/startups_sample.json"
                if os.path.exists(example_path):
                    with open(example_path, "r", encoding="utf-8") as f:
                        example_startups = json.load(f)

                    # Enregistrer les données
                    save_startups(example_startups)
                    st.success(f"{len(example_startups)} startups d'exemple importées avec succès.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Fichier d'exemple non trouvé. Vérifiez que 'data/startups_sample.json' existe.")
            except Exception as e:
                st.error(f"Erreur lors de l'import des données d'exemple: {e}")

    with col2:
        # Importer des données personnalisées
        import_type = st.radio("Format d'import", ["CSV", "JSON"])

        uploaded_file = st.file_uploader(f"Importer un fichier {import_type}", type=[import_type.lower()])

    if uploaded_file is not None:
        try:
            if import_type == "CSV":
                # Import CSV
                df = pd.read_csv(uploaded_file)
                imported_startups = df.to_dict(orient="records")

                # Nettoyage des données
                for startup in imported_startups:
                    # Convertir NaN en chaînes vides
                    for key, value in startup.items():
                        if pd.isna(value):
                            startup[key] = ""

                    # Traiter les tags s'ils sont au format chaîne
                    if "tags" in startup and isinstance(startup["tags"], str):
                        startup["tags"] = [tag.strip() for tag in startup["tags"].split(",") if tag.strip()]
                    elif "tags" not in startup:
                        startup["tags"] = []

            else:
                # Import JSON
                imported_startups = json.load(uploaded_file)

            # Vérification du format
            if not isinstance(imported_startups, list):
                st.error("Format de fichier invalide. Veuillez importer une liste de startups.")
                return

            # Afficher un aperçu
            st.write(f"{len(imported_startups)} startups trouvées dans le fichier:")

            # Créer un DataFrame pour l'aperçu
            preview_df = pd.DataFrame([{
                "name": s.get("name", ""),
                "domain": s.get("domain", ""),
                "location": s.get("location", "")
            } for s in imported_startups])

            st.dataframe(preview_df)

            # Options d'import
            import_option = st.radio(
                "Mode d'import",
                ["Remplacer toutes les startups", "Ajouter aux startups existantes"]
            )

            if st.button("Confirmer l'import"):
                if import_option == "Remplacer toutes les startups":
                    # Remplacer les données existantes
                    for s in imported_startups:
                        # S'assurer que chaque startup a un ID
                        if not s.get("id"):
                            s["id"] = generate_id(s.get("name", str(uuid.uuid4())))
                        # Ajouter la date de mise à jour
                        s["last_updated"] = datetime.now().isoformat()

                    save_startups(imported_startups)
                    st.success(f"{len(imported_startups)} startups importées avec succès.")
                else:
                    # Ajouter aux données existantes
                    merged_startups = startups.copy()

                    # Dictionnaire des IDs existants
                    existing_ids = {s.get("id"): i for i, s in enumerate(merged_startups) if s.get("id")}

                    for s in imported_startups:
                        # S'assurer que chaque startup a un ID
                        if not s.get("id"):
                            s["id"] = generate_id(s.get("name", str(uuid.uuid4())))

                        # Ajouter la date de mise à jour
                        s["last_updated"] = datetime.now().isoformat()

                        # Vérifier si l'ID existe déjà
                        if s.get("id") in existing_ids:
                            # Mettre à jour la startup existante
                            merged_startups[existing_ids[s.get("id")]] = s
                        else:
                            # Ajouter la nouvelle startup
                            merged_startups.append(s)

                    save_startups(merged_startups)
                    st.success(f"{len(imported_startups)} startups importées avec succès.")

                time.sleep(1)
                st.rerun()

        except Exception as e:
            st.error(f"Erreur lors de l'import: {e}")

# Initialisation de l'état
if "startup_admin_view" not in st.session_state:
    st.session_state.startup_admin_view = "list"

if "edit_startup" not in st.session_state:
    st.session_state.edit_startup = None

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None