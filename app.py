import streamlit as st
import json
import base64
from google.cloud import vision
from google.oauth2 import service_account
import fitz  # PyMuPDF

st.set_page_config(page_title="Legal_AI: 문서 자동화", layout="wide")

# [완전 종결] 복사 에러가 절대 날 수 없는 분할 암호화 방식
def get_final_client():
    try:
        # 암호문을 조각내서 복사 사고를 원천 방지합니다.
        chunks = [
            "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogImZvcm1hbC1mYWNl",
            "dC00NjkxMDktbjkiLCAicHJpdmF0ZV9rZXlfaWQiOiAiYTc1ZDVjNjEzMzg2ZTU0OTQ1OGI3",
            "ZjljZTc0MjkwNTNmYTY5MDYwMSIsICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZB",
            "VEUgS0VZLS0tLS1cbiJzYmI3ZkpMQUFvSUJBUURVQ1MyQU9uTG12VzdKY2RIUE1yL1Ivb2ZZ",
            "eWV6VlZERklFQ0tGRmxOQWtFNWRqWXdaWmFyU01sQkFMczNVL0FHRlNTaDlJWFhDeVFWNmhj",
            "VXJhem51bEZBcUJOTEtGR2NBQ2NmdWtvU0poRzF3anY5QTlEM1hCZnp6NldERGRCZ3lyTW82",
            "V2Vtb0VrS2E5MkdVN3ZPUFlxQmtJK1czdXExQ0ppZFRQRnN3SHdoeWtJSk4wVG54bkNVN3Vx",
            "cjFleVc5YWtWK01CWExtSFJOd1pVRWlPcVdyQlB5VTJZY0c3NWlIcmFIMjRNbkJUMlYvcysr",
            "dDBIbW9adStnbHJpaktkK3JMQzN0NTJ6TjhknhSNEhXZW9wSVcrUmVqYXR1OWxFOE90Zm5J",
            "SUlNbzFLMjFnbGdsT3daTWhYQkhCUXZMVTcycWk4YkZzdkpROVdTNnNvczY4eEFnTUJBQUVD",
            "Z2dFQUcxU3BoRWRFYTBDbXFMT2VvUkNLRUNmV1c5ZS9Tc29rNVllVlBoSk45L0I4aVllSW1I"
            "cjhGY2k1L3IvRTFMVUkveVNzYnVDaXZMNUxreStIYkM3UWsxT1R0NjdTZXREQmJBeFd0SVkz"
            "UmtDOHQ3Nys0T0Q2blo0OGVqWWhVQTArMXpMVmZjclhKcmxmMDNqQ243OWpMcDdBYE5nUnNx"
            "cUJ6YTU4VUNyTitDbGRhYlhDWTlGcFZlTVBMYWRJQTVEUVE5bkZwNU5IaFI4akNDV09iLzZI"
            "a2ZJSnlTL2x2WjZmNzRrZWN3RXRlK3h4ZXIvbWFQc3E0SkJCaXg0YkpkeFJBdzFOeGhNMTFj"
            "ZHMwVDI5QnhrRjhkWm1heDRnSTc2ejBJMkdhV0Q0bkw1OHNuTFR6TldiR2ZiVzZsaTFzNFlS"
            "T3c0anF0Nkp1Q05SSC80WktqUnp3S0JnUUQrRmZSNzJyQjM4N2dUQlRhcVl0dDVoakhtWkIx"
            "bVFVL29UMWtxQXVUdUxBVzRPbkJQV2tDbWxXdWFSOHNhazlkSnJQbnVDS1ROaFYraTFvOXNy"
            "UnlWdkNEWW5wRkh2LzNNZVRhYnZKRVlwckNCemhKZmRMQVZHZmY2aVM3amxubnZiT3dxSi80"
            "TVNvY1JMc1ZTeExQRmJkZ2hjT0lOZ3BRWmoyWXh3eUZYd0tCZ1FEVm9IOXNubTdTeUJ1OW9v"
            "cy9VMzNvV2J2RlRPSnZvcmtGcFF2bDZkeCsvWExTUStZWHVWWDIxM2E5VkRSbVVwNHFDOXdr"
            "MjIyMFAyemtHcHdlY2tweTltMEw3UVdrQ1V3TWNUSjFtUTlwdlFMYkJ1SkxWK1gzQVpEbDRw"
            "dHhjUlBHUmNlWm80RFZMYnNrTnQ5SjVPUVk0UFBEeFFQdEFtTUEyV0UzWVRVRmJ3S0JnUURO"
            "RzYwbzB1c1hRcUpzKzJ1WjQwTFZmMS8zRGZzek9ZNkNadGxsZ3RlRnhEd1hoNEFYUHBUM0RI"
            "b3V1bEl0Q3dRMmhZUnZKMzhqQUMvbC9icDJMaEY3VnI3Zk5RRU9GT2w1Z1U4azRiOXlZSTBK"
            "bnNvVW1LbEZWTDF0Zzk1L1MwODZRdGNJRTB6blY0VmRFTjJNR2hmampRa25oMVEzdFZiQnJT"
            "dTdxU2JRS0JnUUNBdmthZnlFN1RPZ0wxd21vV1RMT1kvZExaOFI2WTFrQng0NmdLODJlTko2"
            "STVNdklBTndteEtPSUc4U0x1OHlVY0E3RmNmdmphNGtvMklCUjRLTFBURTh6ZG5nYUROMU1j"
            "QUcrL1RQRnI4SnN5OGJBWVphMVJzU0RvV1NzQ0wzb1NSK1VrNHRMMkphd0RBL0NHY0tsQmtQ"
            "ZDJhRm1ZVUpsblpSZ2xMWFd0Z3dLQmdEaDFVb1lIeXRyNTJwcTlsZWhvZll3QXZaVlhHZDBI"
            "cXY0c2RpK1lXekdjUUtKMzBzg0hmUVVPeE5nTW8xL0FWVmRtK3huK3N2SWsxblZ2ZmphbURH"
            "Q3hCSVFnMzd0RWZaYXNPVndRbGtVclV2TjlVWFlOZ1BQYzI4RS9rcmhwVmRXdDJmb3k2SjBp"
            "TnllOTdOOXI3T292UWRUQ0JmVDBzcnZJTmxRUEVrXG4tLS0tLUVORCBQUklWQVRFIEtFWS0t"
            "LS1cbiIsICJjbGllbnRfZW1haWwiOiAiOTcyMDIwNTAwNDQtY29tcHV0ZUBkZXZlbG9wZXIu"
            "Z3NlcnZpY2VhY2NvdW50LmNvbSIsICJjbGllbnRfaWQiOiAiMTA2NTkxMDYxNzM1MTU1ODQ4"
            "NDAzIiwgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRo"
            "Mi9hdXRoIiwgInRva2VuX3VyaSI6ICJodHRwczovL29hdXRoMi5nb29nbGVhcGlzLmNvbS90"
            "b2tlbiIsICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29v"
            "Z2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwgImNsaWVudF94NTA5X2NlcnRfdXJsIjog"
            "Imh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvOTcy"
            "MDIwNTAwNDQtY29tcHV0ZSU0MGRldmVsb3Blci5nc2VydmljZWFjY291bnQuY29tIiwgInVu"
            "aXZlcnNlX2RvbWFpbiI6ICJnb29nbGVhcGlzLmNvbSJ9"
        ]
        
        # 기계가 조각들을 하나로 합친 뒤 암호를 풉니다.
        full_b64 = "".join(chunks)
        info = json.loads(base64.b64decode(full_b64).decode('utf-8'))
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"❌ 최종 인증 시스템 가동 실패: {e}")
        return None

client = get_final_client()

st.title("⚖️ Legal_AI: 서비스 준비 완료")

if client:
    uploaded_file = st.file_uploader("법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])
    if uploaded_file:
        with st.spinner('AI가 서류를 분석 중입니다...'):
            try:
                text = ""
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap()
                        img = vision.Image(content=pix.tobytes("png"))
                        text += client.document_text_detection(image=img).full_text_annotation.text + "\n"
                else:
                    img = vision.Image(content=uploaded_file.getvalue())
                    text = client.document_text_detection(image=img).full_text_annotation.text
                
                st.success("✅ 분석 완료!")
                st.text_area("인식 결과", text, height=450)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
