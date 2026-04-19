import streamlit as st
import os, re, json
from google.cloud import vision
from google.oauth2 import service_account
import fitz # PyMuPDF

st.set_page_config(page_title="Legal_AI: 문서 자동화", layout="wide")

# 1. 키 데이터 (가장 원시적인 형태로 저장)
raw_key = """{
  "type": "service_account",
  "project_id": "formal-facet-469109-n9",
  "private_key_id": "a75d5c613386e549458b7f9ce7429053fa690601",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDUCS2AOnLmvW7J\\ncdHkPMr/R/ofYyezVVDFECKFFlNAkE5djYwZZarSMlBALsMU8/AGFSSh9IXXCyQV\\n6HcUraznulFAqBNLKFGcACcfukoSJhg1wjv9A9D3XBfzz6WDQdBgyrMo6WemoEkK\\na92GU7vOPYqBkI+W3uq1CJidTPFswHwhykIJN0TnxnCU7uqx1eyW9akV+MBXJmHR\\nNwZUEiOqWrBPyU2YcG75iHraH24MnBT2V/s++t0HmoZu+glrijLd+rLC3t52zN8d\\nxR4XWeopIW+Rejatu9lE8OtfnIIIMo1K21glglOwZMhXBHBQvLU72qi8bFsvJQ9W\\nS6sos68xAgMBAAECggEAG1SphEdEa0CMqLOeoeRCKECfWW9e/Ssok5YeVPhJN9/B\\n8iYeImHr8Fci5/r/E1LUI/ySsbuCivL5Lke+HbC7Qk1OTt67SetDBbAxWtIY3RkC\\n8t77+4OD6nZ48ejYhUA0+1z1Vfcr8Jrlf03jCn79jLp7AXNgRsqqBza58UCrN+Cl\\ndabXCY9FpGeMPLadIA5DRQ9nFp5NHhR8jCCWOb/6HkfIJyS/lvZ6f74kecwEte+x\\nxer/maPsq4JBBix4bJ3xRAw1NxhM11cds0T29BxkF8dZmax4gI76z0I2GaWD4nL5\\n8snLTzNWbGfbW6li1s4YROw4jqt6JuCNRH/4ZKjRzwKBgQD+FfR72rB387gTBTaQ\\nyTt5hjHmZB1mQU/oT1kqAuTuLAW4OnBPWkCmlWuaR8sak9dJrPnuCKTNhV+i1o9s\\nawRyVvCDYnpFHv/3MeTabvJDUprCBzhJfdLAVGff6iS7jlnnvbOwqJ/4MSocRLsV\\nSxLPFbdghcOINgpQZj2YxwyFXwKBgQDVoh9snm7SyBu9oos/U33oWbvFTOJvorjF\\npQvl6dx+/XLSQ+YZuRX213a9VDRmUp4qC97kW220P2zkGPweckpy9m0L7QWkCUwM\\ncTJ1mQ9pvQLbBuJLV+X3AZDl4ptxcRPGRceZo4DVLbskNt9J5OQY4PPDxQPtAmMA\\n2WE3YTUFbwKBgQDOG60o0usXQqJs+2uZ40LVf1/3DfszOY6CZTllgteFxDwXh4AX\\nPpT3DHouulItCwQ2hZRv3J8jAC/l/bp2LhF7Vr7fNQEOFOl58gU8k4b9yYI0Jnso\\nUmKlFVL1tg95/S086QtcIE0znV4VdEN2MGHfjjQknh1Q3tVbBrSsu7qSbQKBgQCA\\nvkYfyE7TOgL1wmoWTLOY/dLZ8R6Y1kBx46gK82eNJCI5MvANWmwxKOIG8SLu8yUc\\nA7Fcfvja4ko2IBR4KLpTE8zdngaDN5McAG+/TPFr8Jsy8bAYZa1RsSDoWSsCL3oS\\nR+Uk4tL2JawdA/CGcKlBkPd2aFmYUJLnZRlgLXWtgwKBgDh1UoYHytr52ps9leho\\nfYwAvZVXGd0Hqv4sdi+YWzGcQKJ30sgHfQUOxNgMo1/AVVdm+xn+svIk18nVvfjl\\nmDGCxBIQg27tEfZasOVwQlkUwULvN9UXYNgPPc28E/krhVVdWt2foy6J0iNye97N\\n9r7OovQdTCBfT0srvINlQpEk\\n-----END PRIVATE KEY-----\\"
}"""

# 2. 어떤 깨진 기호가 들어와도 완벽하게 복구하는 마법의 로직
try:
    # 역슬래시 중복 문제 해결
    fixed_key_str = raw_key.replace("\\\\n", "\n").replace("\\n", "\n")
    info = json.loads(fixed_key_str)
    creds = service_account.Credentials.from_service_account_info(info)
    client = vision.ImageAnnotatorClient(credentials=creds)
except Exception as e:
    st.error(f"⚠️ 인증 복구 시도 중 에러: {e}")
    st.stop()

st.markdown("### ⚖️ Legal_AI: 서비스 준비 완료")

# 3. 파일 업로드 및 분석
uploaded_file = st.file_uploader("법인등기부 PDF를 업로드하세요", type=["pdf", "png", "jpg"])

if uploaded_file:
    with st.spinner('AI가 서류를 읽고 있습니다...'):
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
            
            st.success("✅ 분석이 완료되었습니다!")
            st.text_area("인식 결과", full_text, height
