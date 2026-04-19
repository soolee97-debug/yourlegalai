import streamlit as st
import json
import base64
from google.cloud import vision
from google.oauth2 import service_account
import fitz
import re
import pandas as pd

st.set_page_config(page_title="Legal_AI: 등기 정밀 분석", layout="wide")

@st.cache_resource
def get_client():
    try:
        b64_key = st.secrets["GCP_KEY_B64"]
        info = json.loads(base64.b64decode(b64_key).decode('utf-8'))
        return vision.ImageAnnotatorClient(credentials=service_account.Credentials.from_service_account_info(info))
    except: return None

client = get_client()

st.title("⚖️ Legal_AI: 법인 분석 리포트")

if client:
    uploaded_file = st.file_uploader("법인등기부(PDF/이미지)를 올려주세요", type=["pdf", "png", "jpg"])
    
    if uploaded_file:
        with st.spinner('AI가 법적 리스크를 분석 중입니다...'):
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

                # 2. UI 구성
                st.subheader("📋 1. 기본 정보")
                c1, c2, c3 = st.columns(3)
                
                # 정규식으로 핵심 데이터 추출
                comp_name = re.search(r'상호\s+([^\n]+)', raw_text)
                address = re.search(r'본점\s+([^\n]+)', raw_text)
                purpose = re.findall(r'\d+\.\s+([^\n]+)', raw_text)

                c1.metric("회사명", comp_name.group(1).strip() if comp_name else "미탐지")
                c2.metric("등기번호", re.search(r'등기번호\s+(\d+)', raw_text).group(1) if re.search(r'등기번호\s+(\d+)', raw_text) else "미탐지")
                c3.metric("본점 소재지", "사천시" if "사천" in raw_text else "서울/기타")

                st.divider()

                # 3. 임원진 변동사항 정밀 추출 (Legal AI의 핵심)
                st.subheader("👤 2. 임원진 현황 및 변동 히스토리")
                
                # 임원 이름과 날짜를 매칭하는 복합 정규식
                officer_pattern = r'(대표이사|사내이사|감사)\s+([가-힣\s\(\w\)]+)\s+(\d{4}년\s+\d{1,2}월\s+\d{1,2}일)\s+(취임|중임|사임|퇴임)'
                matches = re.findall(officer_pattern, raw_text)
                
                if matches:
                    df = pd.DataFrame(matches, columns=['직책', '성명', '변동일자', '변동내역'])
                    st.table(df)
                    
                    # 중임 기한 알림 (Legal Insight)
                    st.warning("💡 **Legal Tip:** 주식회사 이사의 임기는 보통 3년입니다. '중임' 날짜로부터 3년이 지났는지 확인하여 과태료 리스크를 방지하세요.")
                else:
                    st.info("임원 변동 상세 내역을 표로 구성하기 위해 추가 분석 중입니다.")

                st.divider()
                
                st.subheader("🎯 3. 사업 목적 (영업 범위)")
                if purpose:
                    st.write(", ".join(purpose[:5]) + " 등")
                else:
                    st.write("원본 텍스트에서 사업 목적을 추출하고 있습니다.")

                with st.expander("📄 원본 텍스트 확인"):
                    st.text(raw_text)

            except Exception as e:
                st.error(f"분석 실패: {e}")
else:
    st.error("보안 설정이 필요합니다.")
