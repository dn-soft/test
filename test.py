import dotenv
import os
import streamlit as st

# Load environment variables
dotenv.load_dotenv()

# Get API key from environment variables or Streamlit input
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

if api_key:
    st.success("API Key is set!")
else:
    st.warning("Please enter your OpenAI API Key to continue")
