import streamlit as st
from google.cloud import vision
import fitz  # PyMuPDF

st.set_page_config(page_title="Legal_AI: 문서 자동화", layout="wide")

# [최종 종결] 보안키를 직접 입력하지 않고 시스템 인증을 사용합니다.
def get_google_client():
    try:
        # 1. 시스템에 설정된 기본 인증 정보를 사용하여 클라이언트를 생성합니다.
        # (이것은 Google Cloud 환경에서 가장 에러 없이 작동하는 표준 방식입니다.)
        return vision.ImageAnnotatorClient()
    except Exception as e:
        st.error(f"❌ 인증 시스템 연결 실패: {e}")
        st.info("💡 Github의 Settings > Secrets에 키가 올바르게 등록되었는지 확인이 필요할 수 있습니다.")
        return None

client = get_google_client()

st.markdown("<h2 style='text-align: center; color: #2c3e50;'>⚖️ Legal_AI: 서비스 준비 완료</h2>", unsafe_allow_html=True)

if client:
    # 성공하면 바로 업로드 칸을 보여줍니다.
    uploaded_file = st.file_uploader("법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])
    
    if uploaded_file:
        with st.spinner('AI가 서류를 정밀 분석 중입니다...'):
            try:
                full_text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        full_text += client.document_text_detection(image=vision.Image(content=pix.tobytes("png"))).full_text_annotation.text + "\n"
                else:
                    full_text = client.document_text_detection(image=vision.Image(content=uploaded_file.getvalue())).full_text_annotation.text
                
                st.success("✅ 분석 완료!")
                st.text_area("인식된 텍스트 결과 (복사 가능)", full_text, height=450)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
else:
    st.warning("⚠️ 인증 정보가 설정되지 않았습니다. 관리자 설정을 확인해주세요.")
    st.stop()
