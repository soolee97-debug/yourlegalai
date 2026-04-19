import streamlit as st
import os, re, json
from datetime import datetime
from google.cloud import vision
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from google.oauth2 import service_account
import fitz # PyMuPDF

st.set_page_config(page_title="Legal_AI: 문서 자동화", layout="wide")

# [최종] 줄바꿈 문제를 해결한 키 데이터
raw_private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDUCS2AOnLmvW7J\ncdHkPMr/R/ofYyezVVDFECKFFlNAkE5djYwZZarSMlBALsMU8/AGFSSh9IXXCyQV\n6HcUraznulFAqBNLKFGcACcfukoSJhg1wjv9A9D3XBfzz6WDQdBgyrMo6WemoEkK\na92GU7vOPYqBkI+W3uq1CJidTPFswHwhykIJN0TnxnCU7uqx1eyW9akV+MBXJmHR\nNwZUEiOqWrBPyU2YcG75iHraH24MnBT2V/s++t0HmoZu+glrijLd+rLC3t52zN8d\nxR4XWeopIW+Rejatu9lE8OtfnIIIMo1K21glglOwZMhXBHBQvLU72qi8bFsvJQ9W\nS6sos68xAgMBAAECggEAG1SphEdEa0CMqLOeoeRCKECfWW9e/Ssok5YeVPhJN9/B\n8iYeImHr8Fci5/r/E1LUI/ySsbuCivL5Lke+HbC7Qk1OTt67SetDBbAxWtIY3RkC\n8t77+4OD6nZ48ejYhUA0+1z1Vfcr8Jrlf03jCn79jLp7AXNgRsqqBza58UCrN+Cl\ndabXCY9FpGeMPLadIA5DRQ9nFp5NHhR8jCCWOb/6HkfIJyS/lvZ6f74kecwEte+x\nxer/maPsq4JBBix4bJ3xRAw1NxhM11cds0T29BxkF8dZmax4gI76z0I2GaWD4nL5\n8snLTzNWbGfbW6li1s4YROw4jqt6JuCNRH/4ZKjRzwKBgQD+FfR72rB387gTBTaQ\nyTt5hjHmZB1mQU/oT1kqAuTuLAW4OnBPWkCmlWuaR8sak9dJrPnuCKTNhV+i1o9s\awRyVvCDYnpFHv/3MeTabvJDUprCBzhJfdLAVGff6iS7jlnnvbOwqJ/4MSocRLsV\SxLPFbdghcOINgpQZj2YxwyFXwKBgQDVoh9snm7SyBu9oos/U33oWbvFTOJvorjF\npQvl6dx+/XLSQ+YZuRX213a9VDRmUp4qC97kW220P2zkGPweckpy9m0L7QWkCUwM\ncTJ1mQ9pvQLbBuJLV+X3AZDl4ptxcRPGRceZo4DVLbskNt9J5OQY4PPDxQPtAmMA\n2WE3YTUFbwKBgQDOG60o0usXQqJs+2uZ40LVf1/3DfszOY6CZTllgteFxDwXh4AX\nPpT3DHouulItCwQ2hZRv3J8jAC/l/bp2LhF7Vr7fNQEOFOl58gU8k4b9yYI0Jnso\nUmKlFVL1tg95/S086QtcIE0znV4VdEN2MGHfjjQknh1Q3tVbBrSsu7qSbQKBgQCA\nvkYfyE7TOgL1wmoWTLOY/dLZ8R6Y1kBx46gK82eNJCI5MvANWmwxKOIG8SLu8yUc\nA7Fcfvja4ko2IBR4KLpTE8zdngaDN5McAG+/TPFr8Jsy8bAYZa1RsSDoWSsCL3oS\nR+Uk4tL2JawdA/CGcKlBkPd2aFmYUJLnZRlgLXWtgwKBgDh1UoYHytr52ps9leho\nfYwAvZVXGd0Hqv4sdi+YWzGcQKJ30sgHfQUOxNgMo1/AVVdm+xn+svIk18nVvfjl\nmDGCxBIQg27tEfZasOVwQlkUwULvN9UXYNgPPc28E/krhVVdWt2foy6J0iNye97N\n9r7OovQdTCBfT0srvINlQpEk\n-----END PRIVATE KEY-----\n"

KEY_DATA = {
  "type": "service_account",
  "project_id": "formal-facet-469109-n9",
  "private_key_id": "a75d5c613386e549458b7f9ce7429053fa690601",
  "private_key": raw_private_key.replace("\\n", "\n"), # 줄바꿈 기호를 진짜 줄바꿈으로 변경
  "client_email": "97202050044-compute@developer.gserviceaccount.com",
  "client_id": "106591061735155848403",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/97202050044-compute%40developer.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

def get_google_client():
    try:
        credentials = service_account.Credentials.from_service_account_info(KEY_DATA)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        st.error(f"❌ 구글 인증 최종 실패: {e}")
        return None

client = get_google_client()

st.markdown("<h1 style='color: #2c3e50;'>⚖️ Legal_AI: PDF 등기부 통합 분석</h1>", unsafe_allow_html=True)

if client:
    uploaded_file = st.file_uploader("법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])
    if uploaded_file:
        with st.spinner('문서 분석 중...'):
            try:
                full_text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        image = vision.Image(content=pix.tobytes("png"))
                        full_text += client.document_text_detection(image=image).full_text_annotation.text + "\n"
                else:
                    image = vision.Image(content=uploaded_file.getvalue())
                    full_text = client.document_text_detection(image=image).full_text_annotation.text
                
                st.success("✅ 분석 완료!")
                st.text_area("인식된 전체 텍스트", full_text, height=300)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
else:
    st.stop()
