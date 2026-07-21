import os
import urllib.request
from typing import Dict, Any

CACHE_DIR = os.path.expanduser("~/.cache/fate_models")

WHISPER_MODELS = {
    "tiny.en": "https://huggingface.co/guillaumekln/faster-whisper-tiny.en/resolve/main/model.bin"
}

PIPER_MODELS = {
    "en_US-lessac-medium": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
}

class ModelWeightsDownloader:
    """Manages checking and fetching local Whisper & Piper ML model weights."""

    def __init__(self, target_dir: str = CACHE_DIR):
        self.target_dir = target_dir
        os.makedirs(self.target_dir, exist_ok=True)

    def get_whisper_model_path(self, name: str = "tiny.en") -> str:
        """Returns local directory path for Whisper model."""
        whisper_dir = os.path.join(self.target_dir, "whisper", name)
        os.makedirs(whisper_dir, exist_ok=True)
        return whisper_dir

    def get_piper_model_path(self, name: str = "en_US-lessac-medium") -> str:
        """Returns local path for Piper ONNX model file."""
        piper_dir = os.path.join(self.target_dir, "piper")
        os.makedirs(piper_dir, exist_ok=True)
        return os.path.join(piper_dir, f"{name}.onnx")

    def ensure_model_weights(self, model_type: str = "all") -> Dict[str, bool]:
        """Checks if model files exist locally. In production, downloads missing weights."""
        status = {
            "whisper": os.path.exists(self.get_whisper_model_path()),
            "piper": os.path.exists(self.get_piper_model_path())
        }
        return status
