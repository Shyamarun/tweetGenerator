# streamlit_app.py
# Tweet-Generator UI with Gemini AI – Neon-Blue / Dark theme
# Run:  streamlit run streamlit_app.py

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from datetime import datetime
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Neon Tweet Generator",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- NEON CSS (FIXED UI BUGS) ----------
st.markdown(
    """
    <style>
    :root {
        --gradient: linear-gradient(90deg, #ff6f61, #ffb88c, #6b7280, #60a5fa);
        --gradient-bg: linear-gradient(135deg, #ff6f61, #ffb88c, #6b7280, #60a5fa);
    }
    
    /* Global background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%);
        color: #ffffff;
        position: relative;
    }
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background: var(--gradient);
        opacity: 0.03;
        pointer-events: none;
        z-index: -1;
    }
    
    /* Hide header/footer */
    header[data-testid="stHeader"], footer[data-testid="stFooter"] {
        display: none;
    }

    /* Safe top padding for content */
    section.main > div {
        padding-top: 2rem !important;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: rgba(26,26,26,0.9);
        color: #fff;
        caret-color: #ff6f61;
        border: 2px solid transparent;
        border-radius: 10px;
        padding: 12px 15px;
        font-size: 1.1rem;
    }
    .stTextInput > div > div,
    .stNumberInput > div > div {
        position: relative;
    }
    .stTextInput > div > div::before,
    .stNumberInput > div > div::before {
        content: '';
        position: absolute;
        inset: 0;
        padding: 2px;
        background: var(--gradient);
        border-radius: 10px;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        pointer-events: none;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        outline: none;
        box-shadow: 0 0 20px rgba(255,111,97,0.3);
    }

    /* Buttons */
    div.stButton > button {
        background: var(--gradient) !important;
        color: #fff !important;
        border: none !important;
        padding: 0.8rem 2.5rem !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        letter-spacing: 1px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(255,111,97,0.3) !important;
        transition: all 0.3s ease-in-out !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(255,111,97,0.5) !important;
        filter: brightness(1.1) !important;
    }

    /* Tweet cards */
    .tweet-card {
        background: linear-gradient(145deg, #1a1a1a, #252525);
        border-radius: 12px;
        padding: 20px 25px;
        margin: 20px 0;
        font-size: 1.1rem;
        color: #fff;
        position: relative;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    .tweet-card::before {
        content: '';
        position: absolute;
        inset: 0;
        padding: 2px;
        background: var(--gradient);
        border-radius: 12px;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        opacity: 0.6;
    }
    .tweet-card::after {
        content: "🐦";
        position: absolute;
        top: 15px;
        right: 20px;
        opacity: 0.3;
        font-size: 1.3rem;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Form */
    .stForm {
        background: linear-gradient(145deg, #1a1a1a, #252525);
        padding: 25px;
        border-radius: 15px;
        position: relative;
    }
    .stForm::before {
        content: '';
        position: absolute;
        inset: 0;
        padding: 2px;
        background: var(--gradient);
        border-radius: 15px;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        opacity: 0.4;
    }

    /* Labels */
    .stTextInput > label, .stNumberInput > label {
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    /* Loading */
    .loading-text {
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        animation: pulse 1.5s ease-in-out infinite;
    }
    @keyframes pulse { 0%{opacity:.7} 50%{opacity:1} 100%{opacity:.7} }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: var(--gradient); border-radius: 4px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- BACKEND ----------
def initialize_gemini():
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("❌ Google API Key not found. Please add GOOGLE_API_KEY to your Streamlit secrets.")
        st.stop()
    os.environ["GOOGLE_API_KEY"] = api_key
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        temperature=0.8,
        max_tokens=1000
    )

def generate_tweets_with_ai(topic: str, count: int, model) -> list[str]:
    tweet_template = """
    Generate exactly {number} creative and engaging tweets about {topic}.
    Each tweet under 280 characters. Use emojis & hashtags. Vary style.
    Separate each tweet with "---".
    """
    tweet_prompt = PromptTemplate(template=tweet_template, input_variables=["number", "topic"])
    tweet_chain = tweet_prompt | model
    response = tweet_chain.invoke({"number": count, "topic": topic})
    tweets_text = getattr(response, "content", str(response))
    tweets = [t.strip() for t in tweets_text.split("---") if t.strip()]
    return tweets[:count] or [f"🔥 {topic} is trending! #Innovation"]

# ---------- MAIN ----------
def main():
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 0.5rem;">
                ⚡ Gradient Tweet Generator ⚡
            </h1>
            <p style="color: #ccc; font-size: 1.2rem;">Powered by Gemini AI • Generate viral tweets in seconds</p>
        </div>
        """, unsafe_allow_html=True
    )

    if "gemini_model" not in st.session_state:
        with st.spinner("Initializing AI model..."):
            st.session_state.gemini_model = initialize_gemini()

    with st.form("generator", clear_on_submit=False):
        col1, col2 = st.columns([3, 1])
        topic = col1.text_input("💡 What's your topic?", placeholder="e.g. AI, Crypto, Web3...")
        num = col2.number_input("📊 Number of tweets", 1, 20, 5, step=1)
        submitted = st.form_submit_button("🚀 Generate Tweets")

    if submitted:
        if not topic.strip():
            st.warning("⚠️ Please enter a topic first!")
            return

        st.markdown("---")
        with st.spinner(""):
            st.markdown('<div class="loading-text">🤖 AI is crafting your tweets...</div>', unsafe_allow_html=True)
            tweets = generate_tweets_with_ai(topic.strip(), int(num), st.session_state.gemini_model)

        st.markdown(
            f"<h3 class='gradient-text' style='text-align:center;'>✨ Generated {len(tweets)} Tweets for \"{topic}\" ✨</h3>",
            unsafe_allow_html=True
        )

        for i, tweet in enumerate(tweets, 1):
            st.markdown(
                f"""
                <div class="tweet-card">
                    <div style="color:#888; font-size:0.9rem;">Tweet #{i}</div>
                    <div>{tweet}</div>
                    <div style="margin-top:10px; border-top:1px solid #333; color:#666; font-size:0.8rem;">
                        Characters: {len(tweet)} • {datetime.now().strftime("%I:%M %p")}
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

        st.success(f"🎉 Generated {len(tweets)} tweets!")

    st.markdown("---")
    st.markdown(
        """
        <div style="text-align:center; color:#888; font-size:0.9rem;">
            <p class="gradient-text">💡 Pro tip: Try topics like "AI", "Startup Tips", "Web Development"</p>
            <p style="color:#666;">Built with ❤️ using Streamlit & Gemini AI</p>
        </div>
        """, unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
