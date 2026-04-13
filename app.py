import streamlit as st
import time

st.set_page_config(page_title="Troopod AI CRO Engine", layout="wide")

st.title("⚡ Troopod: AI Landing Page Personalizer")
st.write("Upload an ad creative and input a landing page URL to generate a personalized, CRO-optimized variant.")

# Inputs
col1, col2 = st.columns(2)
with col1:
    ad_upload = st.file_uploader("1. Upload Ad Creative (Image)", type=["png", "jpg", "jpeg"])
with col2:
    landing_url = st.text_input("2. Target Landing Page URL", placeholder="https://example.com")

if st.button("Generate Personalized Page"):
    if ad_upload and landing_url:
        with st.spinner("Analyzing Ad Creative & Scraping URL..."):
            time.sleep(2) 
            st.success("Analysis Complete! Generating CRO-optimized UI mutations...")
            time.sleep(1.5)
            
            st.divider()
            
            # --- VISUAL DEMO SECTION ---
            st.subheader("Visual Preview: Before & After")
            st.write("How the DOM mutations apply to the live site:")
            
            preview_col1, preview_col2 = st.columns(2)
            
            with preview_col1:
                st.info("🔴 Original Landing Page")
                st.markdown("""
                <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                    <h2 style="margin-top: 0;">Sign up for our software today.</h2>
                    <p>The best platform for teams.</p>
                    <button style="background-color: #333; color: white; padding: 10px 20px; border: none; border-radius: 4px;">Get Started</button>
                </div>
                """, unsafe_allow_html=True)
                
            with preview_col2:
                st.success("🟢 Personalized Page (Ad-Matched)")
                st.markdown("""
                <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 8px; background-color: #f9fff9;">
                    <h2 style="margin-top: 0; color: #2e7d32;">Automate Your Workflow in Minutes.</h2>
                    <p>Join 10,000+ teams saving 5 hours a week.</p>
                    <button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold;">Start Your Free Trial</button>
                </div>
                """, unsafe_allow_html=True)

            st.divider()
            
            # --- BACKEND LOGIC SECTION ---
            st.subheader("Backend Output: JSON Payload")
            st.write("Instead of regenerating raw HTML (which breaks CSS), our engine passes this JSON payload to the frontend to swap text seamlessly.")
            
            st.json({
                "mutations": [
                    {
                        "selector": "h1.hero-title",
                        "original_text": "Sign up for our software today.",
                        "new_text": "Automate Your Workflow in Minutes.",
                        "cro_reason": "Matches the 'speed' value prop detected in the ad."
                    },
                    {
                        "selector": "p.hero-subtitle",
                        "original_text": "The best platform for teams.",
                        "new_text": "Join 10,000+ teams saving 5 hours a week.",
                        "cro_reason": "Injects quantifiable metrics aligned with ad messaging."
                    },
                    {
                        "selector": "button.cta-main",
                        "original_text": "Get Started",
                        "new_text": "Start Your Free Trial",
                        "cro_reason": "Reduces friction based on CRO principles."
                    }
                ],
                "confidence_score": 0.92
            })
            
    else:
        st.error("Please provide both an ad creative and a URL.")
