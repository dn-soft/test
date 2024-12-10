import os
import streamlit as st
import dotenv
from datetime import datetime
import json
from typing import List, Dict

# Load environment variables
dotenv.load_dotenv()

def get_api_key(provider: str, env_var: str) -> str:
    api_key = os.getenv(env_var)
    if not api_key:
        api_key = st.text_input(f"Enter your {provider} API Key (optional):", type="password", key=f"{provider}_key")
        if api_key:
            os.environ[env_var] = api_key
    return api_key

# 공통으로 사용할 설정들
providers = {
    "OpenAI (Default)": "OPENAI_API_KEY",
    "OpenAI (Backup)": "OPENAI_API_KEY_BACKUP",
    "Anthropic": "ANTHROPIC_API_KEY",
    "Azure": "AZURE_API_KEY",
}

provider_models = {
    "OpenAI (Default)": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    "OpenAI (Backup)": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    "Anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-2.1"],
    "Azure": ["gpt-4", "gpt-3.5-turbo"],
}

def get_completion_params(selected_model, selected_provider, api_keys, temperature, max_tokens, top_p, use_streaming, use_json_format):
    completion_params = {
        "model": selected_model,
        "messages": [{"role": "user", "content": "Hello, how are you? Answer in json format"}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "stream": use_streaming
    }

    if selected_provider == "Anthropic":
        completion_params["api_key"] = api_keys[selected_provider]
        completion_params["model_name"] = selected_model

    if selected_provider == "Azure":
        completion_params["api_key"] = api_keys[selected_provider]
        completion_params["azure"] = True

    if use_json_format:
        completion_params["response_format"] = {"type": "json_object"}
        
    return completion_params 
  