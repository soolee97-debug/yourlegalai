import streamlit as st
import json
from google.cloud import vision
from google.oauth2 import service_account
import fitz

st.set_page_config(page_title="Legal_AI: 문서 분석", layout="wide")

def get_google_client():
    try:
        # 금고에 넣어둔 JSON 텍스트를 통째로 읽어 파이썬 객체로 만듭니다.
        # 이 방식은 글자 깨짐 사고가 발생하지 않는 가장 안전한 방법입니다.
        info = json.loads(st.secrets["GCP_JSON"])
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"❌ 인증 연결 실패: {e}")
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
