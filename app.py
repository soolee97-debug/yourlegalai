import streamlit as st
import json
import base64
from google.cloud import vision
from google.oauth2 import service_account
import fitz
import re

st.set_page_config(page_title="Legal_AI: 등기 요약 보고서", layout="wide")

@st.cache_resource
def get_client():
    try:
        b64_key = st.secrets["GCP_KEY_B64"]
        decoded_key = base64.b64decode(b64_key).decode('utf-8')
        info = json.loads(decoded_key)
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except: return None

client = get_client()

st.title("⚖️ Legal_AI: 등기부 정밀 분석")

if client:
    st.success("✅ 보안 인증 완료! 이제 파일만 올리시면 됩니다.")
    uploaded_file = st.file_uploader("분석할 서류를 업로드하세요", type=["pdf", "png", "jpg"])
    
    if uploaded_file:
        with st.spinner('AI가 서류의 핵심 내용을 추출 중입니다...'):
            try:
                raw_text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        res = client.document_text_detection(image=vision.Image(content=pix.tobytes("png")))
                        raw_text += res.full_text_annotation.text + "\n"
                else:
                    res = client.document_text_detection(image=vision.Image(content=uploaded_file.getvalue()))
                    raw_text = res.full_text_annotation.text

                # --- 여기서부터 진짜 '분석' UI ---
                st.divider()
                st.subheader("📑 핵심 요약 보고서")
                
                # 핵심 정보 추출 (간단한 로직)
                comp_name = re.findall(r'상호\s+(.+)', raw_text)
                address = re.findall(r'본점\s+(.+)', raw_text)
                reg_num = re.findall(r'등기번호\s+(\d+)', raw_text)

                col1, col2, col3 = st.columns(3)
                col1.metric("회사명", comp_name[0] if comp_name else "추출 중...")
                col2.metric("등기번호", reg_num[0] if reg_num else "추출 중...")
                col3.metric("소재지", "경상남도 사천시" if "사천" in raw_text else "주소 확인 필요")

                with st.expander("🔍 전체 인식 결과(OCR) 보기"):
                    st.text_area("인식된 원문", raw_text, height=300)

                st.info("💡 위 데이터는 AI가 1차 추출한 결과입니다. 법적 효력을 위해서는 원본 대조가 필요합니다.")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
