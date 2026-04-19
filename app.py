import streamlit as st
import os, json
from google.cloud import vision
from google.oauth2 import service_account
import fitz # PyMuPDF

st.set_page_config(page_title="Legal_AI: 문서 자동화", layout="wide")

def get_google_client():
    try:
        # 1. 파일 경로를 더 정확하게 잡습니다.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        key_path = os.path.join(current_dir, "key.json")
        
        # 만약 파일이 없으면 에러 메시지를 구체적으로 띄웁니다.
        if not os.path.exists(key_path):
            st.error(f"❌ 'key.json' 파일을 찾을 수 없습니다. (현재 경로: {current_dir})")
            st.info("💡 Github 메인 화면에서 [Add file] -> [Upload files]로 'key.json'을 꼭 올려주세요!")
            return None
            
        # 2. 파일로 인증 객체 생성
        creds = service_account.Credentials.from_service_account_file(key_path)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"❌ 인증 실패: {e}")
        return None

client = get_google_client()

st.markdown("<h2 style='text-align: center;'>⚖️ Legal_AI: 서비스 준비 완료</h2>", unsafe_allow_html=True)

if client:
    # 성공하면 바로 업로드 칸을 보여줍니다.
    uploaded_file = st.file_uploader("법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])
    
    if uploaded_file:
        with st.spinner('AI가 서류를 분석하고 있습니다...'):
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
                st.text_area("결과 텍스트", full_text, height=400)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
else:
    st.warning("⚠️ 왼쪽 사이드바나 Github 설정을 통해 보안키(key.json)를 먼저 활성화해주세요.")
    st.stop()
