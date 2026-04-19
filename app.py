import streamlit as st
import json
import base64
from google.cloud import vision
from google.oauth2 import service_account
import fitz

st.set_page_config(page_title="Legal_AI: 완전 자동화", layout="wide")

@st.cache_resource
def get_automated_client():
    try:
        # 1. 금고(Secrets)에서 암호문을 가져옵니다.
        b64_key = st.secrets["GCP_KEY_B64"]
        
        # 2. 시스템 내부에서 직접 해독 (복사 중 글자 깨짐 사고 0%)
        decoded_key = base64.b64decode(b64_key).decode('utf-8')
        info = json.loads(decoded_key)
        
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"❌ 보안 인증 실패: {e}")
        return None

# 접속 시 자동으로 인증 시도
client = get_automated_client()

st.title("⚖️ Legal_AI: 서비스 가동 중")

if client:
    st.success("✅ 보안 인증 완료! 이제 파일만 올리시면 됩니다.")
    uploaded_file = st.file_uploader("분석할 등기부(PDF/이미지)를 업로드하세요", type=["pdf", "png", "jpg"])
    
    if uploaded_file:
        with st.spinner('AI 분석 중...'):
            try:
                text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        res = client.document_text_detection(image=vision.Image(content=pix.tobytes("png")))
                        text += res.full_text_annotation.text + "\n"
                else:
                    res = client.document_text_detection(image=vision.Image(content=uploaded_file.getvalue()))
                    text = res.full_text_annotation.text
                
                st.subheader("📝 분석 결과")
                st.text_area("인식된 내용", text, height=500)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
else:
    st.warning("🔑 보안 설정(Secrets)에서 GCP_KEY_B64 값을 확인해주세요.")
