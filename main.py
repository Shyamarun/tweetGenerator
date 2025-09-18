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
    /* Define the gradient theme */
    :root {
        --gradient: linear-gradient(90deg, #ff6f61, #ffb88c, #6b7280, #60a5fa);
        --gradient-bg: linear-gradient(135deg, #ff6f61, #ffb88c, #6b7280, #60a5fa);
    }
    
    /* Global dark background with gradient overlay */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%);
        color: #ffffff;
        position: relative;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--gradient);
        opacity: 0.03;
        pointer-events: none;
        z-index: -1;
    }
    
    /* Hide streamlit header and footer */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    .main > div {
        padding-top: 2rem;
    }
    
    /* Input fields with gradient borders */
    .stTextInput > div > div > input {
        background: rgba(26, 26, 26, 0.9);
        color: #ffffff;
        caret-color: #ff6f61;
        border: 2px solid transparent;
        background-clip: padding-box;
        border-radius: 10px;
        padding: 12px 15px;
        font-size: 1.1rem;
        position: relative;
    }
    
    .stTextInput > div > div {
        position: relative;
    }
    
    .stTextInput > div > div::before {
        content: '';
        position: absolute;
        inset: 0;
        padding: 2px;
        background: var(--gradient);
        border-radius: 10px;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: xor;
        -webkit-mask-composite: xor;
        pointer-events: none;
    }
    
    .stTextInput > div > div > input:focus {
        outline: none;
        box-shadow: 0 0 20px rgba(255, 111, 97, 0.3);
    }
    
    .stNumberInput > div > div > input {
        background: rgba(26, 26, 26, 0.9);
        color: #ffffff;
        caret-color: #ff6f61;
        border: 2px solid transparent;
        background-clip: padding-box;
        border-radius: 10px;
        padding: 12px 15px;
        font-size: 1.1rem;
    }
    
    .stNumberInput > div > div {
        position: relative;
    }
    
    .stNumberInput > div > div::before {
        content: '';
        position: absolute;
        inset: 0;
        padding: 2px;
        background: var(--gradient);
        border-radius: 10px;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: xor;
        -webkit-mask-composite: xor;
        pointer-events: none;
    }
    
    .stNumberInput > div > div > input:focus {
        outline: none;
        box-shadow: 0 0 20px rgba(255, 111, 97, 0.3);
    }
    
    /* Button with gradient background - FIXED VISIBILITY */
    div.stButton > button {
        background: var(--gradient) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 0.8rem 2.5rem !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease-in-out !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(255, 111, 97, 0.3) !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7) !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(255, 111, 97, 0.5) !important;
        filter: brightness(1.1) !important;
    }
    
    div.stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Tweet cards with gradient accents */
    .tweet-card {
        background: linear-gradient(145deg, #1a1a1a, #252525);
        border: 2px solid transparent;
        background-clip: padding-box;
        padding: 20px 25px;
        margin: 20px 0;
        border-radius: 12px;
        font-size: 1.1rem;
        color: #ffffff;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .tweet-card::before {
        content: '';
        position: absolute;
        inset: 0;
        padding: 2px;
        background: var(--gradient);
        border-radius: 12px;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: xor;
        -webkit-mask-composite: xor;
        opacity: 0.6;
    }
    
    .tweet-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(255, 111, 97, 0.2);
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
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Form styling with gradient */
    .stForm {
        background: linear-gradient(145deg, #1a1a1a, #252525);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid transparent;
        background-clip: padding-box;
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
        mask-composite: xor;
        -webkit-mask-composite: xor;
        opacity: 0.4;
    }
    
    /* Labels with gradient text */
    .stTextInput > label, .stNumberInput > label {
        background: var(--gradient);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    
    /* Success and warning messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(255, 111, 97, 0.1), rgba(255, 184, 140, 0.1));
        border: 1px solid #ff6f61;
        color: #ffffff;
        border-radius: 10px;
    }
    
    .stAlert {
        background: linear-gradient(135deg, rgba(255, 111, 97, 0.1), rgba(255, 184, 140, 0.1));
        border: 1px solid #ffb88c;
        color: #ffffff;
        border-radius: 10px;
    }
    
    /* Loading animation */
    .loading-text {
        background: var(--gradient);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Spinner color */
    .stSpinner > div {
        border-top-color: #ff6f61 !important;
        border-right-color: #ffb88c !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--gradient);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        filter: brightness(1.2);
    }
    
    @keyframes pulse {
        0% { opacity: 0.7; }
        50% { opacity: 1; }
        100% { opacity: 0.7; }
    }
    
    /* Gradient text utility */
    .gradient-text {
        background: var(--gradient);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
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
            <h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                ⚡ Gradient Tweet Generator ⚡
            </h1>
            <p style="color: #cccccc; font-size: 1.2rem; margin-bottom: 2rem; font-weight: 300;">
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
            <h3 class="gradient-text" style='text-align: center; margin: 2rem 0 1rem 0; font-size: 1.8rem;'>
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
        <div style="text-align: center; color: #888; font-size: 0.9rem; margin-top: 2rem;">
            <p class="gradient-text" style="font-size: 1rem; margin-bottom: 1rem;">💡 Pro tip: Try topics like "AI", "Startup Tips", "Web Development", "Marketing" for best results</p>
            <p style="margin-top: 1rem; color: #666;">Built with ❤️ using Streamlit & Google Gemini AI</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
