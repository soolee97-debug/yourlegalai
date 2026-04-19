import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
import fitz
import re

st.set_page_config(page_title="Legal_AI", layout="wide")

@st.cache_resource
def get_final_stable_client():
    try:
        # 1. 금고에서 순수 알맹이만 꺼냅니다.
        raw_body = st.secrets["RAW_KEY_DATA"]
        
        # 2. 혹시나 섞였을지 모를 불필요한 공백을 기계적으로 제거합니다.
        clean_body = "".join(raw_body.split())
        
        # 3. 파이썬이 직접 '정석 PEM 규격'으로 재조립합니다. 
        # (이 과정에서 \n 충돌이 원천 차단됩니다.)
        pem_key = "-----BEGIN PRIVATE KEY-----\n"
        for i in range(0, len(clean_body), 64):
            pem_key += clean_body[i:i+64] + "\n"
        pem_key += "-----END PRIVATE KEY-----\n"
        
        # 4. 전체 인증 정보 구성
        info = {
            "type": "service_account",
            "project_id": "formal-facet-469109-n9",
            "private_key_id": "a75d5c613386e549458b7f9ce7429053fa690601",
            "private_key": pem_key,
            "client_email": "97202050044-compute@developer.gserviceaccount.com",
            "client_id": "106591061735155848403",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/97202050044-compute%40developer.gserviceaccount.com"
        }
        
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"인증 시스템 복구 실패: {e}")
        return None

client = get_final_stable_client()

st.title("⚖️ Legal_AI: 서비스 가동")

if client:
    st.success("✅ 시스템이 정상 연결되었습니다!")
    uploaded_file = st.file_uploader("분석할 법인등기부 PDF를 업로드하세요", type=["pdf", "png", "jpg"])
    if uploaded_file:
        with st.spinner('AI 분석 중...'):
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
