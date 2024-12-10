import os
import streamlit as st
import dotenv
from datetime import datetime
import json
from typing import List, Dict

# Load environment variables from .env file
dotenv.load_dotenv()

def get_api_key(provider: str, env_var: str) -> str:
    # 1. Try to get the API key from st.secrets
    if "secrets.toml" in os.listdir(os.path.expanduser("~/.streamlit")):
        api_key = st.secrets.get(env_var)
    else:
        api_key = None

    # 2. If not found, try to get it from environment variables
    if not api_key:
        api_key = os.getenv(env_var)
    
    # 3. If still not found, prompt the user for input
    if not api_key:
        api_key = st.text_input(f"Enter your {provider} API Key (optional):", type="password", key=f"{provider}_key")
        if api_key:
            os.environ[env_var] = api_key  # Save to environment variable for future use

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

def get_completion_params(selected_model, selected_provider, api_keys, temperature, max_tokens, top_p, use_streaming, use_json_format, system_prompt, user_message):
    completion_params = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
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

def load_prompts() -> List[Dict]:
    try:
        with open("prompts.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_prompt(name: str, content: str, description: str = "") -> None:
    prompts = load_prompts()
    prompt = {
        "name": name,
        "content": content,
        "description": description,
        "created_at": datetime.now().isoformat()
    }
    prompts.append(prompt)
    with open("prompts.json", "w", encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)

def delete_prompt(index: int) -> None:
    prompts = load_prompts()
    if 0 <= index < len(prompts):
        prompts.pop(index)
        with open("prompts.json", "w", encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)

def load_system_prompts() -> List[Dict]:
    """시스템 프롬프트 마크다운 파일들을 로드합니다."""
    prompts = []
    system_prompts_dir = "system_prompts"
    
    # system_prompts 디렉토리가 없으면 생성
    if not os.path.exists(system_prompts_dir):
        os.makedirs(system_prompts_dir)
    
    # .md 파일들을 찾아서 로드
    for filename in os.listdir(system_prompts_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(system_prompts_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 파일명에서 확장자를 제거하여 이름으로 사용
                name = os.path.splitext(filename)[0]
                
                # 파일의 수정 시간을 생성일로 사용
                created_at = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                
                # frontmatter에서 설명 추출
                description = ""
                if content.startswith('---'):
                    try:
                        _, frontmatter, content = content.split('---', 2)
                        for line in frontmatter.strip().split('\n'):
                            if line.startswith('description:'):
                                description = line.replace('description:', '').strip()
                    except:
                        pass
                
                prompts.append({
                    "name": name,
                    "content": content.strip(),
                    "description": description,
                    "created_at": created_at,
                    "file_path": file_path
                })
            except Exception as e:
                st.error(f"Error loading {filename}: {str(e)}")
    
    return prompts

def save_system_prompt(name: str, content: str, description: str = "") -> bool:
    """시스템 프롬프트를 마크다운 파일로 저장합니다."""
    system_prompts_dir = "system_prompts"
    
    # system_prompts 디렉토리가 없으면 생성
    if not os.path.exists(system_prompts_dir):
        os.makedirs(system_prompts_dir)
    
    # 특수문자 제거하고 공백을 언더스코어로 변경하여 파일명 생성
    safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in name)
    file_path = os.path.join(system_prompts_dir, f"{safe_name}.md")
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            if description:
                f.write(f"---\ndescription: {description}\n---\n\n")
            f.write(content)
        return True
    except Exception as e:
        st.error(f"Error saving prompt: {str(e)}")
        return False

def delete_system_prompt(file_path: str) -> bool:
    """시스템 프롬프트 마크다운 파일을 삭제합니다."""
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        st.error(f"Error deleting prompt: {str(e)}")
        return False 

def save_chat_history(messages: List[Dict], filename: str = None) -> str:
    """채팅 히스토리를 JSON 파일로 저장합니다."""
    chat_history_dir = "chat_history"
    
    # 디렉토리가 없으면 생성
    if not os.path.exists(chat_history_dir):
        os.makedirs(chat_history_dir)
    
    # 파일명이 지정되지 않은 경우 현재 시간으로 생성
    if not filename:
        filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    file_path = os.path.join(chat_history_dir, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "messages": messages,
                "saved_at": datetime.now().isoformat(),
            }, f, ensure_ascii=False, indent=2)
        return file_path
    except Exception as e:
        st.error(f"채팅 저장 중 오류 발생: {str(e)}")
        return None

def load_chat_history(file_path: str) -> List[Dict]:
    """저장된 채팅 히스토리를 불러옵니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("messages", [])
    except Exception as e:
        st.error(f"채팅 불러오기 중 오류 발생: {str(e)}")
        return []

def list_chat_histories() -> List[Dict]:
    """저장된 채팅 히스토리 목록을 반환합니다."""
    chat_history_dir = "chat_history"
    histories = []
    
    if not os.path.exists(chat_history_dir):
        return histories
    
    for filename in os.listdir(chat_history_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(chat_history_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    histories.append({
                        "filename": filename,
                        "file_path": file_path,
                        "saved_at": data.get("saved_at", "Unknown"),
                        "message_count": len(data.get("messages", []))
                    })
            except:
                continue
    
    return sorted(histories, key=lambda x: x["saved_at"], reverse=True) 
  