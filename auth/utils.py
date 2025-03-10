"""
Fonctions utilitaires pour l'authentification
"""
import hashlib
import os
import json
import logging
import uuid
from typing import Dict, List, Any, Optional
import re
from datetime import datetime, timedelta
import jwt

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chemin du fichier de base de données utilisateurs
USERS_DB_PATH = "data/users.json"

# Clé secrète pour JWT
JWT_SECRET = os.getenv("JWT_SECRET", "default_secret_key_change_in_production")
# Durée de validité du token (en jours)
JWT_EXPIRATION_DAYS = 7


def hash_password(password: str) -> str:
    """
    Hache un mot de passe avec SHA-256 et un salt

    Args:
        password: Mot de passe en clair

    Returns:
        Mot de passe haché
    """
    salt = "FrenchTechReunion2023"  # Dans une application réelle, utilisez un salt unique par utilisateur
    salted_password = password + salt
    return hashlib.sha256(salted_password.encode()).hexdigest()


def validate_email(email: str) -> bool:
    """
    Valide le format d'une adresse email

    Args:
        email: Adresse email à valider

    Returns:
        True si l'adresse est valide, False sinon
    """
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(email_pattern, email))


def validate_password(password: str) -> bool:
    """
    Valide la complexité d'un mot de passe

    Args:
        password: Mot de passe à valider

    Returns:
        True si le mot de passe est valide, False sinon
    """
    # Au moins 8 caractères, une majuscule, une minuscule et un chiffre
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True


def validate_signup_data(data: Dict[str, str]) -> Optional[str]:
    """
    Valide les données d'inscription

    Args:
        data: Données d'inscription

    Returns:
        Message d'erreur ou None si les données sont valides
    """
    required_fields = ["first_name", "last_name", "email", "password", "company", "role"]

    # Vérification des champs requis
    for field in required_fields:
        if field not in data or not data[field]:
            return f"Le champ '{field}' est requis."

    # Validation de l'email
    if not validate_email(data["email"]):
        return "Adresse email invalide."

    # Validation du mot de passe
    if not validate_password(data["password"]):
        return "Le mot de passe doit contenir au moins 8 caractères, dont une majuscule, une minuscule et un chiffre."

    return None


def init_users_db():
    """
    Initialise la base de données utilisateurs si elle n'existe pas
    """
    os.makedirs(os.path.dirname(USERS_DB_PATH), exist_ok=True)
    if not os.path.exists(USERS_DB_PATH):
        with open(USERS_DB_PATH, "w") as f:
            json.dump([], f)


def get_users() -> List[Dict[str, Any]]:
    """
    Récupère tous les utilisateurs

    Returns:
        Liste des utilisateurs
    """
    init_users_db()
    try:
        with open(USERS_DB_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_users(users: List[Dict[str, Any]]):
    """
    Sauvegarde la liste des utilisateurs

    Args:
        users: Liste des utilisateurs
    """
    init_users_db()
    with open(USERS_DB_PATH, "w") as f:
        json.dump(users, f, indent=2)


def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Recherche un utilisateur par son email

    Args:
        email: Email de l'utilisateur

    Returns:
        Données de l'utilisateur ou None si non trouvé
    """
    users = get_users()
    for user in users:
        if user.get("email") == email:
            return user
    return None


def create_user(user_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Crée un nouvel utilisateur

    Args:
        user_data: Données de l'utilisateur

    Returns:
        Données de l'utilisateur créé
    """
    users = get_users()

    # Création de l'utilisateur
    new_user = {
        "id": str(uuid.uuid4()),
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "email": user_data["email"],
        "password_hash": hash_password(user_data["password"]),
        "company": user_data["company"],
        "role": user_data["role"],
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }

    users.append(new_user)
    save_users(users)

    # Ne pas renvoyer le mot de passe haché
    user_without_password = new_user.copy()
    user_without_password.pop("password_hash")

    return user_without_password


def verify_login(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Vérifie les identifiants de connexion

    Args:
        email: Email de l'utilisateur
        password: Mot de passe

    Returns:
        Données de l'utilisateur ou None si les identifiants sont invalides
    """
    user = find_user_by_email(email)
    if not user:
        return None

    # Vérification du mot de passe
    if user.get("password_hash") != hash_password(password):
        return None

    # Mise à jour de la date de dernière connexion
    users = get_users()
    for u in users:
        if u.get("id") == user["id"]:
            u["last_login"] = datetime.now().isoformat()
            break

    save_users(users)

    # Ne pas renvoyer le mot de passe haché
    user_without_password = user.copy()
    user_without_password.pop("password_hash")

    return user_without_password


def generate_token(user_id: str) -> str:
    """
    Génère un token JWT pour l'authentification

    Args:
        user_id: ID de l'utilisateur

    Returns:
        Token JWT
    """
    expiration = datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    payload = {
        "sub": user_id,
        "exp": expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Vérifie un token JWT et récupère l'utilisateur associé

    Args:
        token: Token JWT

    Returns:
        Données de l'utilisateur ou None si le token est invalide
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")

        # Récupération de l'utilisateur
        users = get_users()
        for user in users:
            if user.get("id") == user_id:
                # Ne pas renvoyer le mot de passe haché
                user_without_password = user.copy()
                user_without_password.pop("password_hash")
                return user_without_password

        return None

    except jwt.PyJWTError:
        return None


def update_user_profile(user_id: str, updated_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Met à jour le profil d'un utilisateur

    Args:
        user_id: ID de l'utilisateur
        updated_data: Données mises à jour

    Returns:
        Données de l'utilisateur mises à jour ou None si l'utilisateur n'existe pas
    """
    users = get_users()

    for i, user in enumerate(users):
        if user.get("id") == user_id:
            # Mise à jour des champs autorisés
            for field in ["first_name", "last_name", "company", "role"]:
                if field in updated_data:
                    users[i][field] = updated_data[field]

            # Mise à jour du mot de passe si fourni
            if "password" in updated_data and updated_data["password"]:
                users[i]["password_hash"] = hash_password(updated_data["password"])

            save_users(users)

            # Ne pas renvoyer le mot de passe haché
            user_without_password = users[i].copy()
            user_without_password.pop("password_hash")

            return user_without_password

    return None