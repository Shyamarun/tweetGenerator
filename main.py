# streamlit_app.py
# Tweet-Generator UI – Neon-Blue / Dark theme  (with Gemini backend)
# Run:  streamlit run streamlit_app.py

import streamlit as st
from datetime import datetime
import time
import os

# ---------- BACKEND ----------
# 1.  Set API key (will be empty string as requested)
os.environ['GOOGLE_API_KEY'] = ""

# 2.  Build LangChain objects
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
    page_title="Neon Tweet Generator",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- NEON CSS ----------
st.markdown(
    """
    <style>
    /* global dark background */
    .stApp {
        background: #0e0e0e;
        color: #ffffff;
    }

    /* inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: #1a1a1a;
        color: #00e5ff;
        caret-color: #00e5ff;
        border: 1px solid #00e5ff;
        border-radius: 8px;
        padding: 10px;
        font-size: 1.1rem;
    }

    /* button neon */
    div.stButton > button {
        background: transparent;
        color: #00e5ff;
        border: 2px solid #00e5ff;
        padding: 0.6rem 2.5rem;
        border-radius: 8px;
        font-weight: bold;
        letter-spacing: 1px;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background: #00e5ff;
        color: #0e0e0e;
        box-shadow: 0 0 15px #00e5ff;
    }

    /* tweet cards */
    .tweet-card {
        background: #161616;
        border-left: 4px solid #00e5ff;
        padding: 15px 20px;
        margin: 15px 0;
        border-radius: 6px;
        font-size: 1.1rem;
        color: #ffffff;
        box-shadow: 0 0 10px rgba(0,229,255,0.25);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- UI ----------
st.markdown("<h1 style='text-align:center;color:#00e5ff;'>⚡ Neon Tweet Generator ⚡</h1>", unsafe_allow_html=True)
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
            tweets = [t for t in tweets if t]  # remove empty lines
        except Exception as e:
            st.error(f"Gemini error: {e}")
            st.stop()

    st.markdown("---")
    st.markdown(f"<h3 style='color:#00e5ff;'>Generated Tweets</h3>", unsafe_allow_html=True)
    for tw in tweets:
        st.markdown(f'<div class="tweet-card">{tw}</div>', unsafe_allow_html=True)

elif submitted:
    st.warning("Please enter a topic first.")
