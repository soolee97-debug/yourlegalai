import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
import fitz
import re

st.set_page_config(page_title="Legal_AI: 문서 분석", layout="wide")

@st.cache_resource
def get_google_client():
    try:
        # 금고에서 정보를 읽어옵니다.
        info = dict(st.secrets["gcp_service_account"])
        raw_key = info["private_key"]
        
        # [핵심] 모든 공백을 제거하고 64자마다 줄바꿈을 넣어 PEM 형식을 강제 생성합니다.
        clean_key = "".join(re.findall(r'[A-Za-z0-9+/=]+', raw_key))
        formatted_key = "-----BEGIN PRIVATE KEY-----\n"
        for i in range(0, len(clean_key), 64):
            formatted_key += clean_key[i:i+64] + "\n"
        formatted_key += "-----END PRIVATE KEY-----\n"
        
        info["private_key"] = formatted_key
        
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"❌ 시스템 인증 연결 실패: {e}")
        return None

client = get_google_client()

st.title("⚖️ Legal_AI: 서비스 가동")

if client:
    st.success("✅ 시스템이 정상적으로 연결되었습니다.")
    uploaded_file = st.file_uploader("분석할 법인등기부 PDF를 업로드하세요", type=["pdf", "png", "jpg"])
    if uploaded_file:
        with st.spinner('AI가 정밀 분석 중입니다...'):
            try:
                text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        text += client.document_text_detection(image=vision.Image(content=pix.tobytes("png"))).full_text_annotation.text + "\n"
                else:
                    text = client.document_text_detection(image=vision.Image(content=uploaded_file.getvalue())).full_text_annotation.text
                
                st.subheader("📝 분석 결과")
                st.text_area("인식된 내용", text, height=500)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
