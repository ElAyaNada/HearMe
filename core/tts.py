import asyncio

import edge_tts

from core.voices import edge_voice_for


async def _synthesize(text: str, voice: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice)
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return bytes(audio)


def synthesize(text: str, gender: str, lang: str = "fr") -> bytes:
    """Renvoie un MP3. Nécessite internet. Lève une exception si le service est injoignable."""
    audio = asyncio.run(_synthesize(text, edge_voice_for(gender, lang)))
    if not audio:
        raise RuntimeError("Aucun audio généré.")
    return audio