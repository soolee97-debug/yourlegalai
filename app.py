import streamlit as st
import os
import re
import pandas as pd
from datetime import datetime
from google.cloud import vision
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
import json
from google.oauth2 import service_account
import fitz  # PyMuPDF: PDF 처리용

st.set_page_config(page_title="Legal_AI: 문서 자동화", layout="wide")

# 1. 환경 설정 및 인증 (클라우드 보안 모드)
try:
    key_dict = json.loads(st.secrets["google_key"])
    credentials = service_account.Credentials.from_service_account_info(key_dict)
    client = vision.ImageAnnotatorClient(credentials=credentials)
except Exception as e:
    st.error("보안 키가 설정되지 않았습니다.")
    st.stop()

# --- 이하 로직 동일하되 PDF 지원 추가 ---

st.markdown("<h1 style='color: #2c3e50;'>⚖️ Legal_AI: PDF 등기부 통합 분석</h1>", unsafe_allow_html=True)

# 워드 생성 함수 (동일)
def create_minutes_docx(company_name, name, title, action_type, deadline_date):
    doc = Document()
    heading = doc.add_heading('임 시 주 주 총 회 의 사 록', 0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"1. 일  시 : {deadline_date}  오전 10시 00분")
    doc.add_paragraph(f"2. 장  소 : {company_name} 본점 회의실")
    doc.add_paragraph(f"3. 발행주식의 총수 :               주 (의결권 있는 주식수 :               주)")
    doc.add_paragraph(f"4. 출석주주 수 :               명\n5. 출석주주의 주식수 :               주")
    doc.add_paragraph(f"\n제 1 호 의안 : {title} 선임의 건")
    if action_type == "교체":
        doc.add_paragraph(f"기존 {title} {name}의 임기가 만료됨에 따라 신규 선임하기로 결의하다.")
    else:
        doc.add_paragraph(f"{title} {name}의 임기 만료에 따라 중임(재선임)하기로 결의하다.")
    doc.add_paragraph(f"\n202X년 XX월 XX일\n{company_name} 의장 대표이사 (인)")
    output = BytesIO()
    doc.save(output)
    return output.getvalue()

# 임기 계산 로직 (동일)
def get_actionable_dates_enterprise(first_appt_str, latest_appt_str, title, term_years, is_listed):
    try:
        nums_first = re.findall(r'\d+', first_appt_str)
        nums_latest = re.findall(r'\d+', latest_appt_str)
        first_date = datetime(int(nums_first[0]), int(nums_first[1]), int(nums_first[2]))
        latest_date = datetime(int(nums_latest[0]), int(nums_latest[1]), int(nums_latest[2]))
        base_expiry = latest_date.replace(year=latest_date.year + term_years)
        expiry_str = base_expiry.strftime('%Y-%m-%d')
        action_type = "중임/선임"
        if is_listed and "사외이사" in title:
            max_limit_date = first_date.replace(year=first_date.year + 6)
            if base_expiry >= max_limit_date:
                action_type = "교체"
                return f"{max_limit_date.strftime('%Y-%m-%d')}", f"🚨 무조건 교체", action_type
        return expiry_str, f"{expiry_str} 이전", action_type
    except: return None, None, "오류"

# 메인 UI
with st.sidebar:
    st.header("⚙️ 설정")
    company_name_manual = st.text_input("회사명 수동 입력")
    is_listed = st.checkbox("📈 상장회사 여부", value=False)
    term_setting = st.radio("이사 임기", [2, 3], index=1)

uploaded_file = st.file_uploader("법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])

if uploaded_file:
    full_text = ""
    with st.spinner('문서 전체를 스캔하고 있습니다...'):
        if uploaded_file.type == "application/pdf":
            # PDF 각 페이지를 이미지로 변환하여 AI에게 전달
            pdf_data = uploaded_file.read()
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            for page in doc:
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                image = vision.Image(content=img_bytes)
                response = client.document_text_detection(image=image)
                full_text += response.full_text_annotation.text + "\n"
        else:
            image = vision.Image(content=uploaded_file.getvalue())
            response = client.document_text_detection(image=image)
            full_text = response.full_text_annotation.text

        # 회사명 추출 (1페이지에 보통 있음)
        company_match = re.search(r"상\s*호\s*([가-힣A-Za-z\(\)\s]+?)(?=\n|본|지)", full_text)
        final_company_name = company_name_manual if company_name_manual else (company_match.group(1).strip() if company_match else "회사명 미인식")
        
        st.success(f"🏢 분석 대상: {final_company_name}")

        # 임원 데이터 파싱 및 UI 출력
        parts = re.split(r"(사내이사|대표이사|감사위원|감사|사외이사|기타비상무이사)", full_text)
        blocks = [(parts[i], parts[i+1]) for i in range(1, len(parts)-1, 2)]
        
        registry_db = {}
        for title, content_text in blocks:
            if "사임" in content_text or "퇴임" in content_text: continue
            name_match = re.search(r"^\s*([가-힣A-Za-z\(\)\s,\-]+?)(?:\d{6}-|\d{4}\s*년)", content_text)
            if name_match:
                name = re.sub(r"^[-*.\s]+", "", name_match.group(1)).strip()
                dates = re.findall(r"(\d{4}\s*년\s*\d{1,2}\s*월\s*\d{1,2}\s*일)\s*(?:취임|중임)", content_text)
                if dates:
                    expiry, deadline, a_type = get_actionable_dates_enterprise(dates[0], dates[-1], title, term_setting, is_listed)
                    
                    # 중복 제거 및 리스트업
                    if f"{title}_{name}" not in registry_db:
                        registry_db[f"{title}_{name}"] = True
                        col_i, col_b = st.columns([3, 1])
                        with col_i:
                            st.info(f"👤 **{title} {name}** | 만료일: {expiry} | **{deadline}**")
                        with col_b:
                            doc_bytes = create_minutes_docx(final_company_name, name, title, a_type, deadline)
                            st.download_button("📄 워드 생성", doc_bytes, f"{name}_의사록.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
