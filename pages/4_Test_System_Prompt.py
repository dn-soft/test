import streamlit as st
from typing import List, Dict
from litellm import completion
from datetime import datetime
import json

class LLMAgent:
    def __init__(self, name: str, system_prompt: str, model: str):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.memory: List[Dict] = []
        self.initialize_memory()
    
    def initialize_memory(self):
        """Initialize the conversation memory with system prompt"""
        self.memory = [{"role": "system", "content": self.system_prompt}]
    
    def update_memory(self, role: str, content: str):
        """Add new message to memory"""
        self.memory.append({"role": role, "content": content})
        
    def get_response(self, max_tokens: int = 300) -> str:
        """Generate response using the model and current memory"""
        try:
            response = completion(
                model=self.model,
                messages=self.memory,
                temperature=0.7,
                max_tokens=max_tokens,
                top_p=1.0,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

class LLMDialogue:
    def __init__(self, agent1: LLMAgent, agent2: LLMAgent):
        self.agent1 = agent1
        self.agent2 = agent2
        self.conversation_history: List[Dict] = []
        
    def conduct_dialogue(self, initial_message: str, max_turns: int = 5) -> List[Dict]:
        """Conduct a dialogue between the two agents"""
        current_speaker = self.agent1
        current_listener = self.agent2
        
        # Start with initial message
        self.agent1.update_memory("user", initial_message)
        self.conversation_history.append({
            "turn": 0,
            "speaker": "user",
            "message": initial_message
        })
        
        for turn in range(max_turns):
            # Get response from current speaker
            response = current_speaker.get_response()
            
            # Update conversation history
            self.conversation_history.append({
                "turn": turn + 1,
                "speaker": current_speaker.name,
                "message": response
            })
            
            # Update both agents' memories
            current_speaker.update_memory("assistant", response)
            current_listener.update_memory("user", response)
            
            # Switch roles
            current_speaker, current_listener = current_listener, current_speaker
            
        return self.conversation_history

def main():
    st.title("🤖 LLM Dialogue System")
    
    # Sidebar configurations
    st.sidebar.header("Configuration")
    
    # Agent 1 configuration
    st.sidebar.subheader("Agent 1 Configuration")
    agent1_name = st.sidebar.text_input("Agent 1 Name", "Agent 1")
    agent1_prompt = st.sidebar.text_area("Agent 1 System Prompt", "You are a helpful assistant.")
    agent1_model = st.sidebar.selectbox("Agent 1 Model", ["gpt-3.5-turbo", "gpt-4"], key="model1")
    
    # Agent 2 configuration
    st.sidebar.subheader("Agent 2 Configuration")
    agent2_name = st.sidebar.text_input("Agent 2 Name", "Agent 2")
    agent2_prompt = st.sidebar.text_area("Agent 2 System Prompt", "You are a curious assistant.")
    agent2_model = st.sidebar.selectbox("Agent 2 Model", ["gpt-3.5-turbo", "gpt-4"], key="model2")
    
    # Dialogue configuration
    st.sidebar.subheader("Dialogue Configuration")
    initial_message = st.sidebar.text_area("Initial Message", "Hello! Let's start a conversation.")
    max_turns = st.sidebar.number_input("Maximum Turns", min_value=1, max_value=20, value=5)
    
    # Start dialogue button
    if st.sidebar.button("Start Dialogue"):
        # Initialize agents
        agent1 = LLMAgent(agent1_name, agent1_prompt, agent1_model)
        agent2 = LLMAgent(agent2_name, agent2_prompt, agent2_model)
        
        # Create dialogue system
        dialogue = LLMDialogue(agent1, agent2)
        
        # Conduct dialogue
        with st.spinner("Conducting dialogue..."):
            conversation = dialogue.conduct_dialogue(initial_message, max_turns)
            
        # Display conversation
        st.subheader("Conversation")
        for entry in conversation:
            with st.chat_message(entry["speaker"].lower()):
                st.write(entry["message"])
        
        # Export conversation
        conversation_json = json.dumps(conversation, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download Conversation",
            data=conversation_json,
            file_name=f"llm_dialogue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()
    