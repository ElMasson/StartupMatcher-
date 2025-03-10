"""
Interface d'administration pour le crawler
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import time

from crawler.startup_crawler import get_startup_data, SCHEDULE_AVAILABLE
from crawler.utils import get_last_crawl_stats as get_crawl_stats
from crawler.firecrawl_handler import get_startup_metadata
from ui.custom_style import display_french_tech_footer
from config import FRENCH_TECH_COLORS

def render_crawler_admin():
    """
    Affiche la page d'administration du crawler
    """
    st.header("🔄 Administration du Crawler")

    # Statistiques du dernier crawl
    st.subheader("Statut du Crawler")

    # Affichage du statut de schedule
    if not SCHEDULE_AVAILABLE:
        st.warning("⚠️ Le module 'schedule' n'est pas installé. Les mises à jour périodiques automatiques fonctionnent en mode simplifié. Pour une meilleure expérience, installez schedule avec: `pip install schedule`")

    # Récupération des statistiques
    crawl_stats = get_crawl_stats()

    if not crawl_stats:
        st.warning("Aucune donnée de crawl disponible. Effectuez un premier crawl pour voir les statistiques.")
    else:
        # Affichage des statuts
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Startups",
                value=crawl_stats.get("count", 0),
                delta=None
            )

        with col2:
            # Formatage de la date de dernière mise à jour
            last_update = datetime.fromisoformat(crawl_stats.get("last_update", "2000-01-01T00:00:00"))
            time_diff = (datetime.now() - last_update).total_seconds()

            if time_diff < 3600:  # Moins d'une heure
                time_str = f"{int(time_diff / 60)} minutes"
            elif time_diff < 86400:  # Moins d'un jour
                time_str = f"{int(time_diff / 3600)} heures"
            else:
                time_str = f"{int(time_diff / 86400)} jours"

            st.metric(
                label="Dernière mise à jour",
                value=last_update.strftime("%d/%m/%Y %H:%M"),
                delta=f"il y a {time_str}"
            )

        with col3:
            status = crawl_stats.get("status", "unknown")

            if status == "success":
                status_display = "✅ Succès"
                delta_color = "normal"
            elif status == "fallback":
                status_display = "⚠️ Données de secours"
                delta_color = "off"
            else:
                status_display = "❌ Erreur"
                delta_color = "inverse"

            st.metric(
                label="Statut",
                value=status_display,
                delta=crawl_stats.get("message", ""),
                delta_color=delta_color
            )

        # Affichage des statistiques détaillées
        st.subheader("Statistiques")

        # Présentation sous forme de carte
        stats_card = f"""
        <div style="background-color: {FRENCH_TECH_COLORS['light_gray']}; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h4 style="color: {FRENCH_TECH_COLORS['primary']};">Statistiques des données</h4>
            <ul>
                <li><strong>Nombre de startups:</strong> {crawl_stats.get("count", 0)}</li>
                <li><strong>Nombre de domaines:</strong> {crawl_stats.get("domains_count", 0)}</li>
                <li><strong>Nombre de localisations:</strong> {crawl_stats.get("locations_count", 0)}</li>
                <li><strong>Tags uniques:</strong> {crawl_stats.get("tags_unique", 0)}</li>
                <li><strong>Total de tags:</strong> {crawl_stats.get("tags_total", 0)}</li>
            </ul>
        </div>
        """

        st.markdown(stats_card, unsafe_allow_html=True)

    # Actions du crawler
    st.subheader("Actions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Rafraîchir les données maintenant", type="primary"):
            with st.spinner("Récupération des données en cours..."):
                # Forcer la mise à jour des données
                start_time = time.time()
                updated_data = get_startup_data(force_refresh=True)
                end_time = time.time()

                # Afficher le résultat
                st.success(f"Données mises à jour avec succès en {end_time - start_time:.2f} secondes. {len(updated_data)} startups récupérées.")
                st.rerun()

    with col2:
        if st.button("Nettoyer le cache", type="secondary"):
            # Supprimer les fichiers de cache
            cache_dir = "data/cache"
            if os.path.exists(cache_dir):
                cache_info_path = os.path.join(cache_dir, "cache_info.json")
                cache_data_path = os.path.join(cache_dir, "startups_data.json")

                deleted_files = []

                if os.path.exists(cache_info_path):
                    os.remove(cache_info_path)
                    deleted_files.append("cache_info.json")

                if os.path.exists(cache_data_path):
                    os.remove(cache_data_path)
                    deleted_files.append("startups_data.json")

                if deleted_files:
                    st.success(f"Cache nettoyé: {', '.join(deleted_files)}")
                else:
                    st.info("Aucun fichier de cache à nettoyer.")
            else:
                st.info("Aucun dossier de cache trouvé.")

    # Visualisation des métadonnées
    st.subheader("Métadonnées des Startups")

    # Récupération des métadonnées
    with st.spinner("Chargement des métadonnées..."):
        metadata = get_startup_metadata()

    if metadata:
        # Onglets pour les différentes métadonnées
        tab1, tab2, tab3 = st.tabs(["Domaines", "Tags", "Localisations"])

        with tab1:
            # Affichage des domaines
            domains = metadata.get("domains", [])
            if domains:
                # Récupération des startups pour compter par domaine
                startups = get_startup_data()
                domain_counts = {}

                for startup in startups:
                    domain = startup.get("domain", "")
                    if domain:
                        domain_counts[domain] = domain_counts.get(domain, 0) + 1

                # Création du DataFrame pour le graphique
                domain_df = pd.DataFrame({
                    "Domaine": list(domain_counts.keys()),
                    "Nombre": list(domain_counts.values())
                })

                # Tri par nombre décroissant
                domain_df = domain_df.sort_values("Nombre", ascending=False)

                # Création du graphique
                fig = px.bar(
                    domain_df,
                    x="Domaine",
                    y="Nombre",
                    color="Nombre",
                    color_continuous_scale=px.colors.sequential.Reds,
                    title="Répartition des startups par domaine"
                )

                # Personnalisation du graphique
                fig.update_layout(
                    xaxis_title="Domaine d'activité",
                    yaxis_title="Nombre de startups",
                    coloraxis_showscale=False,
                    height=500
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucun domaine disponible.")

        with tab2:
            # Affichage des tags
            tags = metadata.get("tags", [])
            if tags:
                # Récupération des startups pour compter par tag
                startups = get_startup_data()
                tag_counts = {}

                for startup in startups:
                    for tag in startup.get("tags", []):
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

                # Création du DataFrame pour le graphique
                tag_df = pd.DataFrame({
                    "Tag": list(tag_counts.keys()),
                    "Nombre": list(tag_counts.values())
                })

                # Tri par nombre décroissant et limitation aux 20 premiers
                tag_df = tag_df.sort_values("Nombre", ascending=False).head(20)

                # Création du graphique
                fig = px.bar(
                    tag_df,
                    x="Tag",
                    y="Nombre",
                    color="Nombre",
                    color_continuous_scale=px.colors.sequential.Blues,
                    title="Top 20 des tags les plus utilisés"
                )

                # Personnalisation du graphique
                fig.update_layout(
                    xaxis_title="Tag",
                    yaxis_title="Nombre de startups",
                    coloraxis_showscale=False,
                    height=500
                )

                st.plotly_chart(fig, use_container_width=True)

                # Liste complète des tags
                with st.expander("Liste complète des tags"):
                    # Affichage sous forme de tableau
                    st.dataframe(
                        tag_df.sort_values("Nombre", ascending=False),
                        use_container_width=True
                    )
            else:
                st.info("Aucun tag disponible.")

        with tab3:
            # Affichage des localisations
            locations = metadata.get("locations", [])
            if locations:
                # Récupération des startups pour compter par localisation
                startups = get_startup_data()
                location_counts = {}

                for startup in startups:
                    location = startup.get("location", "")
                    if location:
                        location_counts[location] = location_counts.get(location, 0) + 1

                # Création du DataFrame pour le graphique
                location_df = pd.DataFrame({
                    "Localisation": list(location_counts.keys()),
                    "Nombre": list(location_counts.values())
                })

                # Tri par nombre décroissant
                location_df = location_df.sort_values("Nombre", ascending=False)

                # Création du graphique
                fig = px.pie(
                    location_df,
                    names="Localisation",
                    values="Nombre",
                    title="Répartition géographique des startups",
                    color_discrete_sequence=px.colors.sequential.Reds_r
                )

                # Personnalisation du graphique
                fig.update_layout(height=500)

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune localisation disponible.")
    else:
        st.warning("Impossible de récupérer les métadonnées. Effectuez un crawl pour générer les données.")

    # Affichage du footer
    display_french_tech_footer()