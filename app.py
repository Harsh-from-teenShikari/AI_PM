import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import base64
from PIL import Image
import io
import json
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Troopod AI CRO Engine", layout="wide")

st.title("⚡ Troopod: Live AI Landing Page Personalizer")

# Input for NVIDIA API Key
api_key = st.text_input("Enter NVIDIA API Key (starts with 'nvapi-'):", type="password")

col1, col2 = st.columns(2)
with col1:
    ad_upload = st.file_uploader("1. Upload Ad Creative (Image)", type=["png", "jpg", "jpeg"])
with col2:
    landing_url = st.text_input("2. Target Landing Page URL", placeholder="https://example.com")

# Helper function for Image
def encode_image_to_base64(uploaded_file):
    image = Image.open(uploaded_file)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Helper function to fetch real HTML
def fetch_real_html(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
       
        if not soup.find('base'):
            base = soup.new_tag('base', href=url)
            soup.head.insert(0, base)
            
        return soup
    except Exception as e:
        return None

if st.button("Generate Personalized Page"):
    if not api_key:
        st.error("Please enter your NVIDIA API key first.")
    elif ad_upload and landing_url:
        with st.spinner("Fetching live website and analyzing ad creative..."):
            
            # FETCH WEBSITE
            live_soup = fetch_real_html(landing_url)
            if not live_soup:
                st.error("Could not fetch the live URL. Some websites block scrapers. Try a simpler site like 'https://example.com'")
                st.stop()
                
            # Extract the actual text
            page_text = live_soup.get_text(separator=' ', strip=True)[:1500] 
            
            try:
                # 2. CONNECT TO AI 
                client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)
                base64_image = encode_image_to_base64(ad_upload)
                
                # 3. PROMPT THE AI WITH REAL DATA
                prompt_text = f"""
                You are a Conversion Rate Optimization (CRO) expert. 
                Ad target URL: {landing_url}
                Here is the actual visible text scraped from that landing page: "{page_text}"
                
                Analyze the uploaded ad image's main message. 
                Provide exactly 3 text mutations to make the landing page match the ad better.
                Use basic HTML tags as the 'selector' (e.g., "h1", "p", "button", "a").
                
                Respond ONLY with a raw JSON object. Do not include markdown formatting:
                {{
                    "mutations": [
                        {{"selector": "h1", "original_text": "...", "new_text": "...", "cro_reason": "..."}}
                    ]
                }}
                """
                
                response = client.chat.completions.create(
                    model="meta/llama-3.2-90b-vision-instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ],
                    max_tokens=1024, temperature=0.1 
                )
                
                # 4. PARSE AI JSON
                raw_response = response.choices[0].message.content
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                
                if json_match:
                    result_dict = json.loads(json_match.group(0))
                    
                    st.success("Analysis Complete! DOM mutations successfully generated and applied.")
                    st.divider()
                    
                    # 5. RENDER REAL PAGE 
                    st.subheader("1. Original Landing Page (Live)")
                    original_html_str = str(live_soup)
                    components.html(original_html_str, height=400, scrolling=True)
                    
                    # 6. APPLY MUTATIONS 
                    edited_soup = BeautifulSoup(original_html_str, 'html.parser')
                    for mutation in result_dict.get("mutations", []):
                        selector = mutation.get("selector", "")
                        new_text = mutation.get("new_text", "")
                        # Try to find the element and swap the text
                        try:
                            elements = edited_soup.select(selector)
                            if elements:
                                elements[0].string = new_text 
                        except:
                            pass 
                            
                    #  7. RENDER EDITED PAGE 
                    st.subheader("2. Edited Landing Page (Mutated in Real-Time)")
                    st.write("Notice how the UI and CSS remained intact, but the text was dynamically updated:")
                    components.html(str(edited_soup), height=400, scrolling=True)

                    st.divider()
                    
                    # 8. JSON OUTPUT
                    st.subheader("3. Backend Output: JSON Mutation File")
                    st.json(result_dict)
                    
                else:
                    st.error("The AI failed to format the output as JSON.")
                
            except Exception as e:
                st.error(f"API Error: {e}")
    else:
        st.error("Please provide an ad creative, a URL, and an API key.")
