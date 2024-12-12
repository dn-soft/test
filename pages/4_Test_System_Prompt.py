import streamlit as st
from utils import load_system_prompts, get_available_models
import json
from datetime import datetime
from litellm import completion
import random

st.title("🧪 시스템 프롬프트 턴 기반 테스트")

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

    # 테스트 입력 필드
    test_inputs = st.sidebar.text_area("테스트 입력 (쉼표로 구분):", 
        "게임 시작해줘, 2/4, 힌트 줘, 다음 문제 알려줘")

    # 턴 수 입력
    max_turns = st.sidebar.number_input("최대 턴 수:", min_value=1, max_value=10, value=5)

    # 모델 선택
    model = st.sidebar.selectbox("테스트할 모델:", get_available_models())

    # 턴 기반 테스트 버튼
    if st.sidebar.button("🚀 턴 기반 테스트 시작"):
        if not all(variables.values()):
            st.sidebar.error("모든 변수를 입력해주세요.")
        else:
            # 전체 테스트 결과 저장
            total_test_results = {
                "max_turns": max_turns,
                "test_date": datetime.now().isoformat(),
                "turns": []
            }

            # 테스트 입력 준비
            test_input_list = [input.strip() for input in test_inputs.split(',') if input.strip()]

            # 시스템 프롬프트에 변수 대체
            prompt_with_variables = selected_prompt_content
            for var, value in variables.items():
                prompt_with_variables = prompt_with_variables.replace(f"{{{var}}}", value)

            # 대화 메시지 초기화
            messages = [
                {"role": "system", "content": prompt_with_variables}
            ]

            # 턴 기반 테스트 수행
            for turn in range(max_turns):
                # 랜덤하게 사용자 입력 선택
                user_input = test_input_list[turn % len(test_input_list)]

                # 메시지에 사용자 입력 추가
                messages.append({"role": "user", "content": user_input})

                # AI 응답 요청
                with st.spinner(f"{turn + 1}/{max_turns} 턴 진행 중..."):
                    try:
                        response = completion(
                            model=model,
                            messages=messages,
                            temperature=0.7,
                            max_tokens=300,
                            top_p=1.0,
                            stream=False
                        )

                        # AI 응답 표시
                        ai_response = response.choices[0].message.content

                        # 메시지에 AI 응답 추가
                        messages.append({"role": "assistant", "content": ai_response})

                        # 턴 결과 저장
                        turn_result = {
                            "turn": turn + 1,
                            "user_input": user_input,
                            "ai_response": ai_response
                        }

                        # JSON 응답 추출 시도
                        try:
                            json_start = ai_response.find('{')
                            json_end = ai_response.rfind('}') + 1
                            if json_start != -1 and json_end != -1:
                                json_str = ai_response[json_start:json_end]
                                turn_result['parsed_json'] = json.loads(json_str)
                        except (json.JSONDecodeError, ValueError):
                            pass

                        total_test_results["turns"].append(turn_result)

                    except Exception as e:
                        st.sidebar.error(f"{turn + 1} 턴 중 오류 발생: {str(e)}")
                        turn_result = {
                            "turn": turn + 1,
                            "error": str(e)
                        }
                        total_test_results["turns"].append(turn_result)

                # 게임 종료 조건 확인 (JSON 응답의 is_end 확인)
                if turn_result.get('parsed_json', {}).get('is_end', False):
                    break

            # 테스트 결과 표시
            st.sidebar.success("턴 기반 테스트 완료!")
            st.sidebar.json(total_test_results)

            # 테스트 결과 다운로드 버튼
            test_results_json = json.dumps(total_test_results, ensure_ascii=False, indent=2)
            st.sidebar.download_button(
                label="테스트 결과 다운로드",
                data=test_results_json,
                file_name=f"turn_based_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            