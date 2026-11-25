import streamlit as st

from core import database
from core.voices import DEFAULT_GENDER, VOICES

user = st.session_state.user

st.title("Choix de la voix")
st.write("Cette voix lira à voix haute les phrases que vous aurez confirmées.")

genders = list(VOICES.keys())
current = user.get("voice_gender", DEFAULT_GENDER)
if current not in genders:
    current = DEFAULT_GENDER

choice = st.radio(
    "Voix",
    genders,
    index=genders.index(current),
    format_func=lambda g: VOICES[g]["label"],
)

if st.button("Enregistrer ma voix"):
    database.update_voice(user["id"], choice)
    st.session_state.user["voice_gender"] = choice
    st.success(f"Voix enregistrée : {VOICES[choice]['label'].lower()}.")
    