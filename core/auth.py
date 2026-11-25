import re
import sqlite3

import bcrypt

from core import database

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def register(email: str, password: str):
    """Renvoie (ok, message)."""
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        return False, "Adresse e-mail invalide."
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères."
    if len(password.encode("utf-8")) > 72:
        return False, "Le mot de passe est trop long (72 octets maximum)."

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        database.create_user(email, hashed)
    except sqlite3.IntegrityError:
        return False, "Un compte existe déjà avec cet e-mail."
    return True, "Compte créé. Vous pouvez vous connecter."


def login(email: str, password: str):
    """Renvoie un dictionnaire utilisateur, ou None si les identifiants sont faux."""
    user = database.get_user_by_email(email.strip().lower())
    if user is None:
        return None
    if len(password.encode("utf-8")) > 72:
        return None
    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return None
    return {
        "id": user["id"],
        "email": user["email"],
        "voice_gender": user["voice_gender"],
    }