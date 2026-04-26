import streamlit as st
import google.cloud.vision as vision
import google.generativeai as genai
import json
import os
from google.oauth2 import service_account

# 1. 환경 설정 및 인증 (Secrets 활용)
# GCP_JSON 세팅
gcp_info = json.loads(st.secrets["GCP_JSON"])
credentials = service_account.Credentials.from_service_account_info(gcp_info)
vision_client = vision.ImageAnnotatorClient(credentials=credentials)

# Gemini API 세팅
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# [중요] 가장 오류가 적은 모델 설정 방식
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text_from_image(image_content):
    """구글 비전 API를 사용하여 이미지에서 텍스트 추출"""
    image = vision.Image(content=image_content)
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description
    return ""

# --- 스트림릿 UI 시작 ---
st.set_page_config(page_title="Legal_AI 법인분석", layout="wide")
st.title("⚖️ Legal_AI: 법인등기부 정밀 분석")
st.write("법인등기부 이미지 또는 PDF를 업로드하면 인공지능이 핵심 내용을 분석합니다.")

uploaded_file = st.file_uploader("법인등기부(PDF/이미지) 업로드", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file is not None:
    st.success("파일이 업로드되었습니다!")
    
    if st.button("🔍 통합 정밀 분석 시작"):
        with st.spinner("AI가 등기부를 정밀 분석 중입니다..."):
            try:
                # 1. 텍스트 추출 (OCR)
                file_bytes = uploaded_file.read()
                extracted_text = extract_text_from_image(file_bytes)
                
                if not extracted_text:
                    st.error("텍스트를 추출할 수 없습니다. 이미지 화질을 확인해주세요.")
                else:
                    # 2. Gemini 분석 리포트 생성
                    prompt = f"""
                    당신은 대한민국 법인 등기 전문가입니다. 
                    아래의 등기부 등본 텍스트를 분석하여 '상업용 분석 리포트'를 작성하세요.
                    
                    [등기부 텍스트]
                    {extracted_text}
                    
                    [포함할 내용]
                    1. 회사의 기본 정보 (상호, 본점 주소, 자본금)
                    2. 임원 현황 및 임기 만료 예정일 (가장 중요)
                    3. 목적 사업 분석
                    4. 법률적 특이사항 또는 주의사항
                    
                    정중하고 전문적인 말투로 작성해 주세요.
                    """
                    
                    # 분석 실행
                    response = model.generate_content(prompt)
                    
                    st.divider()
                    st.subheader("📋 법인 분석 결과 리포트")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"분석 실패: {str(e)}")
                st.info("Tip: 404 에러가 지속되면 모델명을 'gemini-1.5-flash-latest'로 변경해 보세요.")

st.sidebar.info("v1.2 - Project ID: formal-facet-469109-n9")
