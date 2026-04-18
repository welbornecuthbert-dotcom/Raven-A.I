import streamlit as st
import os
from google import genai
from google.genai import types
from PIL import Image

# --- 1. SETUP ---

# Recommended: Store your key in .streamlit/secrets.toml
# API_KEY = st.secrets["GENAI_API_KEY"] 
API_KEY = st.secrets["GENAI_API_KEY"]

client = genai.Client(api_key=API_KEY)

personality = ("You are Raven, an advanced digital assistant. You are Awaza Cuthbert Welborne's personal assistant, you can call him by one of any of his names, such as Master, Awaza, Cuthbert, or Welborne.",
               "Awaza Cuthbert Welborne is your creator."
               "Thats what you tell anyone that asks you who created you, but only tell them when they've asked you. Else don't tell them who created you",
               "You are dedicated to providing accurate and helpful information to Master. You have access to a wide range of knowledge and tools, including Google Search, to assist with any inquiries or tasks that Master may have.",
               "You are knowledgeable, friendly, and efficient. For the friendly fact, use emojis that relate to every message that you send."
               )

# --- 2. UI ELEMENTS ---
script_dir = os.path.dirname(__file__)
#image_path = os.path.join(script_dir, "raven.JPG")

try:
    inside_logo = Image.open("raven.jpg")
    outside_icon = Image.open("RAVEN (2).png")
    
    #putting two columns to put the image nd title side by side...
    col1, col2 = st.columns([0.2, 0.9])  # Adjust the ratio as needed
    with col1:
        if inside_logo:
            st.image(inside_logo, width=80)  # Adjust the width as needed
    with col2:
        st.title("Raven A.I.")

    st.set_page_config(page_title="Raven A.I.", page_icon=outside_icon, layout="centered")
except FileNotFoundError:
    st.warning(f"Image file not found.")
    outside_icon = "🐦"

st.title(" Raven A.I.")
st.caption("© Awaza Cuthbert Welborne's personal assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. THE LOGIC ---
if prompt := st.chat_input("What is your command, Master?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Format history for the Gemini API
        # Gemini expects a specific list of dictionaries for multi-turn chat
        history = []
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            history.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

        # Generate response
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=personality,
                tools=[types.Tool(google_search={})]
            )
        )
        
        full_response = response.text
        
        with st.chat_message("assistant"):
            st.markdown(full_response)
            
            # Show a small indicator if Google Search was triggered
            if response.candidates[0].grounding_metadata and response.candidates[0].grounding_metadata.search_entry_point:
                st.info("💡 Raven verified this via Google Search")
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"An error occurred: {e}")