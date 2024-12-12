import streamlit as st
from utils import load_system_prompts, get_available_models, save_system_prompt
import json
from datetime import datetime
from litellm import completion

st.title("🧪 시스템 프롬프트 테스트")

# 시스템 프롬프트 로드
system_prompts = load_system_prompts()

# 사이드바에서 시스템 프롬프트 선택
st.sidebar.header("시스템 프롬프트 선택")
if not system_prompts:
    st.sidebar.warning("저장된 시스템 프롬프트가 없습니다. 먼저 시스템 프롬프트를 추가하세요.")
else:
    prompt_names = [p['name'] for p in system_prompts]
    selected_prompt_name = st.sidebar.selectbox("테스트할 시스템 프롬프트 선택:", prompt_names)

    # 선택된 시스템 프롬프트 내용 가져오기
    selected_prompt_content = next(p['content'] for p in system_prompts if p['name'] == selected_prompt_name)

    # 시스템 프롬프트에 포함된 변수 추출
    variables = {}
    variable_names = [var.strip('{}') for var in selected_prompt_content.split() if '{' in var and '}' in var]

    # 변수 입력 필드 생성
    for var in variable_names:
        variables[var] = st.sidebar.text_input(f"{var} 값을 입력하세요:", "")

# 사이드바에서 모델 선택 및 파라미터 설정
st.sidebar.header("모델 및 파라미터 설정")
model = st.sidebar.selectbox("모델 선택:", get_available_models())
temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
max_tokens = st.sidebar.number_input("최대 토큰 수:", min_value=1, max_value=4096, value=150, step=1)
top_p = st.sidebar.slider("Top P:", min_value=0.0, max_value=1.0, value=1.0, step=0.1)

# JSON 형식으로 응답 받기 옵션
use_json_format = st.sidebar.checkbox("JSON 형식으로 응답 받기", value=False)

# 채팅 히스토리 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.total_round = 0  # 총 라운드 수 초기화

# 사용자 입력
user_input = st.text_input("메시지를 입력하세요...", "")

# AI 응답 버튼
if st.button("AI 응답 받기"):
    if user_input:
        # 시스템 프롬프트에 변수 대체
        prompt_with_variables = selected_prompt_content
        for var, value in variables.items():
            prompt_with_variables = prompt_with_variables.replace(f"{{{var}}}", value)

        # AI와의 대화 구성
        messages = [
            {"role": "system", "content": prompt_with_variables}
        ] + st.session_state.chat_history + [{"role": "user", "content": user_input}]

        # AI 응답 요청
        with st.spinner("AI 응답을 기다리는 중..."):
            response = completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=False
            )

        # AI 응답 표시
        ai_response = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

        # 총 라운드 수 증가
        st.session_state.total_round += 1

        # 사용자 입력 및 AI 응답 표시
        st.chat_message("user").markdown(user_input)
        st.chat_message("assistant").markdown(ai_response)

        # 사용자 입력 필드 초기화
        st.rerun()  # 페이지 새로 고침

    else:
        st.error("사용자 입력을 입력하세요.")

# 채팅 히스토리 표시 (최신 메시지가 아래에 오도록)
for chat in reversed(st.session_state.chat_history):
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# 사이드바에 채팅 히스토리 다운로드 버튼 추가
with st.sidebar:
    st.markdown("### 채팅 히스토리 다운로드")
    if st.button("채팅 히스토리 다운로��� (JSON)"):
        chat_history_json = json.dumps(st.session_state.chat_history, ensure_ascii=False, indent=2)
        st.download_button(
            label="채팅 히스토리 다운로드",
            data=chat_history_json,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# 채팅 초기화 버튼
if st.sidebar.button("🗑️ 채팅 초기화"):
    st.session_state.chat_history = []
    st.session_state.total_round = 0  # 총 라운드 수 초기화
    st.session_state.clear()  # 세션 상태 초기화
    st.rerun()  # 페이지 새로 고침

# 새로운 섹션: 시스템 프롬프트 자동 테스트 및 평가
st.sidebar.header("🔍 시스템 프롬프트 자동 테스트")

# 테스트 케이스 입력 필드
test_cases = st.sidebar.text_area("테스트 케이스 입력 (각 줄에 하나씩):", 
                                   "간단한 질문\n복잡한 문제 해결\n창의적인 작업")

# 평가 기준 선택
evaluation_criteria = st.sidebar.multiselect(
    "평가 기준 선택:", 
    [
        "정확성", 
        "일관성", 
        "창의성", 
        "응답 길이", 
        "문법 정확성"
    ]
)

# 자동 테스트 버튼
if st.sidebar.button("🚀 시스템 프롬프트 자동 테스트"):
    if not test_cases or not evaluation_criteria:
        st.sidebar.error("테스트 케이스와 평가 기준을 선택해주세요.")
    else:
        # 테스트 결과 저장할 딕셔너리
        test_results = {
            "prompt_name": selected_prompt_name,
            "prompt_content": selected_prompt_content,
            "test_date": datetime.now().isoformat(),
            "test_cases": []
        }

        # 각 테스트 케이스에 대해 테스트 수행
        for case in test_cases.split('\n'):
            if not case.strip():
                continue

            # AI 응답 요청
            messages = [
                {"role": "system", "content": selected_prompt_content},
                {"role": "user", "content": case}
            ]

            response = completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=False
            )

            ai_response = response.choices[0].message.content

            # 테스트 케이스별 평가
            case_evaluation = {
                "input": case,
                "output": ai_response,
                "evaluations": {}
            }

            # 선택된 평가 기준에 따라 평가 (실제 평가는 더 정교한 로직 필요)
            for criterion in evaluation_criteria:
                if criterion == "정확성":
                    case_evaluation["evaluations"]["정확성"] = "보통"  # 임시 평가
                elif criterion == "일관성":
                    case_evaluation["evaluations"]["일관성"] = "높음"  # 임시 평가
                # 다른 평가 기준 추가 가능

            test_results["test_cases"].append(case_evaluation)

        # 테스트 결과 표시
        st.sidebar.success("테스트 완료!")
        st.sidebar.json(test_results)

        # 테스트 결과 다운로드 버튼
        test_results_json = json.dumps(test_results, ensure_ascii=False, indent=2)
        st.sidebar.download_button(
            label="테스트 결과 다운로드",
            data=test_results_json,
            file_name=f"system_prompt_test_{selected_prompt_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

        # 선택적: 평가 결과에 따라 시스템 프롬프트 자동 개선
        if st.sidebar.checkbox("테스트 결과에 따라 프롬프트 자동 개선"):
            # 여기에 프롬프트 개선 로직 추가 
            # 예: OpenAI의 프롬프트 엔지니어링 API 또는 자체 개선 알고리즘
            st.sidebar.info("프롬프트 자동 개선 기능은 아직 구현되지 않았습니다.")
    