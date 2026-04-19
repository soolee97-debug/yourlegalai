import streamlit as st
import os, re, json, pandas as pd
from datetime import datetime
from google.cloud import vision
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from google.oauth2 import service_account
import fitz # PyMuPDF

st.set_page_config(page_title="Legal_AI: 문서 자동화", layout="wide")

def get_google_client():
    try:
        # 금고의 첫 번째 값을 무조건 가져옵니다.
        val = list(st.secrets.values())[0]
        # 혹시 따옴표가 중복으로 감싸져 있으면 뗍니다.
        val = val.strip().strip("'").strip('"')
        key_dict = json.loads(val)
        credentials = service_account.Credentials.from_service_account_info(key_dict)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        st.error(f"❌ 보안 키 인식 실패: {e}")
        return None

client = get_google_client()
if client:
    st.markdown("<h1 style='color: #2c3e50;'>⚖️ Legal_AI: PDF 등기부 통합 분석</h1>", unsafe_allow_html=True)
    # --- 이후 로직 (회사명 추출, 임기 계산 등) 동일 ---
    uploaded_file = st.file_uploader("법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])
    if uploaded_file:
        with st.spinner('문서 분석 중...'):
            full_text = ""
            if uploaded_file.type == "application/pdf":
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                for page in doc:
                    pix = page.get_pixmap()
                    image = vision.Image(content=pix.tobytes("png"))
                    full_text += client.document_text_detection(image=image).full_text_annotation.text + "\n"
            else:
                image = vision.Image(content=uploaded_file.getvalue())
                full_text = client.document_text_detection(image=image).full_text_annotation.text
            st.success("✅ 분석 완료! 아래에서 결과를 확인하세요.")
            st.write(full_text[:500] + "...") # 우선 텍스트 잘 나오는지 확인용
else:
    st.stop()
