import streamlit as st
from utils import *

st.set_page_config(
    page_title="AI Chat App",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Welcome to AI Chat App")
st.markdown("""
### 시작하기
1. 왼쪽 사이드바의 Settings 페이지에서 API 키를 설정하세요
2. Chat 페이지에서 대화를 시작하세요

### 기능
- 다중 AI 제공자 지원 (OpenAI, Anthropic, Azure)
- 실시간 스트리밍 응답
- JSON 형식 응답 지원
- 설정 저장 및 관리
""")

# Show current API key status
st.header("🔑 Current API Status")
api_keys = {}
for provider, env_var in providers.items():
    api_key = get_api_key(provider, env_var)
    api_keys[provider] = api_key
    if api_key:
        st.success(f"✅ {provider} is configured")
    else:
        st.warning(f"⚠️ {provider} needs configuration") 
