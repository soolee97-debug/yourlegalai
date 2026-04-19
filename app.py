import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
import fitz

st.set_page_config(page_title="Legal_AI", layout="wide")

@st.cache_resource
def get_google_client():
    try:
        # Secrets에서 정보를 그대로 가져옵니다. 
        # 따옴표 세 개를 썼기 때문에 별도의 글자 변환 없이 바로 작동합니다.
        info = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"인증 연결 실패: {e}")
        return None

client = get_google_client()

st.title("⚖️ Legal_AI: 서비스 가동 중")

if client:
    st.success("✅ 시스템이 정상 가동됩니다.")
    uploaded_file = st.file_uploader("법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])
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
