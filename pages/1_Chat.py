import streamlit as st
from litellm import completion
from utils import *

st.title("💬 Chat")

# API 키 설정
with st.sidebar.expander("🔑 API Keys", expanded=False):
    api_keys = {}
    for provider, env_var in providers.items():
        api_key = get_api_key(provider, env_var)
        api_keys[provider] = api_key
        if api_key:
            st.success(f"{provider} API Key is set!")

# 모델 선택
available_providers = [provider for provider, api_key in api_keys.items() if api_key]
if available_providers:
    selected_provider = st.sidebar.selectbox("Select Provider:", available_providers)
    selected_model = st.sidebar.selectbox(
        "Select Model:",
        provider_models[selected_provider],
        key="model_selector"
    )

    # 매개변수 설정
    temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    max_tokens = st.sidebar.number_input("최대 토큰 수:", min_value=1, max_value=4096, value=256, step=1)
    top_p = st.sidebar.slider("Top P:", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
    use_json_format = st.sidebar.checkbox("JSON 형식으로 응답 받기", value=False)
    use_streaming = st.sidebar.checkbox("Enable streaming", value=True)

    # 채팅 UI
    chat_container = st.empty()
    
    # completion params 가져오기
    completion_params = get_completion_params(
        selected_model, selected_provider, api_keys,
        temperature, max_tokens, top_p,
        use_streaming, use_json_format
    )

    if use_streaming:
        response_container = st.empty()
        full_response = ""
        
        for chunk in completion(**completion_params):
            if selected_provider == "Anthropic":
                content = chunk.delta.text
            else:  # OpenAI, Azure
                content = chunk.choices[0].delta.content
                
            if content:
                full_response += content
                response_container.markdown(full_response)
    else:
        response = completion(**completion_params)
        st.write(response)
else:
    st.sidebar.warning("Please set at least one API key to use the models.")