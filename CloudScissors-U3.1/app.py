import streamlit as st
import time
from utils.ai_models import generate_response, AVAILABLE_MODELS

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
        
        # Chat input (will be fixed at bottom due to CSS)
        if prompt := st.chat_input("Type your message here..."):
            if not st.session_state.current_model:
                st.error("Please select an AI model first")
                return
                
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt, unsafe_allow_html=True)
                
            # Generate and display AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = generate_response(
                            st.session_state.current_model,
                            st.session_state.messages
                        )
                        
                        if not response or response.strip() == "":
                            st.error(f"Model {selected_model_name} returned an empty response. Please try again or select a different model.")
                            return
                            
                        # Create an empty container for typing animation
                        response_container = st.empty()
                        # Simulate typing animation
                        simulate_typing(response, response_container)
                        # Store the complete response
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response
                        })
                        # Force a rerun to ensure markdown is rendered
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error with model {selected_model_name}: {str(e)}")
                        st.info("Please try again or select a different model.")

if __name__ == "__main__":
    main() 