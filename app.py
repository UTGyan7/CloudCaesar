import streamlit as st
import time
from utils.ai_models import generate_response, AVAILABLE_MODELS
from vosk import Model, KaldiRecognizer
import pyaudio
import json
from gtts import gTTS
import tempfile
import os
import base64
from io import BytesIO
import wave
import numpy as np
import queue
import threading

# Page configuration
st.set_page_config(
    page_title="AI Chat Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_model" not in st.session_state:
    st.session_state.current_model = None
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

def simulate_typing(text: str, container):
    """Simulate typing animation for the assistant's response"""
    words = text.split()
    for i in range(len(words)):
        container.markdown(" ".join(words[:i+1]), unsafe_allow_html=True)
        time.sleep(0.05)  # Adjust typing speed here

def text_to_speech(text: str) -> str:
    """Convert text to speech and return base64 encoded audio"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return base64.b64encode(fp.read()).decode()
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")
        return ""

def save_audio_to_file(audio_data, filename="debug_recording.wav"):
    """Save audio data to a WAV file for debugging"""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(16000)
        wf.writeframes(audio_data)

def get_audio_level(data):
    """Calculate audio level from raw audio data"""
    audio_data = np.frombuffer(data, dtype=np.int16)
    return np.abs(audio_data).mean()

def speech_to_text() -> str:
    """Convert speech to text using Vosk offline speech recognition"""
    try:
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Audio parameters
        CHUNK = 8000
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        # Use default input device
        default_input = p.get_default_input_device_info()
        
        # Create a queue for audio data
        audio_queue = queue.Queue()
        
        # Load Vosk model
        model_path = "vosk-model-small-en-us-0.15"
        if not os.path.exists(model_path):
            st.error("Vosk model not found. Please download it from https://alphacephei.com/vosk/models")
            return ""
        
        model = Model(model_path)
        rec = KaldiRecognizer(model, RATE)
        
        # Audio callback function
        def audio_callback(in_data, frame_count, time_info, status):
            audio_queue.put(in_data)
            return (in_data, pyaudio.paContinue)
        
        # Open audio stream
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=default_input['index'],
            frames_per_buffer=CHUNK,
            stream_callback=audio_callback
        )
        
        stream.start_stream()
        st.info("Listening... (Speak now)")
        
        # Process audio for 5 seconds
        start_time = time.time()
        audio_data = []
        silence_threshold = 500  # Adjust this value based on your microphone
        silence_counter = 0
        
        while time.time() - start_time < 5:
            try:
                data = audio_queue.get(timeout=0.1)
                audio_level = get_audio_level(data)
                st.progress(min(audio_level / 1000, 1.0))
                if audio_level > silence_threshold:
                    audio_data.append(data)
                    silence_counter = 0
                else:
                    silence_counter += 1
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if result.get("text", ""):
                        stream.stop_stream()
                        stream.close()
                        p.terminate()
                        return result["text"]
            except queue.Empty:
                continue
        result = json.loads(rec.FinalResult())
        if audio_data:
            save_audio_to_file(b''.join(audio_data))
        stream.stop_stream()
        stream.close()
        p.terminate()
        if not result.get("text", ""):
            st.warning("No speech detected. Please try again.")
            return ""
        return result.get("text", "")
    except Exception as e:
        st.error(f"Error in speech recognition: {str(e)}")
        return ""

def main():
    # Two-column layout
    sidebar, main = st.columns([1, 4])
    
    with sidebar:
        # Make sidebar sticky and scrollable
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                position: fixed;
                top: 0;
                bottom: 0;
                overflow-y: auto;
            }
            [data-testid="stSidebar"] > div:first-child {
                padding-top: 2rem;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.title("AI Chat Assistant")
        
        # Model selection
        model_names = list(AVAILABLE_MODELS.keys())
        
        if not model_names:
            st.error("No models available. Please check if models.csv exists and is properly formatted.")
            st.stop()
            
        selected_model_name = st.selectbox(
            "Select AI Model",
            model_names,
            key="model_selector"
        )
        
        if selected_model_name:
            selected_model_id = AVAILABLE_MODELS[selected_model_name]
            if selected_model_id != st.session_state.current_model:
                st.session_state.current_model = selected_model_id
                st.info(f"Selected model: {selected_model_name}")
            
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Voice chat controls
        st.markdown("---")
        st.subheader("Voice Chat")
        voice_enabled = st.checkbox("Enable Voice Chat", value=st.session_state.get("voice_enabled", False), key="voice_enabled")
        if voice_enabled:
            if st.button("🎤 Start Voice Input"):
                with st.spinner("Processing speech..."):
                    text = speech_to_text()
                    if text:
                        st.success(f"Recognized: {text}")
                        st.session_state.messages.append({"role": "user", "content": text})
                        st.rerun()
                    else:
                        st.error("Could not recognize speech. Please try again.")
    
    with main:
        # Chat container with fixed input at bottom
        st.markdown("""
            <style>
            /* Main container styling */
            .main .block-container {
                padding-bottom: 100px;
                max-width: 100%;
            }
            
            /* Chat container */
            .chat-container {
                padding: 1rem;
                border-radius: 0.5rem;
                background: rgba(255, 255, 255, 0.05);
                height: calc(100vh - 200px);
                overflow-y: auto;
            }
            
            /* Message styling */
            .stChatMessage {
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: 0.5rem;
            }
            
            /* Markdown content styling */
            .markdown-content {
                line-height: 1.6;
            }
            .markdown-content pre {
                background-color: #2D2D2D;
                padding: 1rem;
                border-radius: 0.5rem;
                overflow-x: auto;
            }
            .markdown-content code {
                background-color: #2D2D2D;
                padding: 0.2rem 0.4rem;
                border-radius: 0.3rem;
            }
            
            /* Fix input at bottom right */
            .stChatInput {
                position: fixed;
                bottom: 0;
                right: 0;
                width: 80%;  /* Match the main column width */
                background-color: var(--background-color);
                padding: 1rem;
                z-index: 100;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            /* Ensure the input container is properly aligned */
            .stChatInput > div {
                max-width: 100%;
                margin: 0 auto;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Create a container for messages
        messages_container = st.container()
        
        # Display messages in the container
        with messages_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"], unsafe_allow_html=True)
                    if message["role"] == "assistant" and st.session_state.get("voice_enabled", False):
                        audio_base64 = text_to_speech(message["content"])
                        if audio_base64:
                            audio_html = f"""
                                <audio controls autoplay>
                                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                    Your browser does not support the audio element.
                                </audio>
                            """
                            st.markdown(audio_html, unsafe_allow_html=True)
                        else:
                            st.warning("TTS failed for this message.")
        
        # Chat input (will be fixed at bottom due to CSS)
        if prompt := st.chat_input("Type your message here..."):
            if not st.session_state.current_model:
                st.error("Please select an AI model first")
                return
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt, unsafe_allow_html=True)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = generate_response(
                            st.session_state.current_model,
                            st.session_state.messages
                        )
                        if not response or response.strip() == "":
                            st.error(f"Model returned an empty response. Please try again or select a different model.")
                            return
                        response_container = st.empty()
                        simulate_typing(response, response_container)
                        audio_base64 = text_to_speech(response)
                        audio_html = f"""
                            <audio controls autoplay>
                                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                Your browser does not support the audio element.
                            </audio>
                        """
                        st.markdown(audio_html, unsafe_allow_html=True)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.info("Please try again or select a different model.")
        
        # --- NEW: Auto-generate assistant reply after voice input ---
        if (
            st.session_state.messages
            and st.session_state.messages[-1]["role"] == "user"
            and (len(st.session_state.messages) < 2 or st.session_state.messages[-2]["role"] != "assistant")
        ):
            # Only generate if last message is user and not already replied
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = generate_response(
                            st.session_state.current_model,
                            st.session_state.messages
                        )
                        if not response or response.strip() == "":
                            st.error(f"Model returned an empty response. Please try again or select a different model.")
                            return
                        response_container = st.empty()
                        simulate_typing(response, response_container)
                        audio_base64 = text_to_speech(response)
                        audio_html = f"""
                            <audio controls autoplay>
                                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                Your browser does not support the audio element.
                            </audio>
                        """
                        st.markdown(audio_html, unsafe_allow_html=True)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.info("Please try again or select a different model.")

if __name__ == "__main__":
    main() 