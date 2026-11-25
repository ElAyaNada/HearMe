VOICES = {
    "female": {"label": "Voix féminine"},
    "male": {"label": "Voix masculine"},
}
DEFAULT_GENDER = "female"

LANGUAGES = {"fr": "Français", "en": "English"}

EDGE_VOICES = {
    ("female", "fr"): "fr-FR-DeniseNeural",
    ("male", "fr"): "fr-FR-HenriNeural",
    ("female", "en"): "en-US-JennyNeural",
    ("male", "en"): "en-US-GuyNeural",
}


def edge_voice_for(gender: str, lang: str = "fr") -> str:
    """Nom de la voix edge-tts pour un genre et une langue."""
    return EDGE_VOICES.get((gender, lang), EDGE_VOICES[(DEFAULT_GENDER, "fr")])