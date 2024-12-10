import streamlit as st
from litellm import completion
from utils import *
import json
from datetime import datetime

st.title("💬 Chat")

# 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# API 키 설정
with st.sidebar.expander("🔑 API Keys", expanded=False):
    api_keys = {}
    for provider, env_var in providers.items():
        api_key = get_api_key(provider, env_var)
        api_keys[provider] = api_key
        if api_key:
            st.success(f"{provider} API Key is set!")

# 시스템 프롬프트 선택
system_prompts = load_system_prompts()
if system_prompts:
    st.sidebar.subheader("🤖 시스템 프롬프트")
    system_template_names = ["기본 프롬프트..."] + [p['name'] for p in system_prompts]
    selected_system_template = st.sidebar.selectbox("시스템 프롬프트 선택:", system_template_names)
    
    if selected_system_template != "기본 프롬프트...":
        system_content = next(p['content'] for p in system_prompts if p['name'] == selected_system_template)
    else:
        system_content = "You are a helpful assistant."
else:
    system_content = "You are a helpful assistant."

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
    with st.sidebar.expander("🎮 고급 설정", expanded=False):
        temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        max_tokens = st.number_input("최대 토큰 수:", min_value=1, max_value=4096, value=256, step=1)
        top_p = st.slider("Top P:", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
        use_json_format = st.checkbox("JSON 형식으로 응답 받기", value=False)
        use_streaming = st.checkbox("Enable streaming", value=True)

    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답
        with st.chat_message("assistant"):
            # 전체 메시지 히스토리 구성
            messages = [
                {"role": "system", "content": system_content}
            ] + st.session_state.messages

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
                        else:  # OpenAI, Azure
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
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # 채팅 관리 섹션 (사이드바 하단에 추가)
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 채팅 관리")
    
    # 채팅 저장 버튼
    if st.session_state.messages:  # 메시지가 있을 때만 저장 버튼 표시
        if st.sidebar.button("현재 채팅 저장"):
            file_path = save_chat_history(st.session_state.messages)
            if file_path:
                st.sidebar.success(f"채팅이 저장되었습니다!")
    
    # 저장된 채팅 불러오기
    st.sidebar.markdown("#### 저장된 채팅")
    histories = list_chat_histories()
    if histories:
        selected_history = st.sidebar.selectbox(
            "저장된 채팅 선택:",
            options=histories,
            format_func=lambda x: f"{x['filename']} ({x['message_count']}개의 메시지)"
        )
        
        col1, col2, col3 = st.sidebar.columns(3)
        with col1:
            if st.button("불러오기"):
                messages = load_chat_history(selected_history['file_path'])
                if messages:
                    st.session_state.messages = messages
                    st.rerun()
        with col2:
            if st.button("삭제"):
                try:
                    os.remove(selected_history['file_path'])
                    st.success("채팅이 삭제되었습니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"삭제 중 오류 발생: {str(e)}")
        with col3:
            # JSON 파일 다운로드 버튼
            try:
                with open(selected_history['file_path'], 'r', encoding='utf-8') as f:
                    json_data = f.read()
                    
                st.download_button(
                    label="다운로드",
                    data=json_data,
                    file_name=selected_history['filename'],
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"파일 읽기 오류: {str(e)}")
    else:
        st.sidebar.info("저장된 채팅이 없습니다.")
    
    # 현재 채팅 내보내기 (JSON 다운로드)
    if st.session_state.messages:
        st.sidebar.markdown("#### 현재 채팅 내보내기")
        current_chat_json = json.dumps({
            "messages": st.session_state.messages,
            "exported_at": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
        
        st.sidebar.download_button(
            label="현재 채팅 다운로드",
            data=current_chat_json,
            file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # 채팅 초기화 버튼
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ 채팅 초기화"):
        st.session_state.messages = []
        st.rerun()

else:
    st.sidebar.warning("Please set at least one API key to use the models.")