import streamlit as st
import json
from google.cloud import vision
from google.oauth2 import service_account
import fitz # PyMuPDF

st.set_page_config(page_title="Legal_AI: 문서 자동화", layout="wide")

# [완전 종결] 어떤 환경에서도 깨지지 않도록 조립된 보안키
def get_final_client():
    try:
        # 키 조각들을 합쳐서 PEM 형식을 강제로 완성합니다.
        key_body = (
            "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDUCS2AOnLmvW7J\n"
            "cdHkPMr/R/ofYyezVVDFECKFFlNAkE5djYwZZarSMlBALsMU8/AGFSSh9IXXCyQV\n"
            "6HcUraznulFAqBNLKFGcACcfukoSJhg1wjv9A9D3XBfzz6WDQdBgyrMo6WemoEkK\n"
            "a92GU7vOPYqBkI+W3uq1CJidTPFswHwhykIJN0TnxnCU7uqx1eyW9akV+MBXJmHR\n"
            "NwZUEiOqWrBPyU2YcG75iHraH24MnBT2V/s++t0HmoZu+glrijLd+rLC3t52zN8d\n"
            "xR4XWeopIW+Rejatu9lE8OtfnIIIMo1K21glglOwZMhXBHBQvLU72qi8bFsvJQ9W\n"
            "S6sos68xAgMBAAECggEAG1SphEdEa0CMqLOeoeRCKECfWW9e/Ssok5YeVPhJN9/B\n"
            "8iYeImHr8Fci5/r/E1LUI/ySsbuCivL5Lke+HbC7Qk1OTt67SetDBbAxWtIY3RkC\n"
            "8t77+4OD6nZ48ejYhUA0+1z1Vfcr8Jrlf03jCn79jLp7AXNgRsqqBza58UCrN+Cl\n"
            "dabXCY9FpGeMPLadIA5DRQ9nFp5NHhR8jCCWOb/6HkfIJyS/lvZ6f74kecwEte+x\n"
            "xer/maPsq4JBBix4bJ3xRAw1NxhM11cds0T29BxkF8dZmax4gI76z0I2GaWD4nL5\n"
            "8snLTzNWbGfbW6li1s4YROw4jqt6JuCNRH/4ZKjRzwKBgQD+FfR72rB387gTBTaQ\n"
            "yTt5hjHmZB1mQU/oT1kqAuTuLAW4OnBPWkCmlWuaR8sak9dJrPnuCKTNhV+i1o9s\n"
            "awRyVvCDYnpFHv/3MeTabvJDUprCBzhJfdLAVGff6iS7jlnnvbOwqJ/4MSocRLsV\n"
            "SxLPFbdghcOINgpQZj2YxwyFXwKBgQDVoh9snm7SyBu9oos/U33oWbvFTOJvorjF\n"
            "pQvl6dx+/XLSQ+YZuRX213a9VDRmUp4qC97kW220P2zkGPweckpy9m0L7QWkCUwM\n"
            "cTJ1mQ9pvQLbBuJLV+X3AZDl4ptxcRPGRceZo4DVLbskNt9J5OQY4PPDxQPtAmMA\n"
            "2WE3YTUFbwKBgQDOG60o0usXQqJs+2uZ40LVf1/3DfszOY6CZTllgteFxDwXh4AX\n"
            "PpT3DHouulItCwQ2hZRv3J8jAC/l/bp2LhF7Vr7fNQEOFOl58gU8k4b9yYI0Jnso\n"
            "UmKlFVL1tg95/S086QtcIE0znV4VdEN2MGHfjjQknh1Q3tVbBrSsu7qSbQKBgQCA\n"
            "vkYfyE7TOgL1wmoWTLOY/dLZ8R6Y1kBx46gK82eNJCI5MvANWmwxKOIG8SLu8yUc\n"
            "A7Fcfvja4ko2IBR4KLpTE8zdngaDN5McAG+/TPFr8Jsy8bAYZa1RsSDoWSsCL3oS\n"
            "R+Uk4tL2JawdA/CGcKlBkPd2aFmYUJLnZRlgLXWtgwKBgDh1UoYHytr52ps9leho\n"
            "fYwAvZVXGd0Hqv4sdi+YWzGcQKJ30sgHfQUOxNgMo1/AVVdm+xn+svIk18nVvfjl\n"
            "mDGCxBIQg27tEfZasOVwQlkUwULvN9UXYNgPPc28E/krhVVdWt2foy6J0iNye97N\n"
            "9r7OovQdTCBfT0srvINlQpEk"
        )
        
        full_key = "-----BEGIN PRIVATE KEY-----\n" + key_body + "\n-----END PRIVATE KEY-----\n"
        
        info = {
            "type": "service_account",
            "project_id": "formal-facet-469109-n9",
            "private_key_id": "a75d5c613386e549458b7f9ce7429053fa690601",
            "private_key": full_key,
            "client_email": "97202050044-compute@developer.gserviceaccount.com",
            "client_id": "106591061735155848403",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/97202050044-compute%40developer.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
        
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"❌ 인증 시스템 오류: {e}")
        return None

client = get_final_client()

st.markdown("<h2 style='text-align: center; color: #2c3e50;'>⚖️ Legal_AI: 서비스 준비 완료</h2>", unsafe_allow_html=True)

if client:
    uploaded_file = st.file_uploader("법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])
    if uploaded_file:
        with st.spinner('AI 분석 중...'):
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
                st.text_area("결과 텍스트", full_text, height=400)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
