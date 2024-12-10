import dotenv
import os
import streamlit as st
from litellm import completion
import json
from datetime import datetime
from typing import List, Dict

# Load environment variables
dotenv.load_dotenv()

# API key handling
def get_api_key(provider: str, env_var: str) -> str:
    api_key = os.getenv(env_var)
    if not api_key:
        api_key = st.text_input(f"Enter your {provider} API Key (optional):", type="password", key=f"{provider}_key")
        if api_key:
            os.environ[env_var] = api_key
    return api_key

# Dictionary of supported providers and their environment variables
providers = {
    "OpenAI (Default)": "OPENAI_API_KEY",
    "OpenAI (Backup)": "OPENAI_API_KEY_BACKUP",
    "Anthropic": "ANTHROPIC_API_KEY",
    "Azure": "AZURE_API_KEY",
    # Add more providers as needed
}

# Create expandable section for API keys in sidebar
with st.sidebar.expander("🔑 API Keys", expanded=False):
    # Create API key inputs for each provider
    api_keys = {}
    for provider, env_var in providers.items():
        api_key = get_api_key(provider, env_var)
        api_keys[provider] = api_key
        if api_key:
            st.success(f"{provider} API Key is set!")

# 추가 매개변수 설정
temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
max_tokens = st.sidebar.number_input("최대 토큰 수:", min_value=1, max_value=4096, value=256, step=1)
top_p = st.sidebar.slider("Top P:", min_value=0.0, max_value=1.0, value=1.0, step=0.1)

response = completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    temperature=temperature,
    max_tokens=max_tokens,
    top_p=top_p,
)

st.write(response)
