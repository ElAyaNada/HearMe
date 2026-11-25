import streamlit as st

user = st.session_state.user

st.title("HearMe")
st.write(f"Bienvenue, {user['email']}.")
st.write("Choisissez votre voix dans le menu, puis lancez la caméra (bientôt disponible).")