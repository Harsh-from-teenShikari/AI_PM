import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

st.set_page_config(page_title="Troopod AI CRO Engine", layout="wide")

st.title("⚡ Troopod: Real AI Landing Page Personalizer")

# Input for API Key
api_key = st.text_input("Enter Google Gemini API Key (to power the AI):", type="password")

col1, col2 = st.columns(2)
with col1:
    ad_upload = st.file_uploader("1. Upload Ad Creative (Image)", type=["png", "jpg", "jpeg"])
with col2:
    landing_url = st.text_input("2. Target Landing Page URL", placeholder="https://example.com")

if st.button("Generate Personalized Page"):
    if not api_key:
        st.error("Please enter your API key first.")
    elif ad_upload and landing_url:
        with st.spinner("Connecting to Google API and auto-discovering models..."):
            try:
                # 1. Connect to the AI
                genai.configure(api_key=api_key)
                
                # 2. AUTO-DISCOVERY: Ask Google what models this API key has access to
                valid_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # Clean up the name by removing 'models/' from the string
                        clean_name = m.name.replace('models/', '')
                        valid_models.append(clean_name)
                
                if not valid_models:
                    st.error("Your API key does not have access to any generation models.")
                    st.stop()
                
                # 3. Pick the best available model (prioritizing flash, then pro, then anything else)
                chosen_model = valid_models[0] # Default to the first one found
                for m in valid_models:
                    if '1.5-flash' in m:
                        chosen_model = m
                        break
                    elif 'gemini-pro' in m or 'gemini-1.0-pro' in m:
                        chosen_model = m
                
                st.success(f"Connected! Auto-selected model: `{chosen_model}`")
                
                # 4. Initialize the chosen model
                model = genai.GenerativeModel(chosen_model)
                
                # 5. Prepare the Image
                img = Image.open(ad_upload)
                
                # 6. Give the AI its instructions
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
                
                # 7. Ask the AI to generate the response
                response = model.generate_content([prompt, img])
                
                # Clean up the output to display nicely
                raw_json = response.text.replace('```json', '').replace('```', '').strip()
                result_dict = json.loads(raw_json)
                
                st.subheader("Dynamic AI Output:")
                st.json(result_dict)
                
            except Exception as e:
                st.error(f"API Error: {e}")
    else:
        st.error("Please provide an ad creative, a URL, and an API key.")
