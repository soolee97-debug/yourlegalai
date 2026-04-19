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

st.title("⚖️ Legal_AI: 법률 문서 분류 엔진")

if client:
    uploaded_file = st.file_uploader("법인등기부를 업로드하세요", type=["pdf", "png", "jpg"])
    
    if uploaded_file:
        with st.spinner('데이터의 문맥을 분석 중입니다...'):
            try:
                # 1. 텍스트 추출
                raw_text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        raw_text += client.document_text_detection(image=vision.Image(content=pix.tobytes("png"))).full_text_annotation.text + "\n"
                else:
                    raw_text = client.document_text_detection(image=vision.Image(content=uploaded_file.getvalue())).full_text_annotation.text

                # 2. 지능형 분류 로직 (문맥 기반)
                lines = raw_text.split('\n')
                
                birth_dates = [] # 이사 생일
                reg_dates = []   # 등기 관련 날짜
                founding_date = "미탐지" # 설립일
                
                for line in lines:
                    date_match = re.search(r'(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)', line)
                    if date_match:
                        dt = date_match.group(1)
                        # (1) 생년월일 판별: "생" 혹은 주민번호 앞자리가 근처에 있는가?
                        if "생" in line or re.search(r'\d{6}-', line):
                            birth_dates.append({"항목": "임원 생년월일", "날짜": dt, "내용": line.strip()})
                        # (2) 설립일 판별: "설립" 단어가 포함되어 있는가?
                        elif "설립" in line:
                            founding_date = dt
                        # (3) 그 외는 등기 변동일
                        else:
                            reg_dates.append({"일자": dt, "변동내용": line.replace(dt, "").strip()})

                # 3. 결과 출력 (UI 개선)
                st.subheader("🏢 법인 기본 분석")
                c1, c2 = st.columns(2)
                c1.metric("최초 설립 등기일", founding_date)
                c2.metric("분석된 임원 수", f"{len(list(set([d['내용'][:5] for d in birth_dates])))}명")

                st.divider()

                tab1, tab2, tab3 = st.tabs(["⏳ 등기 변동 히스토리", "👤 임원 인적사항", "📜 전체 원문"])

                with tab1:
                    st.write("### 📅 주요 등기 일정")
                    if reg_dates:
                        st.table(pd.DataFrame(reg_dates).drop_duplicates().sort_values("일자", ascending=False))
                    else:
                        st.write("검출된 등기 내역이 없습니다.")

                with tab2:
                    st.write("### 🎂 임원 생년월일 데이터")
                    st.caption("AI가 주민번호 및 '생' 키워드로 분류한 정보입니다.")
                    if birth_dates:
                        st.dataframe(pd.DataFrame(birth_dates), use_container_width=True)
                    else:
                        st.write("인식된 생년월일 정보가 없습니다.")

                with tab3:
                    st.text_area("OCR Raw Data", raw_text, height=500)

            except Exception as e:
                st.error(f"분석 엔진 오류: {e}")
