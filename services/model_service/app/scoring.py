import difflib
import re
import wave


def get_audio_duration(wav_path):
    """Real duration (seconds) read from the WAV file itself."""

    try:

        with wave.open(wav_path, "rb") as wf:

            frames = wf.getnframes()
            rate = wf.getframerate()

            return frames / float(rate) if rate else 0.0

    except Exception as e:

        print("Duration read failed:", e)

        return 0.0


def _normalize(text):

    text = text.lower().strip()

    return re.sub(r"[^\w\s]", "", text)


def compute_similarity_score(transcript, target_text):
    """
    Text-similarity between what was said and the target phrase, as a proxy for
    pronunciation accuracy: mispronounced or dropped words show up as transcription
    mismatches when using a strong ASR model like Whisper.

    Returns None when there's no target phrase to compare against (free practice).
    """

    if not target_text:

        return None

    target = _normalize(target_text)
    heard = _normalize(transcript)

    if not target or not heard:

        return 0.0

    return round(
        difflib.SequenceMatcher(None, target, heard).ratio(),
        3,
    )
