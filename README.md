# StartupMatcher - La French Tech Réunion

![Logo French Tech Réunion](https://lafrenchtech-lareunion.com/wp-content/uploads/2019/08/logo-lafrenchtech-lareunion.png)

Une application d'IA agentic permettant aux acheteurs de grands groupes et de collectivités de trouver les startups innovantes adaptées à leurs besoins.

## Fonctionnalités

- 🤖 **Agents IA autonomes** propulsés par CrewAI et Mistral
- 🔍 **Recherche sémantique** de startups selon les besoins exprimés
- 🔄 **Proposition de combinaisons** de startups complémentaires
- 💬 **Interface conversationnelle** intuitive
- 📊 **Visualisation des données** sur les startups
- 🔐 **Système d'authentification** complet (inscription/connexion)
- 👤 **Gestion des profils utilisateurs**

## Architecture

L'application suit une architecture modulaire avec les règles d'or suivantes:
- **Règle 0**: Séparation de l'affichage et du calcul
- **Règle 1**: 1 dossier par fonctionnalité
- **Règle 2**: Dans chaque dossier, un fichier utils.py pour les fonctions transversales
- **Règle 3**: Un fichier .py par fonction

### Structure du projet

```
startup_matcher/
├── main.py                       # Point d'entrée principal
├── config.py                     # Configuration globale
├── requirements.txt              # Dépendances
├── auth/                         # Authentification
│   ├── auth_handler.py
│   ├── auth_ui.py
│   └── utils.py
├── crawler/                      # Crawling des startups
│   ├── firecrawl_handler.py
│   ├── startup_crawler.py
│   └── utils.py
├── rag/                          # RAG (Retrieval Augmented Generation)
│   ├── docling_handler.py
│   ├── embedding.py
│   ├── retrieval.py
│   └── utils.py
├── llm/                          # Gestion des LLM
│   ├── mistral_handler.py
│   ├── langchain_integration.py
│   ├── prompt_builder.py
│   └── utils.py
├── agent/                        # Agents autonomes
│   ├── crew_manager.py           # Gestion des agents CrewAI
│   ├── agent_handler.py
│   └── utils.py
└── ui/                           # Interface utilisateur
    ├── chat_ui.py
    ├── results_ui.py
    ├── startup_detail_ui.py
    ├── profile_ui.py
    ├── custom_style.py
    └── utils.py
```

## Technologies utilisées

- **Frontend**: Streamlit
- **IA**: 
  - Mistral AI (via l'API mistral-large-latest)
  - CrewAI pour les agents autonomes
  - LangChain pour les intégrations
- **RAG**: Docling pour la préparation des documents
- **Crawling**: Firecrawl pour la récupération des données des startups
- **Authentification**: JWT (JSON Web Tokens)
- **Data Processing**: Pandas, NumPy
- **Visualisation**: Plotly

## Installation

1. Cloner le dépôt:
```bash
git clone https://github.com/frenchtech-reunion/startup-matcher.git
cd startup-matcher
```

2. Créer un environnement virtuel:
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances:
```bash
pip install -r requirements.txt
```

4. Créer un fichier `.env` à la racine du projet:
```
MISTRAL_API_KEY=votre-clé-api-mistral
JWT_SECRET=une-clé-secrète-pour-les-jetons-jwt
```

## Lancement

```bash
streamlit run main.py
```

## Flux utilisateur

1. **Inscription/Connexion**: L'utilisateur doit créer un compte ou se connecter
2. **Chat avec l'assistant**: Expression des besoins en innovation
3. **Résultats**: Visualisation des startups correspondantes
4. **Détails**: Exploration des détails d'une startup spécifique
5. **Profil**: Gestion des informations personnelles

## Cas d'utilisation

- **Acheteurs de grands groupes**: Recherche de startups innovantes pour des appels d'offres
- **Collectivités territoriales**: Identification de partenaires pour des projets d'innovation
- **Responsables innovation**: Veille technologique et cartographie de l'écosystème
- **Startups**: Possibilité de trouver des partenaires complémentaires

## Architecture des agents

L'application utilise CrewAI pour orchestrer trois agents spécialisés:

1. **Analyste de besoins**: Comprend et structure les besoins exprimés
2. **Expert en startups**: Identifie les startups pertinentes
3. **Architecte de solutions**: Propose des combinaisons complémentaires

Ces agents collaborent de manière autonome, communiquent entre eux, et s'appuient sur le système RAG pour accéder aux informations sur les startups.

## Contribuer

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou à proposer une pull request pour améliorer l'application.

## Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

## Contact

La French Tech Réunion - [https://lafrenchtech-lareunion.com/](https://lafrenchtech-lareunion.com/)