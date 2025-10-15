"""Streamlit frontend for AI Voice Knowledge Assistant."""
import streamlit as st
import requests
from pathlib import Path
import json

from frontend.auth.auth_handler import AuthHandler
from frontend.utils.session_manager import SessionManager
from frontend.utils.api_client import APIClient


# Page configuration
st.set_page_config(
    page_title="AI Voice Knowledge Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []


def login_page():
    """Display login page."""
    st.title("🤖 AI Voice Knowledge Assistant")
    st.subheader("Please login to continue")

    with st.form("login_form"):
        access_key = st.text_input(
            "Access Key",
            type="password",
            placeholder="Enter your access key"
        )
        submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            if access_key:
                auth = AuthHandler()
                result = auth.login(access_key)

                if result['success']:
                    st.session_state.authenticated = True
                    st.session_state.token = result['token']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(f"Login failed: {result.get('error', 'Invalid credentials')}")
            else:
                st.warning("Please enter your access key")

    st.info("Default access key: `admin_hasan_007_no_exit`")


def sidebar():
    """Display sidebar with navigation and controls."""
    with st.sidebar:
        st.title("Navigation")

        # User info
        st.success("✓ Authenticated")

        # Logout button
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.token = None
            st.session_state.conversation_history = []
            st.rerun()

        st.divider()

        # Document upload section
        st.subheader("📄 Document Upload")
        uploaded_file = st.file_uploader(
            "Upload document to knowledge base",
            type=['pdf', 'docx', 'xlsx', 'csv', 'txt'],
            help="Upload documents to add to the knowledge base"
        )

        if uploaded_file and st.button("Upload Document", use_container_width=True):
            api_client = APIClient(st.session_state.token)
            result = api_client.upload_document(uploaded_file)

            if result.get('status') == 'success':
                st.success(f"✓ {result.get('filename')} uploaded successfully!")
                st.session_state.uploaded_files.append(result.get('filename'))
            else:
                st.error(f"Upload failed: {result.get('message', 'Unknown error')}")

        st.divider()

        # Conversation controls
        st.subheader("💬 Conversation")

        turns_count = len(st.session_state.conversation_history)
        st.metric("Conversation Turns", f"{turns_count}/20")

        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.conversation_history = []
            st.success("Conversation cleared!")
            st.rerun()

        st.divider()

        # Uploaded files
        if st.session_state.uploaded_files:
            st.subheader("📚 Uploaded Files")
            for filename in st.session_state.uploaded_files:
                st.text(f"• {filename}")


def chat_interface():
    """Display main chat interface."""
    st.title("🤖 AI Voice Knowledge Assistant")

    # Display conversation history
    for turn in st.session_state.conversation_history:
        with st.chat_message("user"):
            st.write(turn.get('user', ''))

        with st.chat_message("assistant"):
            st.write(turn.get('assistant', ''))

    # Chat input
    user_input = st.chat_input("Ask a question about your documents...")

    if user_input:
        # Add user message to history
        with st.chat_message("user"):
            st.write(user_input)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                api_client = APIClient(st.session_state.token)
                result = api_client.query(user_input, st.session_state.conversation_history)

                if result.get('answer'):
                    st.write(result['answer'])

                    # Show sources if available
                    if result.get('sources'):
                        with st.expander("📚 Sources"):
                            for source in result['sources']:
                                st.text(f"• {source.get('filename', 'Unknown')} (chunk {source.get('chunk_index', 0)})")

                else:
                    st.error("Failed to generate response")

        # Update conversation history (keep last 20 turns)
        st.session_state.conversation_history.append({
            'user': user_input,
            'assistant': result.get('answer', 'Error generating response')
        })

        if len(st.session_state.conversation_history) > 20:
            st.session_state.conversation_history = st.session_state.conversation_history[-20:]

        st.rerun()


def voice_interface():
    """Display voice interaction interface."""
    st.subheader("🎤 Voice Interaction")

    col1, col2 = st.columns(2)

    with col1:
        st.info("Voice recording feature will be integrated with WebRTC")
        audio_file = st.file_uploader("Upload audio file", type=['wav', 'mp3', 'ogg'])

        if audio_file and st.button("Transcribe Audio"):
            api_client = APIClient(st.session_state.token)
            result = api_client.transcribe_audio(audio_file)

            if result.get('status') == 'success':
                st.success("Transcription:")
                st.write(result.get('text', ''))
            else:
                st.error("Transcription failed")

    with col2:
        st.info("Text-to-speech feature available")
        tts_text = st.text_area("Enter text for speech synthesis")

        if st.button("Generate Speech") and tts_text:
            api_client = APIClient(st.session_state.token)
            result = api_client.synthesize_speech(tts_text)

            if result.get('status') == 'success':
                st.success("Speech generated successfully!")
                # Audio playback would be implemented here
            else:
                st.error("TTS generation failed")


def main():
    """Main application entry point."""
    init_session_state()

    if not st.session_state.authenticated:
        login_page()
    else:
        sidebar()

        # Main content tabs
        tab1, tab2 = st.tabs(["💬 Chat", "🎤 Voice"])

        with tab1:
            chat_interface()

        with tab2:
            voice_interface()


if __name__ == "__main__":
    main()
