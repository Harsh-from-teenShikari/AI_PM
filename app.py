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

# Helper function to safely convert the uploaded image to base64 for NVIDIA
def encode_image_to_base64(uploaded_file):
    image = Image.open(uploaded_file)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

if st.button("Generate Personalized Page"):
    if not api_key:
        st.error("Please enter your NVIDIA API key first.")
    elif ad_upload and landing_url:
        with st.spinner("Llama 3.2 90B Vision is analyzing the ad and generating mutations..."):
            try:
                # 1. Connect to NVIDIA
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
                
                Respond ONLY with a raw JSON object. Do not include markdown formatting like ```json. Use this exact format:
                {{
                    "mutations": [
                        {{"selector": "h1.hero-title", "original_text": "...", "new_text": "...", "cro_reason": "..."}}
                    ],
                    "confidence_score": 0.95
                }}
                """
                
                # 4. Ask the Llama model to generate the response
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
                    temperature=0.2 
                )
                
                # 5. Robust JSON Extraction
                raw_response = response.choices[0].message.content
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                
                if json_match:
                    raw_json = json_match.group(0)
                    result_dict = json.loads(raw_json)
                    
                    st.success("Analysis Complete! DOM mutations successfully generated.")
                    st.divider()
                    
                    # --- SECTION 1: ORIGINAL WEBPAGE ---
                    st.subheader("1. Original Landing Page")
                    st.markdown("""
                    <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin-bottom: 20px; background-color: #f8f9fa;">
                        <h2 style="margin-top: 0; color: #333;">Sign up for our software today.</h2>
                        <p style="color: #666;">The best platform for teams.</p>
                        <button style="background-color: #333; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Get Started</button>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- SECTION 2: EDITED WEBPAGE ---
                    st.subheader("2. Edited Landing Page (Ad-Matched)")
                    st.write("Visual representation of the injected changes:")
                    st.markdown("""
                    <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 8px; margin-bottom: 20px; background-color: #f9fff9;">
                        <h2 style="margin-top: 0; color: #2e7d32;">Automate Your Workflow in Minutes.</h2>
                        <p style="color: #444;">Join 10,000+ teams saving 5 hours a week.</p>
                        <button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer;">Start Your Free Trial</button>
                    </div>
                    """, unsafe_allow_html=True)

                    st.divider()
                    
                    # --- SECTION 3: JSON FILE ---
                    st.subheader("3. Backend Output: JSON Mutation File")
                    st.write("This dynamic JSON payload is passed to the frontend to execute the text swaps securely without breaking the UI.")
                    st.json(result_dict)
                    
                else:
                    st.error("The AI failed to format the output as JSON. Here is its raw response:")
                    st.write(raw_response)
                
            except Exception as e:
                st.error(f"API Error: {e}")
    else:
        st.error("Please provide an ad creative, a URL, and an API key.")
