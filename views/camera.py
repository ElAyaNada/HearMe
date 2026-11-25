import streamlit as st
from streamlit_webrtc import webrtc_streamer

from core.tts import synthesize
from core.video import SignProcessor
from core.voices import LANGUAGES, VOICES

user = st.session_state.user

st.title("Caméra")
st.write("Placez une main devant la caméra et tenez chaque lettre environ 1 seconde.")

ctx = webrtc_streamer(
    key="sign-camera",
    video_processor_factory=SignProcessor,
    media_stream_constraints={"video": {"width": 640, "height": 480}, "audio": False},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    async_processing=True,
)

col_a, col_b = st.columns(2)
lang = col_a.selectbox("Langue de lecture", list(LANGUAGES), format_func=lambda k: LANGUAGES[k])
auto_space = col_b.checkbox("Espace automatique", value=True)
space_delay = col_b.slider(
    "Délai sans main avant l'espace (secondes)", 1.0, 4.0, 2.0, 0.5,
    disabled=not auto_space,
)
if ctx.video_processor:
    ctx.video_processor.auto_space = auto_space
    ctx.video_processor.space_delay = space_delay


@st.fragment(run_every=0.5)
def live_panel(ctx):
    processor = ctx.video_processor
    if processor is None:
        st.info("Cliquez sur START pour activer la caméra.")
        return

    st.caption(f"Lettre détectée : {processor.get_letter() or '-'}")
    text = processor.get_text()
    st.markdown(f"### {text}▏" if text else "### …")

    c1, c2, c3 = st.columns(3)
    if c1.button("Supprimer la dernière lettre"):
        processor.delete_last()
    if c2.button("Espace"):
        processor.add_space()
    if c3.button("Tout effacer"):
        processor.clear()


live_panel(ctx)

st.divider()

if st.button("Confirmer et écouter", type="primary"):
    processor = ctx.video_processor
    text = " ".join(processor.get_text().split()) if processor else ""
    if not text:
        st.warning("Aucun texte à lire. Signez quelques lettres d'abord.")
    else:
        try:
            with st.spinner("Génération de la voix..."):
                audio = synthesize(text.lower(), user["voice_gender"], lang)
            st.session_state.last_audio = audio
            st.session_state.last_text = text
            st.session_state.play_now = True
        except Exception:
            st.error("Impossible de générer la voix. Vérifiez votre connexion internet.")

if st.session_state.get("last_audio"):
    voice_label = VOICES.get(user["voice_gender"], {}).get("label", "")
    st.write(f"Dernière phrase lue : **{st.session_state.last_text}** ({voice_label.lower()})")
    autoplay = st.session_state.pop("play_now", False)
    st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=autoplay)