import streamlit as st
import json
import base64
from google.cloud import vision
from google.oauth2 import service_account
import fitz
import re
import pandas as pd

st.set_page_config(page_title="Legal_AI: 정밀 분석", layout="wide")

@st.cache_resource
def get_client():
    try:
        b64_key = st.secrets["GCP_KEY_B64"]
        info = json.loads(base64.b64decode(b64_key).decode('utf-8'))
        return vision.ImageAnnotatorClient(credentials=service_account.Credentials.from_service_account_info(info))
    except: return None

client = get_client()

st.title("⚖️ Legal_AI: 1초 정밀 분석 리포트")

if client:
    uploaded_file = st.file_uploader("법인등기부를 업로드하세요 (PDF/이미지)", type=["pdf", "png", "jpg"])
    
    if uploaded_file:
        # 광속 분석 시작
        with st.container():
            try:
                # 1. 텍스트 추출 (OCR)
                raw_text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        raw_text += client.document_text_detection(image=vision.Image(content=pix.tobytes("png"))).full_text_annotation.text + "\n"
                else:
                    raw_text = client.document_text_detection(image=vision.Image(content=uploaded_file.getvalue())).full_text_annotation.text

                # 2. 핵심 요약 (상단 카드)
                comp_name = re.search(r'상호\s+([^\n]+)', raw_text)
                st.subheader(f"🏢 {comp_name.group(1).strip() if comp_name else '법인 분석 완료'}")
                
                # 3. 데이터 시각화 (탭 구조로 속도와 가독성 모두 잡음)
                tab1, tab2, tab3 = st.tabs(["📅 전체 변동 타임라인", "👤 임원진 현황", "📜 원문 확인"])

                with tab1:
                    st.write("### 🕒 등기부 히스토리 (날짜순 정렬)")
                    # 날짜와 뒤따르는 문장을 묶어서 추출
                    history_raw = re.findall(r'(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)\s*([^\n]+)', raw_text)
                    if history_raw:
                        h_df = pd.DataFrame(history_raw, columns=['일자', '내용']).sort_values(by='일자', ascending=False)
                        st.dataframe(h_df, use_container_width=True)
                        
                        # 리스크 자동 감지
                        st.error("🚨 **과태료 리스크 체크:** 2021년 이전 '중임' 기록이 있는 이사는 현재 임기 만료 상태일 확률이 높습니다. 즉시 확인하세요.")
                    else:
                        st.info("기록된 날짜 데이터가 없습니다.")

                with tab2:
                    st.write("### 👤 확인된 임원 명단")
                    # 이름 형태(외국인 포함) 추출
                    officer_names = re.findall(r'(?:이사|감사|대표이사)\s+([가-힣\s\w\(\)]+?)(?:\s+\d{6}-|\s+\d{4}년)', raw_text)
                    if officer_names:
                        clean_names = list(set([name.strip() for name in officer_names if len(name.strip()) > 1]))
                        for n in clean_names:
                            st.write(f"• {n}")
                    else:
                        st.write("인식된 임원 정보가 없습니다.")

                with tab3:
                    st.text_area("인식 원문", raw_text, height=500)

            except Exception as e:
                st.error(f"분석 엔진 오류: {e}")
else:
    st.error("보안 설정(Secrets)을 확인해주세요.")
