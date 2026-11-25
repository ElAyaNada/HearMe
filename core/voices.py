VOICES = {
    "female": {"label": "Voix féminine", "edge_voice": "fr-FR-DeniseNeural"},
    "male": {"label": "Voix masculine", "edge_voice": "fr-FR-HenriNeural"},
}
DEFAULT_GENDER = "female"


def edge_voice_for(gender: str) -> str:
    """Nom de la voix edge-tts à utiliser (servira au jour 7)."""
    return VOICES.get(gender, VOICES[DEFAULT_GENDER])["edge_voice"]