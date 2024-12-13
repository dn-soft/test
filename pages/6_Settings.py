import streamlit as st
from utils import *

st.title("⚙️ Settings")

# API 키 관리 섹션
st.header("🔑 API Key Management")
with st.expander("API Keys Configuration", expanded=True):
    api_keys = {}
    for provider, env_var in providers.items():
        st.subheader(provider)
        api_key = get_api_key(provider, env_var)
        api_keys[provider] = api_key
        if api_key:
            st.success(f"✅ API Key is set!")
            st.info(f"Available models: {', '.join(provider_models[provider])}")
        else:
            st.warning(f"⚠️ No API key set for {provider}")

# 기본 설정값
st.header("🎮 Default Parameters")
with st.form("default_params"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.default_temperature = st.slider(
            "Temperature:",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get('default_temperature', 0.7),
            step=0.1,
            help="Higher values make the output more random, lower values make it more focused and deterministic"
        )
        
        st.session_state.default_top_p = st.slider(
            "Top P:",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get('default_top_p', 1.0),
            step=0.1,
            help="Controls diversity via nucleus sampling"
        )
    
    with col2:
        st.session_state.default_max_tokens = st.number_input(
            "Max Tokens:",
            min_value=1,
            max_value=4096,
            value=st.session_state.get('default_max_tokens', 256),
            step=1,
            help="Maximum number of tokens to generate"
        )
        
        st.session_state.default_streaming = st.checkbox(
            "Enable Streaming by default",
            value=st.session_state.get('default_streaming', True),
            help="Stream the response token by token"
        )
    
    st.session_state.default_json_format = st.checkbox(
        "Use JSON format by default",
        value=st.session_state.get('default_json_format', False),
        help="Request responses in JSON format"
    )
    
    if st.form_submit_button("Save Default Settings"):
        st.success("Default settings saved successfully!")

# 모델 정보 표시
st.header("📚 Available Models")
for provider in providers:
    with st.expander(f"Models for {provider}"):
        st.write(f"Available models:")
        for model in provider_models[provider]:
            st.code(model)

# 도움말 섹션
st.header("❓ Help")
with st.expander("Usage Guide"):
    st.markdown("""
    ### How to use this app
    1. First, set up your API keys for the providers you want to use
    2. Configure your default parameters (temperature, max tokens, etc.)
    3. Go to the Chat page to start interacting with the AI models
    
    ### Tips
    - Higher temperature (>0.7) will give more creative responses
    - Lower temperature (<0.3) will give more focused and deterministic responses
    - JSON format is useful for structured data responses
    - Streaming shows the response as it's being generated
    """) 
    