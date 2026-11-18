import html
import pickle
import threading
import time
from pathlib import Path

import av
import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer


st.set_page_config(
    page_title="SignSpeak | Sign Language Recognition",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="collapsed",
)


class RecognitionState:
    """Thread-safe data shared between the Streamlit script and video callback."""

    def __init__(self, recognized_text=""):
        self.lock = threading.Lock()
        self.recognized_text = recognized_text
        self.current_prediction = ""
        self.hand_detected = False

    def snapshot(self):
        with self.lock:
            return (
                self.recognized_text,
                self.current_prediction,
                self.hand_detected,
            )

    def set_tracking(self, prediction, hand_detected):
        with self.lock:
            self.current_prediction = prediction
            self.hand_detected = hand_detected

    def append_letter(self, letter):
        with self.lock:
            self.recognized_text += letter

    def clear_text(self):
        with self.lock:
            self.recognized_text = ""

    def delete_last(self):
        with self.lock:
            self.recognized_text = self.recognized_text[:-1]

    def add_space(self):
        with self.lock:
            self.recognized_text += " "


@st.cache_resource(show_spinner="Loading the trained sign recognition model...")
def load_model():
    model_path = Path(__file__).resolve().parent / "assets" / "model.p"
    with model_path.open("rb") as model_file:
        model_dict = pickle.load(model_file)
    return model_dict["model"]


