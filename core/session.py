import streamlit as st


def require_login():
    """Arrête la page si personne n'est connecté, sinon renvoie l'utilisateur."""
    user = st.session_state.get("user")
    if not user:
        st.warning("Veuillez vous connecter pour accéder à cette page.")
        st.page_link("main.py", label="Aller à la connexion", icon="🔑")
        st.stop()
    return user