import streamlit as st

from core import auth, database

st.set_page_config(page_title="HearMe", page_icon="🤟")
database.init_db()

if "user" not in st.session_state:
    st.session_state.user = None

st.title("HearMe")
st.write("De la langue des signes à la voix.")

if st.session_state.user:
    st.success(f"Connecté : {st.session_state.user['email']}")
    if st.button("Se déconnecter"):
        st.session_state.user = None
        st.rerun()
else:
    tab_login, tab_register = st.tabs(["Connexion", "Inscription"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("E-mail")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")
        if submitted:
            user = auth.login(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("E-mail ou mot de passe incorrect.")

    with tab_register:
        with st.form("register_form"):
            r_email = st.text_input("E-mail", key="r_email")
            r_password = st.text_input("Mot de passe (8 caractères minimum)", type="password", key="r_pw")
            r_password2 = st.text_input("Confirmer le mot de passe", type="password", key="r_pw2")
            r_submitted = st.form_submit_button("Créer mon compte")
        if r_submitted:
            if r_password != r_password2:
                st.error("Les mots de passe ne correspondent pas.")
            else:
                ok, message = auth.register(r_email, r_password)
                if ok:
                    st.success(message)
                else:
                    st.error(message)