import streamlit as st
import os
from groq import Groq
import base64
from PIL import Image
from PyPDF2 import PdfReader

# 1. Page Setup
st.set_page_config(page_title="OCT Expert (Llama 4 Vision)", layout="wide")
st.title("👁️ OCT Analysis (Powered by Groq Llama 4)")

# 2. Sidebar
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter Groq API Key (starts with gsk_)", type="password")
uploaded_file = st.sidebar.file_uploader("Upload Guidelines/Chapter (PDF)", type=['pdf'])
st.sidebar.info("Model: Llama 4 Scout (Newest Vision Model)")

# 3. Main Input
uploaded_image = st.file_uploader("Upload OCT Scan", type=['png', 'jpg', 'jpeg'])

# Helper: Convert Image to Base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Helper: Extract Text from PDF
def get_pdf_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    # Limit to first 20 pages to avoid token limits
    for i, page in enumerate(reader.pages):
        if i > 20: break 
        text += page.extract_text()
    return text

# 4. Analysis Logic
if st.button("Analyze Scan"):
    if not api_key or not uploaded_file or not uploaded_image:
        st.error("❌ Please provide API Key, PDF, and Image.")
    else:
        try:
            with st.spinner("Analyzing with Llama 4 Vision..."):
                client = Groq(api_key=api_key)

                # Process Inputs
                pdf_text = get_pdf_text(uploaded_file)
                with open("temp_oct.jpg", "wb") as f:
                    f.write(uploaded_image.getbuffer())
                base64_image = encode_image("temp_oct.jpg")

                # The Prompt
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": f"You are an expert Ophthalmologist. Use this medical text as context:\n\n{pdf_text}\n\nAnalyze the attached OCT scan. Describe layers, identify pathology, and suggest a diagnosis."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]

                # UPDATED MODEL ID (2025 Standard)
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model="meta-llama/llama-4-scout-17b-16e-instruct", 
                )

                st.success("Analysis Complete")
                st.markdown(chat_completion.choices[0].message.content)

        except Exception as e:
            st.error(f"Error: {e}")
