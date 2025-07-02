import streamlit as st
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

st.set_page_config(page_title="Simple Search Chat Bot")

st.markdown("# Simple Google-Search Chat Bot 🔎")
st.sidebar.markdown("# Chat Bot page 🔎")

# Load environment variables from .env file
load_dotenv()
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_API_KEY")  
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_CLIENT_ID")

if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_CX:
    st.error("Please set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_CX in a .env file to use the chatbot.")
    st.stop()

# Build the Google Custom Search service
_search_service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)

def get_google_results(query: str, *, num_results: int = 5):
    """Return a list of search-result dicts for the query."""
    try:
        response = _search_service.cse().list(q=query, cx=GOOGLE_SEARCH_CX, num=num_results).execute()
        return response.get("items", [])
    except Exception as exc:
        st.error(f"Error while querying Google Search API: {exc}")
        return []

st.header("Ask me anything – I'll search Google for you")

# Initialize session state for chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

input_text = st.text_input("Input:", key="input")
submit_button = st.button("Search on Google")

if submit_button and input_text:
    results = get_google_results(input_text)

    # Store the user query
    st.session_state["chat_history"].append(("You", input_text))

    st.subheader("Top Results")
    if not results:
        st.info("No results found.")
    for idx, item in enumerate(results, start=1):
        title = item.get("title")
        link = item.get("link")
        snippet = item.get("snippet")
        st.markdown(f"**{idx}. [{title}]({link})**\n\n{snippet}")
        st.session_state["chat_history"].append(("Result", f"{title} – {link}"))

st.subheader("Chat History")
for role, text in st.session_state["chat_history"]:
    st.write(f"{role}: {text}")