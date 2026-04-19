import streamlit as st
import json
from google.cloud import vision
from google.oauth2 import service_account
import fitz

st.set_page_config(page_title="Legal_AI: 문서 분석", layout="wide")

def get_google_client():
    try:
        # Streamlit Secrets에서 보안 정보를 안전하게 읽어옵니다.
        # 이 방식은 텍스트 깨짐 현상이 발생하지 않습니다.
        info = dict(st.secrets["gcp_service_account"])
        # JSON 안에 섞인 줄바꿈 기호를 실제 줄바꿈으로 변환
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"❌ 보안 금고 연결 실패: {e}")
        st.info("💡 앱 설정(Settings > Secrets)에 보안키를 입력했는지 확인해주세요.")
        return None

client = get_google_client()

st.title("⚖️ Legal_AI: 서비스 가동 중")

if client:
    st.success("✅ 시스템 정상 가동")
    uploaded_file = st.file_uploader("법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])
    if uploaded_file:
        with st.spinner('AI 분석 중...'):
            try:
                full_text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        full_text += client.document_text_detection(image=vision.Image(content=pix.tobytes("png"))).full_text_annotation.text + "\n"
                else:
                    full_text = client.document_text_detection(image=vision.Image(content=uploaded_file.getvalue())).full_text_annotation.text
                
                st.subheader("📝 분석 결과")
                st.text_area("인식된 텍스트", full_text, height=500)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
