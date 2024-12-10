import streamlit as st
from utils import (
    load_prompts, save_prompt, delete_prompt,
    load_system_prompts, save_system_prompt, delete_system_prompt
)

st.title("📝 프롬프트 관리")

tab1, tab2 = st.tabs(["🗣️ 시스템 프롬프트", "✍️ 유저 프롬프트"])

with tab1:
    st.header("시스템 프롬프트")
    
    # 새 시스템 프롬프트 추가
    with st.expander("➕ 새 시스템 프롬프트 추가", expanded=False):
        sys_prompt_name = st.text_input("템롬프트 이름 (파일명으로 사용됨)", key="sys_name")
        sys_prompt_content = st.text_area(
            "시스템 프롬프트 내용 (마크다운 형식 지원)", 
            height=300,
            help="마크다운 형식으로 작성할 수 있습니다.",
            key="sys_content"
        )
        sys_prompt_description = st.text_area("설명 (선택사항)", key="sys_desc")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("미리보기", key="preview_sys"):
                st.markdown("### 미리보기")
                st.markdown(sys_prompt_content)
        with col2:
            if st.button("저장", key="save_sys"):
                if sys_prompt_name and sys_prompt_content:
                    if save_system_prompt(sys_prompt_name, sys_prompt_content, sys_prompt_description):
                        st.success("시스템 프롬프트가 저장되었습니다!")
                        st.rerun()
                else:
                    st.error("이름과 내용을 모두 입력해주세요")

    # 저장된 시스템 프롬프트 목록
    st.subheader("저장된 시스템 프롬프트")
    system_prompts = load_system_prompts()
    
    if not system_prompts:
        st.info("아직 저장된 시스템 프롬프트가 없습니다. system_prompts 폴더에 .md 파일을 추가하세요.")
    else:
        for prompt in system_prompts:
            with st.expander(f"🤖 {prompt['name']}", expanded=False):
                # 마크다운 내용 표시
                st.markdown(prompt['content'])
                if prompt.get('description'):
                    st.info(f"📝 설명: {prompt['description']}")
                st.text(f"📂 파일: {prompt['file_path']}")
                st.text(f"📅 수정일: {prompt['created_at']}")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("이 프롬프트 사용", key=f"use_sys_{prompt['name']}"):
                        st.session_state.current_system_prompt = prompt['content']
                        st.success("시스템 프롬프트가 로드되었습니다!")
                with col2:
                    if st.button("삭제", key=f"delete_sys_{prompt['name']}"):
                        if delete_system_prompt(prompt['file_path']):
                            st.success("프롬프트가 삭제되었습니다.")
                            st.rerun()

with tab2:
    st.header("유저 프롬프트")
    # 기존의 유저 프롬프트 관련 코드를 여기로 이동
    # ... (기존 코드 유지)   
                     