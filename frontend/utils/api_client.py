"""API client for communicating with backend services."""
import requests
from typing import Dict, List, Optional, Any


class APIClient:
    """Client for backend API communication."""

    def __init__(self, token: str, base_url: str = "http://localhost:8000"):
        """
        Initialize API client.

        Args:
            token: JWT authentication token
            base_url: Base URL of the backend API
        """
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    def upload_document(self, file) -> Dict:
        """
        Upload document to knowledge base.

        Args:
            file: File object to upload

        Returns:
            Upload result
        """
        try:
            files = {"file": (file.name, file.getvalue(), file.type)}

            response = requests.post(
                f"{self.base_url}/documents/upload",
                headers=self.headers,
                files=files,
                timeout=60
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": response.json().get("detail", "Upload failed")
                }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        """
        Query the knowledge base.

        Args:
            query: User query
            conversation_history: Previous conversation turns

        Returns:
            Query response with answer and sources
        """
        try:
            payload = {
                "query": query,
                "conversation_history": conversation_history or []
            }

            response = requests.post(
                f"{self.base_url}/query",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "answer": "Error: Unable to process query",
                    "sources": []
                }

        except Exception as e:
            return {
                "answer": f"Error: {str(e)}",
                "sources": []
            }

    def transcribe_audio(self, audio_file) -> Dict:
        """
        Transcribe audio to text.

        Args:
            audio_file: Audio file object

        Returns:
            Transcription result
        """
        try:
            files = {"file": (audio_file.name, audio_file.getvalue(), audio_file.type)}

            response = requests.post(
                f"{self.base_url}/stt/transcribe",
                headers=self.headers,
                files=files,
                timeout=60
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "text": ""
                }

        except Exception as e:
            return {
                "status": "error",
                "text": "",
                "error": str(e)
            }

    def synthesize_speech(self, text: str, voice_id: Optional[str] = None) -> Dict:
        """
        Convert text to speech.

        Args:
            text: Text to convert
            voice_id: Optional voice ID

        Returns:
            TTS result
        """
        try:
            payload = {
                "text": text,
                "voice_id": voice_id
            }

            response = requests.post(
                f"{self.base_url}/tts/synthesize",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error"
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
