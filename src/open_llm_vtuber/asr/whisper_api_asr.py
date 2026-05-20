import io
import wave

import httpx
import numpy as np
from loguru import logger

from .asr_interface import ASRInterface


class VoiceRecognition(ASRInterface):
    def __init__(
        self,
        base_url: str,
        api_key: str | None,
        model: str,
        language: str | None = None,
        prompt: str | None = None,
        hotwords: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        if not base_url:
            raise ValueError("Whisper API requires a base_url.")
        if not model:
            raise ValueError("Whisper API requires a model.")

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.model = model
        self.language = language
        self.prompt = prompt
        self.hotwords = hotwords
        self.timeout = timeout
        self.endpoint = f"{self.base_url}/v1/audio/transcriptions"

    def _build_audio_buffer(self, audio: np.ndarray) -> io.BytesIO:
        audio = np.asarray(audio, dtype=np.float32)
        audio = np.clip(audio, -1, 1)
        audio_integer = (audio * 32767).astype(np.int16)

        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, "wb") as wf:
            wf.setnchannels(self.NUM_CHANNELS)
            wf.setsampwidth(self.SAMPLE_WIDTH)
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(audio_integer.tobytes())

        audio_buffer.seek(0)
        return audio_buffer

    def transcribe_np(self, audio: np.ndarray) -> str:
        logger.info("Transcribing audio (WhisperAPI)...")

        audio_buffer = self._build_audio_buffer(audio)
        data = {
            "model": self.model,
            "response_format": "json",
        }

        if self.language:
            data["language"] = self.language
        if self.prompt:
            data["prompt"] = self.prompt
        if self.hotwords:
            data["hotwords"] = self.hotwords

        headers = {}
        if self.api_key.strip():
            headers["Authorization"] = f"Bearer {self.api_key}"
        files = {
            "file": ("audio.wav", audio_buffer, "audio/wav"),
        }

        try:
            response = httpx.post(
                url=self.endpoint,
                headers=headers,
                data=data,
                files=files,
                timeout=self.timeout,
            )

            if response.status_code == 404:
                raise ValueError(
                    f"Whisper API returned 404 for model '{self.model}'. "
                    "Check that the model name is correct and available on the server."
                )
            if response.status_code == 500:
                raise ValueError(
                    "Whisper API returned 500. This usually indicates a server-side "
                    "configuration issue or an unavailable model."
                )

            response.raise_for_status()
            payload = response.json()
            text = payload.get("text")
            if text is None:
                raise ValueError(
                    f"Whisper API response did not include a 'text' field: {payload}"
                )

            return text
        except httpx.RequestError as e:
            logger.error(f"Whisper API connection error: {e}")
            raise ConnectionError(f"Failed to connect to Whisper API: {e}") from e
        except httpx.HTTPStatusError as e:
            logger.error(
                "Whisper API request failed with status {}: {}",
                e.response.status_code,
                e.response.text,
            )
            raise
