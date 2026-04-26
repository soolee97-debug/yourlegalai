import streamlit as st
import json
import base64
from google.cloud import vision
from google.oauth2 import service_account
import fitz
import google.generativeai as genai
import os

# 1. [보안] 로컬의 key.json 대신 금고(Secrets)에서 키를 가져와 환경변수를 설정합니다.
# 1. [보안] 로컬의 key.json 대신 금고(Secrets)에서 키를 가져와 환경변수를 설정합니다.
# 1. [보안] 로컬의 key.json 대신 금고(Secrets)에서 키를 가져와 환경변수를 설정합니다.
# 1. [보안] 오류를 일으키는 Base64를 버리고, 순수 JSON을 직접 읽어옵니다!
def setup_auth():
    try:
        # GCP_JSON 이라는 이름의 순수 텍스트 데이터를 가져옵니다.
        raw_json = st.secrets["GCP_JSON"]
        info = json.loads(raw_json, strict=False)
        
        # 줄바꿈 기호(\n)만 정상적으로 작동하도록 펴줍니다.
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
            
        return service_account.Credentials.from_service_account_info(info)
        
    except Exception as e:
        st.error(f"🚨 디버깅 모드: {e}")
        return None
# 2. Gemini 지능 연결 (상업화의 핵심)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# 'models/'를 빼고, 뒤에 버전을 붙여줍니다.
model = genai.GenerativeModel('gemini-1.5-flash-001')

st.set_page_config(page_title="Legal_AI: 상업용 통합 버전", layout="wide")

st.title("⚖️ Legal_AI: 통합 정밀 분석 리포트")

creds = setup_auth()

if creds:
    client = vision.ImageAnnotatorClient(credentials=creds)
    uploaded_file = st.file_uploader("법인등기부(PDF/이미지) 업로드", type=["pdf", "png", "jpg"])
    
    if uploaded_file:
        with st.spinner('대표님의 main.py 엔진과 Gemini 지능을 가동 중입니다...'):
            try:
                # [OCR 단계] 대표님의 main.py 로직 적용
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

                # [지능 분석 단계] 대표님이 화내셨던 "구분 못 하는 문제"를 해결합니다.
                prompt = f"""
                당신은 대한민국 법인 등기 전문가입니다. 
                아래 텍스트에서 '설립 등기일'과 '임원 생년월일'을 완벽하게 구분하여 보고서를 작성하세요.
                내용이 없으면 "데이터 없음"이라고 명시하세요.
                
                [분석 대상]
                {raw_text}
                
                [양식]
                1. 법인 기본 정보 (상호, 설립년월일, 본점주소)
                2. 임원진 명단 및 임기 현황 (생년월일 별도 표기)
                3. 주요 법적 변동 사항 및 리스크 진단
                """
                response = model.generate_content(prompt)

                # [출력]
                st.success("✅ 상업화 등급의 정밀 분석이 완료되었습니다.")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"분석 실패: {e}")
else:
    st.error("GCP_KEY_B64 보안 설정이 필요합니다.")
