# streamlit_app.py
# Neon-Gradient Tweet Generator (entire UI wrapped in the requested gradient)
# Run:  streamlit run streamlit_app.py

import streamlit as st
import time
import os

# ---------- BACKEND ----------
os.environ['GOOGLE_API_KEY'] = ""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import PromptTemplate

gemini_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")

tweet_temp = "Give me {number} tweets on the topic {name} in {language}"
tweet_prompt = PromptTemplate(
    template=tweet_temp,
    input_variables=["number", "name", "language"]
)
tweet_chain = tweet_prompt | gemini_model

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Gradient Tweet Generator",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- GLOBAL GRADIENT CSS ----------
st.markdown(
    """
    <style>
    /* 1.  whole page gradient */
    .stApp {
        background: linear-gradient(90deg, #ff6f61, #ffb88c, #6b7280, #60a5fa);
        background-attachment: fixed;
        color: #ffffff;
    }

    /* 2.  make inputs & selects semi-transparent dark so gradient shows through */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: rgba(0,0,0,0.35);
        color: #ffffff;
        caret-color: #ffffff;
        border: 1px solid rgba(255,255,255,0.45);
        border-radius: 8px;
        padding: 10px;
        font-size: 1.1rem;
    }

    /* 3.  neon-white button with gradient glow */
    div.stButton > button {
        background: rgba(255,255,255,0.15);
        color: #ffffff;
        border: 2px solid rgba(255,255,255,0.7);
        padding: 0.6rem 2.5rem;
        border-radius: 8px;
        font-weight: bold;
        letter-spacing: 1px;
        transition: all 0.25s ease-in-out;
    }
    div.stButton > button:hover {
        background: rgba(255,255,255,0.3);
        box-shadow: 0 0 20px rgba(255,255,255,0.6);
    }

    /* 4.  tweet cards – frosted glass */
    .tweet-card {
        background: rgba(255,255,255,0.18);
        backdrop-filter: blur(6px);
        border-left: 4px solid rgba(255,255,255,0.8);
        padding: 15px 20px;
        margin: 15px 0;
        border-radius: 8px;
        font-size: 1.15rem;
        color: #ffffff;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }

    /* 5.  title */
    h1 {
        color: #ffffff;
        text-shadow: 0 0 8px rgba(255,255,255,0.6);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- UI ----------
st.markdown("<h1 style='text-align:center;'>⚡ Gradient Tweet Generator ⚡</h1>", unsafe_allow_html=True)
st.markdown("---")

with st.form("generator"):
    topic = st.text_input("Topic name", placeholder="e.g. Quantum Computing")
    num = st.number_input("No. of tweets", min_value=1, max_value=20, value=5, step=1)
    lang = st.selectbox("Language", ["English", "Spanish", "French", "Hindi", "German"])
    submitted = st.form_submit_button("Generate")

if submitted and topic.strip():
    with st.spinner("Gemini is crafting your tweets…"):
        try:
            response = tweet_chain.invoke({
                "number": int(num),
                "name": topic.strip(),
                "language": lang
            })
            tweets = response.content.strip().split("\n")
            tweets = [t for t in tweets if t]
        except Exception as e:
            st.error(f"Gemini error: {e}")
            st.stop()

    st.markdown("---")
    st.markdown("#### Generated Tweets")
    for tw in tweets:
        st.markdown(f'<div class="tweet-card">{tw}</div>', unsafe_allow_html=True)

elif submitted:
    st.warning("Please enter a topic first.")
