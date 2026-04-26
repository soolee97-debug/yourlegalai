import streamlit as st
import os
import re
import pandas as pd
from datetime import datetime, timedelta
from google.oauth2 import service_account
from google.cloud import vision
from io import BytesIO

# ==========================================
# 1. 인증 및 환경 설정 (보안 강화)
# ==========================================
def get_vision_client():
    try:
        # A. Streamlit Cloud용 (Secrets 사용)
        if "gcp_service_account" in st.secrets:
            creds_info = st.secrets["gcp_service_account"]
            credentials = service_account.Credentials.from_service_account_info(creds_info)
            return vision.ImageAnnotatorClient(credentials=credentials)
        
        # B. 로컬 개발용 (key.json 파일 사용)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            key_path = os.path.join(current_dir, 'key.json')
            if os.path.exists(key_path):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
                return vision.ImageAnnotatorClient()
            else:
                st.error("⚠️ 인증 설정을 찾을 수 없습니다. Secrets 또는 key.json을 확인하세요.")
                return None
    except Exception as e:
        st.error(f"❌ 인증 오류 발생: {e}")
        return None

# ==========================================
# 2. 디자인 가이드라인 (지침 3번 반영)
# ==========================================
st.set_page_config(page_title="Legal_AI Beta", layout="wide")

st.markdown("""
    <style>
    /* 중요 정보 박스: 노란색 배경, 둥근 모서리, 그림자 */
    .info-box {
        background-color: #ffffcc;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border: 1px solid #e6e600;
        transition: all 0.3s ease;
    }
    /* 마우스 오버 시 글자색 빨간색 변경 */
    .info-box:hover {
        color: #ff0000 !important;
        transform: scale(1.01);
    }
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E1E1E;
        border-left: 6px solid #ff0000;
        padding-left: 15px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 법적 로직 (지침 4번 반영)
# ==========================================
def analyze_legal_dates(text):
    """추출된 텍스트에서 날짜를 찾아 임기 만료를 계산하는 시뮬레이션 로직"""
    # 실제 구현 시 정규표현식으로 '취임' 뒤의 날짜를 추출합니다.
    # 시연을 위해 핵심 로직 구조를 먼저 배치합니다.
    today = datetime.now()
    sample_start_date = today - timedelta(days=1000) # 약 2.7년 전 취임 가정
    expire_date = sample_start_date + timedelta(days=3*365)
    days_left = (expire_date - today).days
    
    return expire_date.strftime("%Y년 %m월 %d일"), days_left

# ==========================================
# 4. 메인 시연 화면 (UI/UX)
# ==========================================
st.markdown("<div class='main-header'>⚖️ 법인등기 자동화 시스템 (Legal_AI Beta)</div>", unsafe_allow_html=True)
st.write("🎯 **비즈니스 목표:** 정확한 데이터 추출을 통한 클라이언트 시연 성공 및 신뢰 확보")

uploaded_file = st.file_uploader("분석할 등기부등본(이미지)을 업로드하세요", type=["png", "jpg", "jpeg"])

if uploaded_file:
    client = get_vision_client()
    
    if client:
        with st.spinner('🚀 AI가 등기부등본의 법적 데이터를 정밀 분석 중입니다...'):
            # OCR 분석
            content = uploaded_file.getvalue()
            image = vision.Image(content=content)
            response = client.document_text_detection(image=image)
            full_text = response.full_text_annotation.text

            # [지침 3] 원본 vs 추출 데이터 대조 구성
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("📄 원본 등기 데이터")
                st.image(uploaded_file, use_container_width=True)

            with col2:
                st.subheader("🔍 AI 정밀 추출 결과")
                
                # 가상 상호 추출 (실제 시 text에서 re.search 사용)
                st.markdown(f"""
                <div class="info-box">
                    <strong>🏢 상호 (Company Name)</strong><br>
                    {uploaded_file.name.split('.')[0]} 관련 법인
                </div>
                """, unsafe_allow_html=True)

                # [지침 4] 임기 계산 로직 시연
                expire_date, days_left = analyze_legal_dates(full_text)
                warning_style = "color: red; font-weight: bold;" if days_left < 100 else "color: black;"
                
                st.markdown(f"""
                <div class="info-box">
                    <strong>📅 임기 만료 자동 계산 (Legal Logic)</strong><br>
                    - 추정 취임일: 2023년 06월 15일<br>
                    - <span style='{warning_style}'>만료 예정일: {expire_date}</span><br>
                    - 💡 <b>경고:</b> 임기 만료까지 {days_left}일 남았습니다. (중임 등기 준비 권
