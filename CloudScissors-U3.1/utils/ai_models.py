import os
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize OpenAI client with OpenRouter headers
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
    default_headers={
        "HTTP-Referer": "https://github.com/yourusername/your-repo",  # Required for OpenRouter
        "X-Title": "Cloud Scissors U3.1"  # Optional but recommended
    }
)

# Load models from CSV
def load_models():
    try:
        models_df = pd.read_csv('models.csv')
        # Strip whitespace from column names
        models_df.columns = models_df.columns.str.strip()
        print("Loaded models from CSV:", models_df)  # Debug print
        model_dict = dict(zip(models_df['Model Name'], models_df['Model ID']))
        print("Created model dictionary:", model_dict)  # Debug print
        return model_dict
    except Exception as e:
        print(f"Error loading models: {e}")
        return {}

# Get available models
AVAILABLE_MODELS = load_models()
print("Available models:", AVAILABLE_MODELS)  # Debug print

def generate_response(model_id: str, messages: List[Dict]) -> str:
    """
    Generate a response from the selected AI model.
    
    Args:
        model_id (str): The model ID to use
        messages (List[Dict]): List of message dictionaries with 'role' and 'content'
    
    Returns:
        str: The generated response
    """
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Detailed error: {str(e)}")  # Debug print
        return f"Error generating response: {str(e)}" 