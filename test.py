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

# Dictionary of supported providers and their models
provider_models = {
    "OpenAI (Default)": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    "OpenAI (Backup)": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    "Anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-2.1"],
    "Azure": ["gpt-4", "gpt-3.5-turbo"],
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

# Model selection based on available API keys
available_providers = [provider for provider, api_key in api_keys.items() if api_key]
if available_providers:
    selected_provider = st.sidebar.selectbox("Select Provider:", available_providers)
    selected_model = st.sidebar.selectbox(
        "Select Model:",
        provider_models[selected_provider],
        key="model_selector"
    )
else:
    st.sidebar.warning("Please set at least one API key to use the models.")
    selected_provider = None
    selected_model = None

# 추가 매개변수 설정
temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
max_tokens = st.sidebar.number_input("최대 토큰 수:", min_value=1, max_value=4096, value=256, step=1)
top_p = st.sidebar.slider("Top P:", min_value=0.0, max_value=1.0, value=1.0, step=0.1)

# JSON 응답 형식 선택 옵션 추가
use_json_format = st.sidebar.checkbox("JSON 형식으로 응답 받기", value=False)

# Update completion params with selected model
completion_params = {
    "model": selected_model,
    "messages": [{"role": "user", "content": "Hello, how are you? Answer in json format"}],
    "temperature": temperature,
    "max_tokens": max_tokens,
    "top_p": top_p
}

# Add provider to completion params if needed (for non-OpenAI providers)
if selected_provider == "Anthropic":
    completion_params["api_key"] = api_keys[selected_provider]
    completion_params["model_name"] = selected_model

if selected_provider == "Azure":
    completion_params["api_key"] = api_keys[selected_provider]
    completion_params["azure"] = True

if use_json_format:
    completion_params["response_format"] = {"type": "json_object"}

response = completion(**completion_params)

st.write(response)
