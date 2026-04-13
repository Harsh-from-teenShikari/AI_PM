import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io
import json
import re

st.set_page_config(page_title="Troopod AI CRO Engine", layout="wide")

st.title("⚡ Troopod: Real AI Landing Page Personalizer")

# Input for NVIDIA API Key
api_key = st.text_input("Enter NVIDIA API Key (starts with 'nvapi-'):", type="password")

col1, col2 = st.columns(2)
with col1:
    ad_upload = st.file_uploader("1. Upload Ad Creative (Image)", type=["png", "jpg", "jpeg"])
with col2:
    landing_url = st.text_input("2. Target Landing Page URL", placeholder="https://troopod.io")

# Helper function to convert the uploaded image to base64 for NVIDIA
def encode_image_to_base64(uploaded_file):
    image = Image.open(uploaded_file)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

if st.button("Generate Personalized Page"):
    if not api_key:
        st.error("Please enter your NVIDIA API key first.")
    elif ad_upload and landing_url:
        with st.spinner("Llama 3.2 90B Vision is analyzing the ad and generating mutations..."):
            try:
                # 1. Connect to NVIDIA NIM using the OpenAI SDK
                client = OpenAI(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=api_key
                )
                
                # 2. Process the image
                base64_image = encode_image_to_base64(ad_upload)
                
                # 3. Give the AI its instructions
                prompt_text = f"""
                You are a Conversion Rate Optimization (CRO) expert. 
                I am giving you an ad creative image and a target URL: {landing_url}
                
                Analyze the ad's main message, tone, and offer. Then, imagine the landing page for that URL.
                Provide exactly 3 text mutations (changes) to make the landing page match the ad better.
                
                Respond ONLY with a raw JSON object using this exact format without any markdown formatting:
                {{
                    "mutations": [
                        {{"selector": "h1.hero-title", "original_text": "...", "new_text": "...", "cro_reason": "..."}}
                    ],
                    "confidence_score": 0.95
                }}
                """
                
                # 4. Ask the Llama 3.2 Vision model to generate the response
                response = client.chat.completions.create(
                    model="meta/llama-3.2-90b-vision-instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=1024,
                    temperature=0.2 # Low temperature for more reliable JSON
                )
                
                # 5. Robust JSON Extraction
                raw_response = response.choices[0].message.content
                
                # Use regex to find everything between the first { and the last }
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                
                if json_match:
                    raw_json = json_match.group(0)
                    result_dict = json.loads(raw_json)
                    
                    st.success("Analysis Complete! Here are the dynamic, NVIDIA AI-generated results:")
                    st.json(result_dict)
                else:
                    # If it completely failed to make JSON, show what it actually said so we can debug it
                    st.error("The AI failed to format the output correctly. Here is its raw response:")
                    st.write(raw_response)
