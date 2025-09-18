# updated_streamlit_app.py (core parts to paste / replace)
import streamlit as st
import os
import traceback
import importlib.metadata as importlib_metadata

# Force-using the official Genie SDK before any LangChain calls
try:
    import google.generativeai as genai
except Exception as e:
    st.error("google-generativeai not installed: " + str(e))
    raise

# Ensure secret present
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.error("❌ Add GOOGLE_API_KEY to Streamlit secrets")
    st.stop()

# 1) Force configure Google SDK (prevents metadata fallback)
genai.configure(api_key=api_key)

# 2) Also set env var (defensive)
os.environ["GOOGLE_API_KEY"] = api_key

# 3) Show versions so we can pin later if needed
st.write("## Installed package versions (debug)")
libs = ["google-generativeai", "langchain-google-genai", "langchain", "google-auth"]
for lib in libs:
    try:
        st.write(f"{lib} == {importlib_metadata.version(lib)}")
    except Exception as ex:
        st.write(f"{lib} : not found ({ex})")

# 4) Now import LangChain wrapper and build chain
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain import PromptTemplate
except Exception as e:
    st.error("Failed importing LangChain or wrapper: " + str(e))
    raise

# Create prompt as before
tweet_template = "Give me {number} tweets on {topic}"
tweet_prompt = PromptTemplate(template=tweet_template, input_variables=["number", "topic"])

# Initialize the Gemini model and pass the key explicitly if wrapper supports it
try:
    gemini_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        temperature=0.8,
        max_tokens=1000,
        google_api_key=api_key  # explicit — many wrappers accept this param
    )
except TypeError:
    # Fallback if the wrapper does not accept google_api_key
    gemini_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.8, max_tokens=1000)

# Create the chain (your shorter pipe syntax)
tweet_chain = tweet_prompt | gemini_model

# UI
st.header("Tweet Generator - Sam")
topic = st.text_input("Topic")
number = st.number_input("Number of tweets", min_value=1, max_value=10, value=1, step=1)

if st.button("Generate"):
    try:
        with st.spinner("Calling model..."):
            resp = tweet_chain.invoke({"number": number, "topic": topic})
        # safe print of response
        if hasattr(resp, "content"):
            st.code(resp.content)
        else:
            st.write(resp)
    except Exception as e:
        st.error("🚨 Invocation failed. See traceback below.")
        st.text(traceback.format_exc())
