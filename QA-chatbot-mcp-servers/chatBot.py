import streamlit as st
import google.generativeai as genai
# from dotenv import load_dotenv
import os

st.set_page_config(page_title="Simple Chat Bot")

st.markdown("# Simple Chat Bot page 🗨️")
st.sidebar.markdown("# Chat Bot page 🗨️")

# Load environment variables from .env file
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("AIzaSyDMeSwgaPXIYrgqpli2VXMzcoxYyWUZotU")

# if not GOOGLE_API_KEY:
#     st.error("Please set GEMINI_API_KEY in a .env file to use the chatbot.")
#     st.stop()

# Configure Google Generative AI
genai.configure(api_key="AIzaSyDMeSwgaPXIYrgqpli2VXMzcoxYyWUZotU")

# Initialize gemini-2.0-flash-001 model and chat session
_model = genai.GenerativeModel("gemini-2.0-flash-001")
_chat = _model.start_chat(history=[])

def get_gemini_response(query: str):
    """Send the user query to gemini-2.0-flash-001 and stream back the response chunks."""
    return _chat.send_message(query, stream=True)

st.header("A simple Chat Bot")

# Initialize session state for chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Single-line text input widget
input_text = st.text_input("Input:", key="input")
submit_button = st.button("Get Instant answers")

if submit_button and input_text:
    # Call Gemini and stream response
    response_chunks = get_gemini_response(input_text)

    # Add user query to chat history
    st.session_state["chat_history"].append(("You", input_text))

    st.subheader("The Response is")
    for chunk in response_chunks:
        st.write(chunk.text)
        st.session_state["chat_history"].append(("Bot", chunk.text))

st.subheader("The Chat History is")
for role, text in st.session_state["chat_history"]:
    st.write(f"{role}: {text}")