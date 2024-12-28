import os
import json
import streamlit as st
import time
from groq import Groq

st.set_page_config(
    page_title="Dynamic Character Chatbot",
    page_icon="🤖",
    layout="centered"
)


# groq api

working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/api.json"))

GROQ_API_KEY = config_data.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("API key is missing in the config.json file.")
    st.stop()

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

try:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Failed to initialize Groq client: {e}")
    st.stop()




# Initialize 

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False



# title

st.title("🤖 Dynamic Character Chatbot")



# Sidebar 

st.sidebar.title("Customize Your Chatbot")
character_name = st.sidebar.text_input("Name", "Harsvardhan")
character_gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Neutral"])
character_expertise = st.sidebar.selectbox(
    "Expertise", ["Education", "Healthcare", "Gaming", "Finance"]
)
character_tone = st.sidebar.selectbox(
    "Narrative Design", ["Friendly", "Formal", "Humorous", "Empathetic"]
)



# button

if st.sidebar.button("Start Chatbot"):
    st.session_state.chat_started = True
    st.session_state.chat_history = [] 

    #  prompt with user inputs
    prompt = (
        f"Write a short and crisp opening message for a chatbot named {character_name}. "
        f"The chatbot uses {'he/him' if character_gender == 'Male' else 'she/her' if character_gender == 'Female' else 'they/them'} pronouns. "
        f"The chatbot is an expert in {character_expertise.lower()} and has a {character_tone.lower()} personality. "
        f"Keep it engaging and friendly."
    )

    # LLM 
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=50,
        )
        opening_message = response.choices[0].message.content.strip()
        st.session_state.chat_history.append({"role": "assistant", "content": opening_message})

    except Exception as e:
        st.error(f"Failed to generate the opening message: {e}")




# display the chat
if st.session_state.chat_started:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # input
    user_prompt = st.chat_input("Ask me anything...")

    if user_prompt:
        st.chat_message("user").markdown(user_prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})


        # Generating answer...
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Generating answer...") 
            time.sleep(2) 


        # dynamic character
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a chatbot named {character_name}. "
                    f"You use {character_gender.lower()} pronouns. "
                    f"You are an expert in {character_expertise.lower()} and have a "
                    f"{character_tone.lower()} personality. Be consistent with these attributes. "
                    "Provide short and concise answers, sticking to the point without elaborating unnecessarily."
                ),
            },
            *st.session_state.chat_history,
        ]

        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                max_tokens=100,
            )

            assistant_response = response.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

            placeholder.markdown(assistant_response)

        except Exception as e:
            placeholder.markdown("")
            st.error(f"Error while fetching the response from GROQ: {e}")
else:
    st.info("Customize your chatbot in the sidebar and click 'Start Chatbot' to begin!")
