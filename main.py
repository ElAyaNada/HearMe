import streamlit as st

from core import database

st.set_page_config(page_title="HearMe", page_icon="🤟")
database.init_db()

if "user" not in st.session_state:
    st.session_state.user = None

login_page = st.Page("views/login.py", title="Connexion", icon="🔑")
home_page = st.Page("views/accueil.py", title="Accueil", icon="🏠", default=True)
voice_page = st.Page("views/voix.py", title="Ma voix", icon="🗣️")

if st.session_state.user:
    pg = st.navigation([home_page, voice_page])
    with st.sidebar:
        st.caption(f"Connecté : {st.session_state.user['email']}")
        if st.button("Se déconnecter"):
            st.session_state.user = None
            st.rerun()
else:
    pg = st.navigation([login_page])
    # Pas de barre latérale tant que l'utilisateur n'est pas connecté
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

pg.run()