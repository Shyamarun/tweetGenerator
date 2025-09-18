# streamlit_app.py
# Tweet-Generator UI with Gemini AI – Neon-Blue / Dark theme
# Run:  streamlit run streamlit_app.py

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from datetime import datetime
import time
import os

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
    
    /* Hide streamlit header and footer */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    .main > div {
        padding-top: 2rem;
    }
    
    /* inputs */
    .stTextInput > div > div > input {
        background: #1a1a1a;
        color: #00e5ff;
        caret-color: #00e5ff;
        border: 1px solid #00e5ff;
        border-radius: 8px;
        padding: 10px;
        font-size: 1.1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border: 2px solid #00e5ff;
        box-shadow: 0 0 10px rgba(0,229,255,0.3);
    }
    
    .stNumberInput > div > div > input {
        background: #1a1a1a;
        color: #00e5ff;
        caret-color: #00e5ff;
        border: 1px solid #00e5ff;
        border-radius: 8px;
        padding: 10px;
        font-size: 1.1rem;
    }
    
    .stNumberInput > div > div > input:focus {
        border: 2px solid #00e5ff;
        box-shadow: 0 0 10px rgba(0,229,255,0.3);
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
        width: 100%;
    }
    
    div.stButton > button:hover {
        background: #00e5ff;
        color: #0e0e0e;
        box-shadow: 0 0 15px #00e5ff;
        transform: translateY(-1px);
    }
    
    /* tweet cards */
    .tweet-card {
        background: linear-gradient(145deg, #161616, #1a1a1a);
        border-left: 4px solid #00e5ff;
        padding: 15px 20px;
        margin: 15px 0;
        border-radius: 8px;
        font-size: 1.1rem;
        color: #ffffff;
        box-shadow: 0 0 10px rgba(0,229,255,0.25);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .tweet-card:hover {
        box-shadow: 0 0 20px rgba(0,229,255,0.4);
        transform: translateX(5px);
    }
    
    .tweet-card::before {
        content: "🐦";
        position: absolute;
        top: 10px;
        right: 15px;
        opacity: 0.3;
        font-size: 1.2rem;
    }
    
    /* spinner */
    .stSpinner > div {
        border-top-color: #00e5ff;
    }
    
    /* warning messages */
    .stAlert {
        background-color: #1a1a1a;
        border: 1px solid #ff6b35;
        color: #ffffff;
    }
    
    /* form styling */
    .stForm {
        background: #161616;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333333;
    }
    
    /* labels */
    .stTextInput > label, .stNumberInput > label {
        color: #00e5ff !important;
        font-weight: 600;
    }
    
    /* success message */
    .stSuccess {
        background-color: rgba(0, 229, 255, 0.1);
        border: 1px solid #00e5ff;
        color: #00e5ff;
    }
    
    /* loading animation */
    .loading-text {
        color: #00e5ff;
        text-align: center;
        font-size: 1.2rem;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- BACKEND SETUP ----------
def initialize_gemini():
    """Initialize Gemini model with API key from secrets"""
    try:
        # Get API key from Streamlit secrets
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key:
            st.error("❌ Google API Key not found in secrets. Please add GOOGLE_API_KEY to your Streamlit secrets.")
            st.stop()
        
        os.environ['GOOGLE_API_KEY'] = api_key
        
        # Initialize Google's Gemini model
        gemini_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            temperature=0.8,
            max_tokens=1000
        )
        
        return gemini_model
    
    except Exception as e:
        st.error(f"❌ Error initializing Gemini: {str(e)}")
        st.stop()

def generate_tweets_with_ai(topic: str, count: int, model) -> list[str]:
    """Generate tweets using Gemini AI"""
    try:
        # Create prompt template for generating tweets
        tweet_template = """
        Generate exactly {number} creative and engaging tweets about {topic}. 

        Requirements:
        - Each tweet should be under 280 characters
        - Make them engaging, informative, and shareable
        - Use relevant emojis and hashtags where appropriate
        - Vary the style (some can be questions, statements, tips, etc.)
        - Make them feel authentic and not overly promotional
        - Separate each tweet with "---"

        Topic: {topic}
        Number of tweets: {number}

        Generate the tweets now:
        """
        
        tweet_prompt = PromptTemplate(
            template=tweet_template, 
            input_variables=['number', 'topic']
        )
        
        # Create chain
        tweet_chain = tweet_prompt | model
        
        # Generate tweets
        response = tweet_chain.invoke({"number": count, "topic": topic})
        
        # Parse the response
        if hasattr(response, 'content'):
            tweets_text = response.content
        else:
            tweets_text = str(response)
        
        # Split tweets by separator
        tweets = [tweet.strip() for tweet in tweets_text.split("---") if tweet.strip()]
        
        # If we don't get enough tweets, pad with the ones we have
        while len(tweets) < count and len(tweets) > 0:
            tweets.extend(tweets[:count-len(tweets)])
        
        return tweets[:count] if tweets else [f"🔥 {topic} is the future! Stay tuned for more updates. #Innovation"]
    
    except Exception as e:
        st.error(f"❌ Error generating tweets: {str(e)}")
        return [f"⚡ Exciting things happening with {topic}! #TechTrends"]

# ---------- MAIN UI ----------
def main():
    # Header with neon effect
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #00e5ff; font-size: 3rem; text-shadow: 0 0 20px #00e5ff; margin-bottom: 0.5rem;">
                ⚡ Neon Tweet Generator ⚡
            </h1>
            <p style="color: #888; font-size: 1.2rem; margin-bottom: 2rem;">
                Powered by Google Gemini AI • Generate viral tweets in seconds
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Initialize Gemini model
    if 'gemini_model' not in st.session_state:
        with st.spinner('Initializing AI model...'):
            st.session_state.gemini_model = initialize_gemini()
    
    # Main form
    with st.form("generator", clear_on_submit=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            topic = st.text_input(
                "💡 What's your topic?", 
                placeholder="e.g. Artificial Intelligence, Crypto, Web3, Climate Change...",
                help="Enter any topic you want to create tweets about"
            )
        
        with col2:
            num = st.number_input(
                "📊 Number of tweets", 
                min_value=1, 
                max_value=20, 
                value=5, 
                step=1,
                help="Choose how many tweets to generate"
            )
        
        submitted = st.form_submit_button("🚀 Generate Tweets")
    
    # Generate tweets when form is submitted
    if submitted and topic.strip():
        st.markdown("---")
        
        # Loading animation
        with st.spinner(''):
            st.markdown('<div class="loading-text">🤖 AI is crafting your tweets...</div>', unsafe_allow_html=True)
            
            # Generate tweets using AI
            tweets = generate_tweets_with_ai(topic.strip(), int(num), st.session_state.gemini_model)
        
        # Display results
        st.markdown(
            f"""
            <h3 style='color: #00e5ff; text-align: center; margin: 2rem 0 1rem 0;'>
                ✨ Generated {len(tweets)} Tweets for "{topic}" ✨
            </h3>
            """, 
            unsafe_allow_html=True
        )
        
        # Display each tweet
        for i, tweet in enumerate(tweets, 1):
            st.markdown(
                f'''
                <div class="tweet-card">
                    <div style="color: #888; font-size: 0.9rem; margin-bottom: 10px;">Tweet #{i}</div>
                    <div>{tweet}</div>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #333; color: #666; font-size: 0.8rem;">
                        Characters: {len(tweet)} • {datetime.now().strftime("%I:%M %p")}
                    </div>
                </div>
                ''', 
                unsafe_allow_html=True
            )
        
        # Success message
        st.success(f"🎉 Successfully generated {len(tweets)} tweets! Copy and paste to your favorite platform.")
    
    elif submitted:
        st.warning("⚠️ Please enter a topic first to generate tweets!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #555; font-size: 0.9rem; margin-top: 2rem;">
            <p>💡 Pro tip: Try topics like "AI", "Startup Tips", "Web Development", "Marketing" for best results</p>
            <p style="margin-top: 1rem;">Built with ❤️ using Streamlit & Google Gemini AI</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
