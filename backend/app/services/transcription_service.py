import whisper
import os

# Load the base model lazily to avoid crashing on startup if network is slow/unavailable
# Base is a good balance between speed and accuracy for local development
_model = None

def get_whisper_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model

def transcribe_media(file_path: str) -> dict:
    """
    Transcribes audio or video files using OpenAI's Whisper model.
    Returns a dictionary with the full text and timestamped segments.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Media file not found at: {file_path}")

    try:
        # Transcribe the media file
        # Whisper handles audio/video conversion internally via ffmpeg
        result = get_whisper_model().transcribe(file_path)
        
        return {
            "full_text": result.get("text", ""),
            "segments": [
                {
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"]
                }
                for segment in result.get("segments", [])
            ]
        }
        
    except Exception as e:
        # Re-raise for the API layer to handle
        raise Exception(f"Transcription failed: {str(e)}")
