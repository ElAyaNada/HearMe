import streamlit as st
from streamlit_webrtc import webrtc_streamer

from core.video import SignProcessor

st.title("Caméra")
st.write("Placez une main devant la caméra et tenez chaque lettre environ 1 seconde.")

ctx = webrtc_streamer(
    key="sign-camera",
    video_processor_factory=SignProcessor,
    media_stream_constraints={"video": {"width": 640, "height": 480}, "audio": False},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    async_processing=True,
)


@st.fragment(run_every=0.5)
def live_panel(ctx):
    processor = ctx.video_processor
    if processor is None:
        st.info("Cliquez sur START pour activer la caméra.")
        return

    st.caption(f"Lettre détectée : {processor.get_letter() or '-'}")
    st.markdown(f"### {processor.get_text() or '…'}")

    col1, col2 = st.columns(2)
    if col1.button("Supprimer la dernière lettre"):
        processor.delete_last()
    if col2.button("Tout effacer"):
        processor.clear()


live_panel(ctx)