import streamlit as st
import json
import base64
from google.cloud import vision
from google.oauth2 import service_account
import fitz

st.set_page_config(page_title="Legal_AI 종결", layout="wide")

# [우주 최강 종결] 복사 사고가 절대로 날 수 없게 특수 포장된 데이터입니다.
def get_final_stable_client():
    try:
        # 이 암호문은 알파벳과 숫자로만 되어 있어 복사 중에 변형될 수가 없습니다.
        p_1 = "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogImZvcm1hbC1m"
        p_2 = "YWNldC00NjkxMDktbjkiLCAicHJpdmF0ZV9rZXlfaWQiOiAiYTc1ZDVjNjEzMzg2ZTU0"
        p_3 = "OTQ1OGI3ZjljZTc0MjkwNTNmYTY5MDYwMSIsICJwcml2YXRlX2tleSI6ICItLS0tLUJF"
        p_4 = "R0lOIFBSSVZBVEUgS0VZLS0tLS1cbiIgKyAiTUlJRXZnSUJBRURBTkJna3Foa2lHOXcw"
        p_5 = "QkFRRUZBQVNDQktnd2dnU2tBZ0VBQW9JQkFRRFVDUzJBT25MbXZXN0pcdm5jZEhrUE1y"
        p_6 = "L1Ivb2ZZeWV6VlZERklFQ0tGRmxOQWtFNWRqWXdaWmFyU01sQkFMczNVL0FHRlNTaDlJ"
        p_7 = "WFhDeVFWXG52NmhjVXJhem51bEZBcUJOTEtGR2NBQ2NmdWtvU0poRzF3anY5QTlEM1hC"
        p_8 = "Znp6NldERGRCZ3lyTW82V2Vtb0VrS2E5MkdVN3ZPUFlxQmtJK1czdXExQ0ppZFRQRnN3"
        p_9 = "SHdoeWtJSk4wVG54bkNVN3VxejFleVc5YWtWK01CWExtSFJOd1pVRWlPcVdyQlB5VTJZ"
        p_10 = "Y0c3NWlIcmFIMjRNbkJUMlYvcysrdDBIbW9adStnbHJpaktkK3JMQzN0NTJ6TjhkXG54"
        p_11 = "UjRIXFwvV2VvUElXK1JlamF0dTlsRThPdGZuSUlJTW8xSzIxZ2xnbE93Wk1oWEJIQlF2"
        p_12 = "TFVceC83MnFpOGJGN3N2SlE5V1M2c29zNjh4QWdNQkFBRUNnZ0VBRzFTcGhFZEVhMENt"
        p_13 = "cUxPZW9lUkNLRUNmV1c5ZS9Tc29rNVllVlBoSk45L0JcbiIArCAiaThZZUltSHI4RmNp"
        p_14 = "NS9yL0UxTFVJL3lTc2J1Q2l2TDVMa2UrS2JDN1FrMU9UdDY3U2V0REJiQXhXdElZM1Jr"
        p_15 = "Qzh0NzcrNE9ENm5aNDhlalloVUEwKzF6MVZmY3I4SnJsZjAzakNuNzlqTHA3QVhOZ1Jz"
        p_16 = "cXBCemE1OFVDck4rQ2xcbmRhYlhDWTlGcFdlTVBMYWRJQTVEUVQ5bkZwNU5IaFI4akND"
        p_17 = "V09iLzZIa2ZJSnlTL2x2WjZmNzRrZWN3RXRlK3h4ZXIvbWFQc3E0SkJCaXg0YkpkeFJB"
        p_18 = "dzFOeGhNMTFjZHMwVDI5QnhrRjhkWm1heDRnSTc2ejBJMkdhV0Q0bkw1OHNuTFR6Tldi"
        p_19 = "R2ZiVzZsaTFzNFlST3c0anF0Nkp1Q05SSC80WktqUnp3S0JnUUQrRmZSNzJyQjM4N2dU"
        p_20 = "QlRhcVl0dDVoakhtWkIxbVFVL29UMWtxQXVUdUxBVzRPbkJQV2tDbWxXdWFSOHNhazlk"
        p_21 = "SnJQbnVDS1ROaFYraTFvOXNyUnlWdkNEWW5wRkh2LzNNZVRhYnZKRVlwckNCemhKZmRM"
        p_22 = "QVZHZmY2aVM3amxubnZiT3dxSi80TVNvY1JMc1ZTeExQRmJkZ2hjT0lOZ3BRWmoyWXh3"
        p_23 = "eUZYd0tCZ1FEVm9IOXNubTdTeUJ1OW9vcy9VMzNvV2J2RlRPSnZvcmtGcFF2bDZkeCsv"
        p_24 = "WExTUStZWHVWWDIxM2E5VkRSbVVwNHFDOXdrMjIyMFAyemtHcHdlY2tweTltMEw3UVdr"
        p_25 = "Q1V3TWNUSjFtUTlwdlFMYkJ1SkxWK1gzQVpEbDRwdHhjUlBHUmNlWm80RFZMYnNrTnQ5"
        p_26 = "SjVPUVk0UFBEeFFQdEFtTUEyV0UzWVRVRmJ3S0JnUURORzYwbzB1c1hRcUpzKzJ1WjQw"
        p_27 = "TFZmMS8zRGZzek9ZNkNadGxsZ3RlRnhEd1hoNEFYUHBUM0RIb3V1bEl0Q3dRMmhZUnZK"
        p_28 = "MzhqQUMvbC9icDJMaEY3VnI3Zk5RRU9GT2w1Z1U4azRiOXlZSTBKbnNvVW1LbEZWTDF0"
        p_29 = "Zzk1L1MwODZRdGNJRTB6blY0VmRFTjJNR2hmampRa25oMVEzdFZiQnJTdTdxU2JRS0Jn"
        p_30 = "UUNBdmthZnlFN1RPZ0wxd21vV1RMT1kvZExaOFI2WTFrQng0NmdLODJlTko2STVNdklB"
        p_31 = "TndteEtPSUc4U0x1OHlVY0E3RmNmdmphNGtvMklCUjRLTFBURTh6ZG5nYUROMU1jQUcr"
        p_32 = "L1RQRnI4SnN5OGJBWVphMVJzU0RvV1NzQ0wzb1NSK1VrNHRMMkphd0RBL0NHY0tsQmtQ"
        p_33 = "ZDJhRm1ZVUpsblpSZ2xMWFd0Z3dLQmdEaDFVb1lIeXRyNTJwcTlsZWhvZll3QXZaVlhH"
        p_34 = "ZDBIcXY0c2RpK1lXekdjUUtKMzBzg0hmUVVPeE5nTW8xL0FWVmRtK3huK3N2SWsxblZ2"
        p_35 = "ZmphbURHQ3hCSVFnMzd0RWZaYXNPVndRbGtVclV2TjlVWFlOZ1BQYzI4RS9rcmhwVmRX"
        p_36 = "dDJmb3k2SjBpTnllOTdOOXI3T292UWRUQ0JmVDBzcnZJTmxRUEVrXG4tLS0tLUVORCBQ"
        p_37 = "UklWQVRFIEtFWS0tLS0tIiwgImNsaWVudF9lbWFpbCI6ICI5NzIwMjA1MDA0NC1jb21w"
        p_38 = "dXRlQGRldmVsb3Blci5nc2VydmljZWFjY291bnQuY29tIiwgImNsaWVudF9pZCI6ICIx"
        p_39 = "MDY1OTEwNjE3MzUxNTU4NDg0MDMiLCAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50"
        p_40 = "cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLCAidG9rZW5fdXJpIjogImh0dHBzOi8v"
        p_41 = "b2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwgImF1dGhfcHJvdmlkZXJfeDUwOV9j"
        p_42 = "ZXJ0X3VybCI6ICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9vYXV0aDIvdjEvY2Vy"
        p_43 = "dHMiLCAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBp"
        p_44 = "cy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS85NzIwMjA1MDA0NC1jb21wdXRlJTQw"
        p_45 = "ZGV2ZWxvcGVyLmdzZXJ2aWNlYWNjb3VudC5jb20iLCAidW5pdmVyc2VfZG9tYWluIjog"
        p_46 = "Imdvb2dsZWFwaXMuY29tIn0="
        
        # 합체 및 해독
        b64_str = p_1+p_2+p_3+p_4+p_5+p_6+p_7+p_8+p_9+p_10+p_11+p_12+p_13+p_14+p_15+p_16+p_17+p_18+p_19+p_20+p_21+p_22+p_23+p_24+p_25+p_26+p_27+p_28+p_29+p_30+p_31+p_32+p_33+p_34+p_35+p_36+p_37+p_38+p_39+p_40+p_41+p_42+p_43+p_44+p_45+p_46
        info = json.loads(base64.b64decode(b64_str).decode('utf-8'))
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"❌ 인증 종결 시스템 실패: {e}")
        return None

client = get_final_stable_client()

st.title("⚖️ Legal_AI: 서비스 가동")

if client:
    st.success("✅ 드디어 시스템이 정상 연결되었습니다!")
    uploaded_file = st.file_uploader("법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])
    if uploaded_file:
        with st.spinner('AI 분석 중...'):
            try:
                text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        text += client.document_text_detection(image=vision.Image(content=pix.tobytes("png"))).full_text_annotation.text + "\n"
                else:
                    text = client.document_text_detection(image=vision.Image(content=uploaded_file.getvalue())).full_text_annotation.text
                st.text_area("분석 결과", text, height=500)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
