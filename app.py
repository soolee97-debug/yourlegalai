import streamlit as st
import json
import base64
from google.cloud import vision
from google.oauth2 import service_account
import fitz
import re
import pandas as pd

st.set_page_config(page_title="Legal_AI: 정밀 분석", layout="wide", page_icon="⚖️")

@st.cache_resource
def get_client():
    try:
        b64_key = st.secrets["GCP_KEY_B64"]
        info = json.loads(base64.b64decode(b64_key).decode('utf-8'))
        return vision.ImageAnnotatorClient(credentials=service_account.Credentials.from_service_account_info(info))
    except: return None

client = get_client()

# --- 깔끔한 UI 디자인 ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Legal_AI: 1초 정밀 분석 리포트")
st.caption("법인등기부의 핵심 데이터를 분석하여 법적 리스크를 진단합니다.")

if client:
    uploaded_file = st.file_uploader("법인등기부를 업로드하세요 (PDF/이미지)", type=["pdf", "png", "jpg"])
    
    if uploaded_file:
        with st.spinner('데이터를 정밀 분석 중입니다...'):
            try:
                # 1. OCR 텍스트 추출
                raw_text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        raw_text += client.document_text_detection(image=vision.Image(content=pix.tobytes("png"))).full_text_annotation.text + "\n"
                else:
                    raw_text = client.document_text_detection(image=vision.Image(content=uploaded_file.getvalue())).full_text_annotation.text

                # 2. 정보 정제 로직
                comp_name = re.search(r'상호\s+([^\n]+)', raw_text)
                title = comp_name.group(1).strip() if comp_name else "법인 분석 리포트"
                
                # 3. 레이아웃 구성
                st.header(f"🏢 {title}")
                
                tab1, tab2, tab3 = st.tabs(["📊 핵심 요약", "⏳ 변동 타임라인", "📝 원문 데이터"])

                with tab1:
                    st.subheader("💡 법인 요약 정보")
                    c1, c2, c3 = st.columns(3)
                    
                    # 자본금 추출 시도
                    capital = re.search(r'자본금의 액\s+금\s*([\d,]+)', raw_text)
                    c1.metric("추정 자본금", capital.group(1) + "원" if capital else "별도 확인")
                    c2.metric("등기 상태", "정상 (살아있는 법인)" if "말소" not in raw_text else "말소 사항 포함")
                    c3.metric("본점 소재지", "사천/기타" if "사천" in raw_text else "서울/기타")

                    st.subheader("🚨 리스크 자가진단")
                    # 날짜 기반 리스크 분석
                    expired_directors = re.findall(r'(\d{4}년\s+\d{1,2}월\s+\d{1,2}일)\s+(?:중임|취임)', raw_text)
                    if expired_directors:
                        latest_date = max(expired_directors)
                        if int(latest_date[:4]) <= 2021:
                            st.error(f"⚠️ **임기 만료 주의:** 마지막 중임일이 {latest_date}입니다. 3년 임기 만료에 따른 등기 여부를 즉시 확인하세요!")
                        else:
                            st.success(f"✅ **임원 임기 양호:** 최근 {latest_date}에 등기가 확인되었습니다.")

                with tab2:
                    st.subheader("📅 변동 사항 히스토리 (최신순)")
                    history = re.findall(r'(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)\s*([^\n]+)', raw_text)
                    if history:
                        h_df = pd.DataFrame(history, columns=['일자', '내용']).sort_values(by='일자', ascending=False)
                        st.table(h_df.head(15)) # 상위 15개만 깔끔하게
                    else:
                        st.info("기록된 날짜 데이터가 없습니다.")

                with tab3:
                    st.text_area("인식된 원문 전체", raw_text, height=600)

            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
else:
    st.error("보안 설정이 필요합니다.")
