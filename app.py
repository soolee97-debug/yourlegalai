import streamlit as st
import json
from google.cloud import vision
from google.oauth2 import service_account
import fitz  # PyMuPDF

st.set_page_config(page_title="Legal_AI: 문서 자동화", layout="wide")

# [완전 종결] 어떤 오차도 허용하지 않는 강제 인증 방식
def get_final_client():
    try:
        # 키의 몸통입니다. (복사 에러를 막기 위해 아주 튼튼하게 짰습니다.)
        k_data = (
            "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDUCS2AOnLmvW7J"
            "cdHkPMr/R/ofYyezVVDFECKFFlNAkE5djYwZZarSMlBALsMU8/AGFSSh9IXXCyQV"
            "6HcUraznulFAqBNLKFGcACcfukoSJhg1wjv9A9D3XBfzz6WDQdBgyrMo6WemoEkK"
            "a92GU7vOPYqBkI+W3uq1CJidTPFswHwhykIJN0TnxnCU7uqx1eyW9akV+MBXJmHR"
            "NwZUEiOqWrBPyU2YcG75iHraH24MnBT2V/s++t0HmoZu+glrijLd+rLC3t52zN8d"
            "xR4XWeopIW+Rejatu9lE8OtfnIIIMo1K21glglOwZMhXBHBQvLU72qi8bFsvJQ9W"
            "S6sos68xAgMBAAECggEAG1SphEdEa0CMqLOeoeRCKECfWW9e/Ssok5YeVPhJN9/B"
            "8iYeImHr8Fci5/r/E1LUI/ySsbuCivL5Lke+HbC7Qk1OTt67SetDBbAxWtIY3RkC"
            "8t77+4OD6nZ48ejYhUA0+1z1Vfcr8Jrlf03jCn79jLp7AXNgRsqqBza58UCrN+Cl"
            "dabXCY9FpGeMPLadIA5DRQ9nFp5NHhR8jCCWOb/6HkfIJyS/lvZ6f74kecwEte+x"
            "xer/maPsq4JBBix4bJ3xRAw1NxhM11cds0T29BxkF8dZmax4gI76z0I2GaWD4nL5"
            "8snLTzNWbGfbW6li1s4YROw4jqt6JuCNRH/4ZKjRzwKBgQD+FfR72rB387gTBTaQ"
            "yTt5hjHmZB1mQU/oT1kqAuTuLAW4OnBPWkCmlWuaR8sak9dJrPnuCKTNhV+i1o9s"
            "awRyVvCDYnpFHv/3MeTabvJDUprCBzhJfdLAVGff6iS7jlnnvbOwqJ/4MSocRLsV"
            "SxLPFbdghcOINgpQZj2YxwyFXwKBgQDVoh9snm7SyBu9oos/U33oWbvFTOJvorjF"
            "pQvl6dx+/XLSQ+YZuRX213a9VDRmUp4qC97kW220P2zkGPweckpy9m0L7QWkCUwM"
            "cTJ1mQ9pvQLbBuJLV+X3AZDl4ptxcRPGRceZo4DVLbskNt9J5OQY4PPDxQPtAmMA"
            "2WE3YTUFbwKBgQDOG60o0usXQqJs+2uZ40LVf1/3DfszOY6CZTllgteFxDwXh4AX"
            "PpT3DHouulItCwQ2hZRv3J8jAC/l/bp2LhF7Vr7fNQEOFOl58gU8k4b9yYI0Jnso"
            "UmKlFVL1tg95/S086QtcIE0znV4VdEN2MGHfjjQknh1Q3tVbBrSsu7qSbQKBgQCA"
            "vkYfyE7TOgL1wmoWTLOY/dLZ8R6Y1kBx46gK82eNJCI5MvANWmwxKOIG8SLu8yUc"
            "A7Fcfvja4ko2IBR4KLpTE8zdngaDN5McAG+/TPFr8Jsy8bAYZa1RsSDoWSsCL3oS"
            "R+Uk4tL2JawdA/CGcKlBkPd2aFmYUJLnZRlgLXWtgwKBgDh1UoYHytr52ps9leho"
            "fYwAvZVXGd0Hqv4sdi+YWzGcQKJ30sgHfQUOxNgMo1/AVVdm+xn+svIk18nVvfjl"
            "mDGCxBIQg27tEfZasOVwQlkUwULvN9UXYNgPPc28E/krhVVdWt2foy6J0iNye97N"
            "9r7OovQdTCBfT0srvINlQpEk"
        )
        
        # 기계가 직접 줄바꿈을 넣어 PEM 형식을 강제 완성합니다.
        formatted_key = "-----BEGIN PRIVATE KEY-----\n"
        for i in range(0, len(k_data), 64):
            formatted_key += k_data[i:i+64] + "\n"
        formatted_key += "-----END PRIVATE KEY-----\n"
        
        info = {
            "type": "service_account",
            "project_id": "formal-facet-469109-n9",
            "private_key_id": "a75d5c613386e549458b7f9ce7429053fa690601",
            "private_key": formatted_key,
            "client_email": "97202050044-compute@developer.gserviceaccount.com",
            "client_id": "106591061735155848403",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/97202050044-compute%40developer.gserviceaccount.com"
        }
        
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"❌ 인증 복구 실패: {e}")
        return None

client = get_final_client()

st.markdown("<h2 style='text-align: center;'>⚖️ Legal_AI: 서비스 준비 완료</h2>", unsafe_allow_html=True)

if client:
    uploaded_file = st.file_uploader("법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])
    if uploaded_file:
        with st.spinner('AI가 서류를 정밀 분석 중입니다...'):
            try:
                full_text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        full_text += client.document_text_detection(image=vision.Image(content=pix.tobytes("png"))).full_text_annotation.text + "\n"
                else:
                    full_text = client.document_text_detection(image=vision.Image(content=uploaded_file.getvalue())).full_text_annotation.text
                
                st.success("✅ 분석 완료!")
                st.text_area("인식 결과", full_text, height=450)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
