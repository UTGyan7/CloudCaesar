
# AI Chat Application Implementation Guide with Streamlit

## Project Overview
This guide details how to recreate the AI chat application using Streamlit framework. The application features real-time chat with AI models, conversation management, and a modern UI.

## Project Structure
```
ai_chat_app/
├── app.py
├── components/
│   ├── chat.py
│   ├── sidebar.py
│   └── message.py
├── utils/
│   ├── ai_models.py
│   └── storage.py
└── requirements.txt
```

## Setup Instructions

### 1. Dependencies
Create requirements.txt with necessary packages:

```txt
streamlit>=1.28.0
openai>=1.0.0
python-dotenv>=0.19.0
pandas
```

### 2. Main Application (app.py)

```python
import streamlit as st
from components.chat import ChatContainer
from components.sidebar import Sidebar
import utils.storage as storage

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

def main():
    # Two-column layout
    sidebar, main = st.columns([1, 4])
    
    with sidebar:
        Sidebar()
    
    with main:
        ChatContainer()

if __name__ == "__main__":
    main()
```

### 3. Chat Component (components/chat.py)

```python
import streamlit as st
from utils.ai_models import generate_response

def ChatContainer():
    # Chat container styling
    st.markdown("""
        <style>
        .chat-container {
            padding: 1rem;
            border-radius: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        if not st.session_state.current_model:
            st.error("Please select an AI model first")
            return
            
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # Generate and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(
                    st.session_state.current_model,
                    st.session_state.messages
                )
                st.write(response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
```

### 4. Sidebar Component (components/sidebar.py)

```python
import streamlit as st
from utils.storage import get_conversations, create_conversation

def Sidebar():
    st.sidebar.title("AI Chat Assistant")
    
    # Model selection
    models = [
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-2",
        "gemini-pro"
    ]
    
    selected_model = st.sidebar.selectbox(
        "Select AI Model",
        models,
        key="model_selector"
    )
    
    if selected_model != st.session_state.current_model:
        st.session_state.current_model = selected_model
    
    # Conversations list
    st.sidebar.subheader("Conversations")
    
    if st.sidebar.button("New Conversation"):
        create_conversation()
        st.session_state.messages = []
    
    conversations = get_conversations()
    for conv in conversations:
        if st.sidebar.button(conv["title"], key=conv["id"]):
            st.session_state.conversation_id = conv["id"]
            st.session_state.messages = conv["messages"]
```

### 5. AI Models Integration (utils/ai_models.py)

```python
import openai
import os

openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.base_url = "https://openrouter.ai/api/v1"  # Example; confirm actual base

def generate_response(model: str, messages: List[Dict]) -> str:
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Error generating response: {str(e)}"
```

### 6. Storage Implementation (utils/storage.py)

```python
import sqlite3
from typing import List, Dict

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_conversations() -> List[Dict]:
    """Retrieve all conversations"""
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('SELECT * FROM conversations ORDER BY created_at DESC')
    conversations = c.fetchall()
    conn.close()
    return [
        {"id": row[0], "title": row[1], "created_at": row[2]}
        for row in conversations
    ]

def create_conversation() -> int:
    """Create a new conversation"""
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO conversations (title) VALUES (?)',
        [f"Conversation {get_conversation_count() + 1}"]
    )
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return new_id

def get_conversation_count() -> int:
    """Get total number of conversations"""
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM conversations')
    count = c.fetchone()[0]
    conn.close()
    return count
```

## Running the Application

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

The application will be available at `http://0.0.0.0:5000`.

## Key Features
- Real-time chat interface with AI models
- Conversation management and persistence
- Modern, responsive UI
- Support for multiple AI models
- Message history
- Easy-to-use sidebar navigation

## Customization
- Modify the theme by adjusting Streamlit's theme configuration
- Add more AI models by extending the models list
- Customize the UI by adding CSS styles through st.markdown
- Implement additional features like file uploads or code syntax highlighting

## Deployment
Deploy your Streamlit app on Replit by:
1. Creating a new Repl with Python
2. Upload your project files
3. Set the run command to `streamlit run app.py`
4. Use the Replit deployment feature to make your app publicly accessible