class SignLanguageVideoProcessor(VideoProcessorBase):
    def __init__(self, model, recognition_state):
        self.model = model
        self.recognition_state = recognition_state
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.5,
        )
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.landmark_drawing_spec = self.mp_drawing.DrawingSpec(
            color=(153, 255, 210),
            thickness=3,
            circle_radius=2,
        )
        self.connection_drawing_spec = self.mp_drawing.DrawingSpec(
            color=(0, 0, 0),
            thickness=2,
            circle_radius=2,
        )
        self.previous_prediction = ""
        self.prediction_started_at = time.time()

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        height, width = image.shape[:2]
        processing_image = image
        if width > 480:
            processing_height = round(height * 480 / width)
            processing_image = cv2.resize(
                image, (480, processing_height), interpolation=cv2.INTER_AREA
            )
        results = self.hands.process(
            cv2.cvtColor(processing_image, cv2.COLOR_BGR2RGB)
        )
        hand_landmarks = (
            results.multi_hand_landmarks[0]
            if results.multi_hand_landmarks
            else None
        )

        if hand_landmarks is None:
            self.recognition_state.set_tracking("", False)
        else:
            self.mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=self.landmark_drawing_spec,
                connection_drawing_spec=self.connection_drawing_spec,
            )

            landmarks = hand_landmarks.landmark
            x_values = [landmark.x for landmark in landmarks]
            y_values = [landmark.y for landmark in landmarks]
            min_x, max_x = min(x_values), max(x_values)
            min_y, max_y = min(y_values), max(y_values)
            features = []
            for landmark in landmarks:
                features.extend(
                    (
                        landmark.x - min_x,
                        landmark.y - min_y,
                    )
                )

            prediction = str(self.model.predict([np.asarray(features)])[0])
            self.recognition_state.set_tracking(prediction, True)

            if prediction != self.previous_prediction:
                self.previous_prediction = prediction
                self.prediction_started_at = time.time()
            elif time.time() - self.prediction_started_at > 1:
                self.recognition_state.append_letter(prediction)
                self.prediction_started_at = time.time()

            x1 = max(0, int(min_x * width) - 10)
            y1 = max(0, int(min_y * height) - 10)
            x2 = min(width - 1, int(max_x * width) - 10)
            y2 = min(height - 1, int(max_y * height) - 10)
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 255, 255), 4)
            cv2.putText(
                image,
                prediction,
                (x1, max(30, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.3,
                (255, 255, 255),
                3,
                cv2.LINE_AA,
            )

        return av.VideoFrame.from_ndarray(image, format="bgr24")

    def on_ended(self):
        self.hands.close()


def render_styles():
    st.markdown(
        """
        <style>
        :root {
            color-scheme: light;
            --page: #f2faf7;
            --panel-soft: #f1f8f6;
            --line: #d7e8e2;
            --text: #173b34;
            --muted: #658078;
            --accent: #0fa879;
        }
        .stApp {
            background:
                radial-gradient(ellipse at 12% 0%, rgba(15, 168, 121, .14), transparent 36%),
                var(--page);
            color: var(--text);
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { right: 1.5rem; }
        .block-container {
            max-width: 1440px;
            padding-top: 2rem;
            padding-bottom: 2.5rem;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--line);
            border-radius: 18px;
            background: rgba(255, 255, 255, .94);
            box-shadow: 0 12px 32px rgba(27, 79, 64, .06);
        }
        h1, h2, h3, p, label { color: var(--text); }
        .brand-kicker {
            color: var(--accent);
            font-size: .75rem;
            font-weight: 700;
            letter-spacing: .16em;
            text-transform: uppercase;
            margin-bottom: .35rem;
        }
        .brand-title {
            color: var(--text);
            font-size: clamp(2rem, 4vw, 3rem);
            font-weight: 750;
            line-height: 1.08;
            letter-spacing: -.04em;
            margin: 0;
        }
        .brand-subtitle {
            color: var(--muted);
            font-size: 1rem;
            margin: .65rem 0 0;
        }
        .section-title {
            color: var(--text);
            font-size: 1.12rem;
            font-weight: 700;
            margin: 0;
        }
        .section-caption {
            color: var(--muted);
            font-size: .86rem;
            margin: .25rem 0 0;
        }
        .result-card {
            min-height: 78px;
            padding: 1rem 1.1rem;
            border: 1px solid #b8e9d4;
            border-radius: 14px;
            background: linear-gradient(135deg, #ddf8eb, #edf9ff);
        }
        .result-label {
            color: #13825f;
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .12em;
            text-transform: uppercase;
        }
        .result-value {
            color: var(--text);
            font-size: 1.8rem;
            font-weight: 750;
            line-height: 1.2;
            margin-top: .25rem;
        }
        .recognized-output {
            min-height: 170px;
            max-height: 360px;
            overflow-y: auto;
            padding: 1rem 1.1rem;
            border: 1px solid var(--line);
            border-radius: 14px;
            background: var(--panel-soft);
            color: var(--text);
            font-size: 1.15rem;
            line-height: 1.7;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }
        .empty-output { color: var(--muted); }
        .stButton > button {
            min-height: 2.75rem;
            border-radius: 10px;
            border: 1px solid var(--line);
            background: #ffffff;
            color: var(--text);
            font-weight: 650;
            transition: border-color .16s ease, transform .16s ease, background .16s ease;
        }
        .stButton > button:hover {
            border-color: var(--accent);
            color: var(--text);
            background: #e7f8f1;
            transform: translateY(-1px);
        }
        [data-testid="stMetric"] {
            padding: .75rem;
            border: 1px solid var(--line);
            border-radius: 12px;
            background: #f8fcfb;
        }
        [data-testid="stMetricLabel"] { color: var(--muted); }
        [data-testid="stMetricValue"] { color: var(--text); }
        div[data-testid="stMarkdownContainer"] p { color: inherit; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    render_styles()
    st.markdown(
        """
        <div class="brand-kicker">AI-powered computer vision</div>
        <h1 class="brand-title">SignSpeak</h1>
        <p class="brand-subtitle">
            Turn hand signs into text, instantly. Start your camera and hold a sign
            steady to recognize its letter.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    if not hasattr(mp, "solutions"):
        st.error(
            "This app requires MediaPipe 0.10.21 for its `solutions` API. "
            "Stop the running Streamlit server, then reinstall with "
            "`python -m pip install -r requirements.txt` and restart the app."
        )
        st.stop()

    try:
        model = load_model()
    except (OSError, EOFError, KeyError, pickle.PickleError, ModuleNotFoundError) as error:
        st.error(f"Could not load the trained model from `assets/model.p`: {error}")
        st.stop()

    if "recognized_text" not in st.session_state:
        st.session_state.recognized_text = ""
    if "recognition_state" not in st.session_state:
        st.session_state.recognition_state = RecognitionState(
            st.session_state.recognized_text
        )
    recognition_state = st.session_state.recognition_state

    camera_column, results_column = st.columns([1.55, 1], gap="large")

    with camera_column:
        with st.container(border=True):
            st.markdown(
                '<p class="section-title">Live camera</p>'
                '<p class="section-caption">Your hand landmarks and recognized letter appear on the video.</p>',
                unsafe_allow_html=True,
            )
            st.write("")
            webrtc_context = webrtc_streamer(
                key="sign-language-recognition",
                mode=WebRtcMode.SENDRECV,
                video_processor_factory=lambda: SignLanguageVideoProcessor(
                    model, recognition_state
                ),
                media_stream_constraints={
                    "video": {
                        "width": {"ideal": 480, "max": 480},
                        "height": {"ideal": 360, "max": 360},
                        "frameRate": {"ideal": 15, "max": 18},
                    },
                    "audio": False,
                },
                async_processing=True,
            )
            camera_active = webrtc_context.state.playing
            if camera_active:
                st_autorefresh(interval=750, key="recognition-refresh")

            st.caption(
                "Use the camera panel's **Start** and **Stop** controls to manage the webcam."
            )

    if not camera_active:
        recognition_state.set_tracking("", False)
    recognized_text, current_prediction, hand_detected = recognition_state.snapshot()
    st.session_state.recognized_text = recognized_text

    with results_column:
        with st.container(border=True):
            st.markdown(
                '<p class="section-title">Recognition status</p>'
                '<p class="section-caption">Live camera and hand tracking state</p>',
                unsafe_allow_html=True,
            )
            st.write("")
            camera_status, hand_status = st.columns(2)
            camera_status.metric("Camera", "Active" if camera_active else "Off")
            hand_status.metric("Hand", "Detected" if hand_detected else "Not detected")
            prediction = current_prediction if current_prediction else "—"
            safe_prediction = html.escape(prediction)
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="result-label">Currently identified letter</div>
                    <div class="result-value">{safe_prediction}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    with st.container(border=True):
        st.markdown(
            '<p class="section-title">Recognized text</p>'
            '<p class="section-caption">Letters are added after a sign is held steady for one second.</p>',
            unsafe_allow_html=True,
        )
        st.write("")
        controls = st.columns(3, gap="small")
        controls[0].button(
            "Clear text",
            use_container_width=True,
            on_click=recognition_state.clear_text,
        )
        controls[1].button(
            "Delete last",
            use_container_width=True,
            on_click=recognition_state.delete_last,
        )
        controls[2].button(
            "Add space",
            use_container_width=True,
            on_click=recognition_state.add_space,
        )
        st.session_state.recognized_text = recognition_state.snapshot()[0]
        text = st.session_state.recognized_text
        if text:
            safe_text = html.escape(text)
            st.markdown(
                f'<div class="recognized-output">{safe_text}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="recognized-output empty-output">'
                "Your recognized letters will appear here."
                "</div>",
                unsafe_allow_html=True,
            )
        st.caption(f"{len(text)} characters")

    st.markdown(
        """
        <div style="text-align:center; color:#71839b; font-size:.8rem; padding-top:1rem">
            SignSpeak · MediaPipe hand tracking · Random Forest recognition
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
