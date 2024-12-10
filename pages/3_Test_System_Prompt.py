import streamlit as st
from utils import load_system_prompts
from litellm import completion

st.title("🧪 시스템 프롬프트 테스트")

# 시스템 프롬프트 로드
system_prompts = load_system_prompts()

if not system_prompts:
    st.warning("저장된 시스템 프롬프트가 없습니다. 먼저 시스템 프롬프트를 추가하세요.")
else:
    # 시스템 프롬프트 선택
    prompt_names = [p['name'] for p in system_prompts]
    selected_prompt_name = st.selectbox("테스트할 시스템 프롬프트 선택:", prompt_names)

    # 선택된 시스템 프롬프트 내용 가져오기
    selected_prompt_content = next(p['content'] for p in system_prompts if p['name'] == selected_prompt_name)

    # 사용자 입력
    user_input = st.text_area("사용자 입력:", height=150)

    # AI 응답 버튼
    if st.button("AI 응답 받기"):
        if user_input:
            # AI와의 대화 구성
            messages = [
                {"role": "system", "content": selected_prompt_content},
                {"role": "user", "content": user_input}
            ]

            # AI 응답 요청
            with st.spinner("AI 응답을 기다리는 중..."):
                response = completion(
                    model="gpt-3.5-turbo",  # 사용할 모델을 지정하세요
                    messages=messages,
                    temperature=0.7,
                    max_tokens=150,
                    top_p=1.0,
                    stream=False
                )

            # AI 응답 표시
            st.markdown("### AI 응답")
            st.write(response.choices[0].message.content)
        else:
            st.error("사용자 입력을 입력하세요.") 
            