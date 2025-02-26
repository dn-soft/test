import streamlit as st
from litellm import completion
from utils import *
import json
from datetime import datetime

st.title("💬 Chat with Simulated AI")

# 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 초기화 버튼 추가
if st.button("대화 초기화"):
    st.session_state.messages = []  # 메시지 초기화
    st.success("대화가 초기화되었습니다.")  # 사용자에게 알림

# API 키 설정
with st.sidebar.expander("🔑 API Keys", expanded=False):
    api_keys = {}
    for provider, env_var in providers.items():
        api_key = get_api_key(provider, env_var)
        api_keys[provider] = api_key
        if api_key:
            st.success(f"{provider} API Key is set!")

# 시스템 프롬프트 설정
system_prompts = load_system_prompts()
if system_prompts:
    st.sidebar.subheader("🤖 시스템 프롬프트")
    system_template_names = ["기본 프롬프트..."] + [p['name'] for p in system_prompts]
    selected_system_template_1 = st.sidebar.selectbox("첫 번째 시스템 프롬프트 선택:", system_template_names, key="system_prompt_1")
    selected_system_template_2 = st.sidebar.text_area("두 번째 시스템 프롬프트 입력:", value="다른 AI에게 전달할 메시지입니다.", key="system_prompt_2")

    if selected_system_template_1 != "기본 프롬프트...":
        system_content_1 = next(p['content'] for p in system_prompts if p['name'] == selected_system_template_1)
    else:
        system_content_1 = "You are a helpful assistant."

    system_content_2 = selected_system_template_2 if selected_system_template_2 else "You are a simulated assistant."
else:
    system_content_1 = "You are a helpful assistant."
    system_content_2 = "You are a simulated assistant."

# 모델 선택 및 설정
available_providers = [provider for provider, api_key in api_keys.items() if api_key]
if available_providers:
    selected_provider = st.sidebar.selectbox("Select Provider:", available_providers)
    selected_model = st.sidebar.selectbox(
        "Select Model:",
        provider_models[selected_provider],
        key="model_selector"
    )

    # 매개변수 설정
    with st.sidebar.expander("🎮 고급 설정", expanded=False):
        temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        max_tokens = st.number_input("최대 토큰 수:", min_value=1, max_value=4096, value=256, step=1)
        top_p = st.slider("Top P:", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
        use_json_format = st.checkbox("JSON 형식으로 응답 받기", value=False)
        use_streaming = st.checkbox("Enable streaming", value=True)

        # 대화 반복 횟수 입력 (사이드바로 이동)
        num_iterations = st.number_input("대화 반복 횟수:", min_value=1, max_value=10, value=6, step=1)

    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 간 대화 반복
        current_prompt = prompt
        for i in range(num_iterations):
            current_system_content = system_content_1 if i % 2 == 0 else system_content_2
            current_role = "assistant" if i % 2 == 0 else "user"  # 역할 번갈아 설정

            # 메시지 구성
            # messages = [
            #     {"role": "system", "content": current_system_content},
            #     {"role": "user", "content": current_prompt},
            # ]
            messages = [{"role": "system", "content": current_system_content}] + st.session_state.messages

            # completion params 설정
            completion_params = {
                "model": selected_model,
                "messages": messages,
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

            # 스트리밍 응답 처리
            response_container = st.empty()
            full_response = ""

            try:
                if use_streaming:
                    for chunk in completion(**completion_params):
                        if selected_provider == "Anthropic":
                            content = chunk.delta.text
                        else:
                            content = chunk.choices[0].delta.content

                        if content:
                            full_response += content
                            response_container.markdown(full_response)
                else:
                    response = completion(**completion_params)
                    if selected_provider == "Anthropic":
                        full_response = response.content
                    else:
                        full_response = response.choices[0].message.content
                    response_container.markdown(full_response)

                # 응답을 채팅 히스토리에 추가
                if not st.session_state.messages or st.session_state.messages[-1]["content"] != full_response:
                    st.session_state.messages.append({"role": current_role, "content": full_response})
                    # current_prompt = full_response  # 다음 AI의 입력으로 설정
                    with st.chat_message(current_role):
                        st.markdown(full_response)
                        
                    # AI 응답을 다음 입력으로 설정
                    current_prompt = full_response

            except Exception as e:
                st.error(f"Error: {str(e)}")

    # 채팅 히스토리 다운로드 버튼
    if st.button("채팅 히스토리 다운로드 (JSON)"):
        chat_history_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
        st.download_button(
            label="채팅 히스토리 다운로드",
            data=chat_history_json,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

else:
    st.sidebar.warning("Please set at least one API key to use the models.") 