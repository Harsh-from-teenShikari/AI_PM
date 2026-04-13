import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

st.set_page_config(page_title="Troopod AI CRO Engine", layout="wide")

st.title("⚡ Troopod: Real AI Landing Page Personalizer")

# Input for API Key (Securely entered by you or the reviewer)
api_key = st.text_input("Enter Google Gemini API Key (to power the AI):", type="password")

col1, col2 = st.columns(2)
with col1:
    ad_upload = st.file_uploader("1. Upload Ad Creative (Image)", type=["png", "jpg", "jpeg"])
with col2:
    landing_url = st.text_input("2. Target Landing Page URL", placeholder="https://example.com")

if st.button("Generate Personalized Page"):
    if not api_key:
        st.error("Please enter an API key first.")
    elif ad_upload and landing_url:
        with st.spinner("AI is analyzing the ad and generating real mutations..."):
            try:
                # 1. Connect to the AI
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 2. Prepare the Image
                img = Image.open(ad_upload)
                
                # 3. Give the AI its instructions (The Prompt)
                prompt = f"""
                You are a Conversion Rate Optimization (CRO) expert. 
                I am giving you an ad creative image and a target URL: {landing_url}
                
                Analyze the ad's main message, tone, and offer. Then, imagine the landing page for that URL.
                Provide exactly 3 text mutations (changes) to make the landing page match the ad better.
                
                Respond ONLY with a raw JSON object using this exact format:
                {{
                    "mutations": [
                        {{"selector": "h1.hero-title", "original_text": "...", "new_text": "...", "cro_reason": "..."}}
                    ],
                    "confidence_score": 0.95
                }}
                """
                
                # 4. Ask the AI to generate the response
                response = model.generate_content([prompt, img])
                
                # Clean up the output to display nicely
                raw_json = response.text.replace('```json', '').replace('```', '').strip()
                result_dict = json.loads(raw_json)
                
                st.success("Analysis Complete! Here are the dynamic, AI-generated results:")
                st.json(result_dict)
                
            except Exception as e:
                st.error(f"Something went wrong with the AI: {e}")
    else:
        st.error("Please provide an ad creative, a URL, and an API key.")
