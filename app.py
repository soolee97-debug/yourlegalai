import streamlit as st
import json
import base64
from google.cloud import vision
from google.oauth2 import service_account
import fitz  # PyMuPDF

st.set_page_config(page_title="Legal_AI: 문서 분석", layout="wide")

def get_final_client():
    try:
        # [복사 에러 방지용 특수 포장]
        # 모든 데이터를 알파벳과 숫자로만 변환했습니다. 
        # 이제 복사 중에 글자가 깨지거나 잘릴 위험이 0%입니다.
        b64_parts = [
            "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogImZvcm1hbC1mYWNl",
            "dC00NjkxMDktbjkiLCAicHJpdmF0ZV9rZXlfaWQiOiAiYTc1ZDVjNjEzMzg2ZTU0OTQ1OGI3",
            "ZjljZTc0MjkwNTNmYTY5MDYwMSIsICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZB",
            "VEUgS0VZLS0tLS1cbk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktnd2dnU2tB",
            "Z0VBQW9JQkFRRFVDUzJBT25MbXZXN0pcbmNkSGtQTXIvUi9vZll5ZXpWVkRGRUNLRkZsTkFr",
            "RTVkall3WlphclNNbEJBTHNNVTgvQUdGU1NoOUlYWEN5UVZcbjZIY1VyYXpudWxGQXFCTkxL",
            "RkdjQUNjZnVrb1NKaGcxd2p2OUE5RDNYQmZ6ejZXRFFkQmd5ck1vNldlbW9Fa0tcbmE5MkdV",
            "N3ZPUFlxQmtJK1czdXExQ0ppZFRQRnN3SHdoeWtJSk4wVG54bkNVN3VxeDFleVc5YWtWK01C",
            "WEptSFJcbk53WlVFaU9xV3JCUHlVMlljRzc1aUhyYUgyNE1uQlQyVi9zKyt0MEhtb1p1K2ds",
            "cmloTGQrckxDM3Q1MnpOOGRcbnhSNFhXZW9wSVcrUmVqYXR1OWxFOE90Zm5JSUlNbzFLMjFn",
            "bGdsT3daTWhYQkhCUXZMVTcycWk4YkZzdkpROVdcblM2c29zNjh4QWdNQkFBRUNnZ0VBRzFT",
            "cGhFZEVhMENNcUxPZW9lUkNLRUNmV1c5ZS9Tc29rNVllVlBoSk45L0JcbjhpWWVJbUhyOEZj",
            "aTUvci9FMUxVSS95U3NidUNpdkw1TGtlK0hiQzdRazFPVHQ2N1NldERCYkF4V3RJWTNSa0Nc",
            "Njh0NzcrNE9ENm5aNDhlalloVUEwKzF6MVZmY3I4SnJsZjAzakNuNzlqTHA3QVhOZ1JzcXBC",
            "emE1OFVDck4rQ2xcbmRhYlhDWTlGcEdlTVBMYWRJQTVEUlE5bkZwNU5IaFI4akNDV09iLzZI",
            "a2ZJSnlTL2x2WjZmNzRrZWN3RXRlK3hcbnhlci9tYVBzcTRKQkJpeDRiSjN4UkF3MU54aE0x",
            "MWNkczBUMjlCeGtGOGRabWF4NGdJNzZ6MEkyR2FXRDRuTDVcbjhzbkxUek5XYkdmYlc2bGkx",
            "czRZUk93NGpxdDZKdUNOUkgvNFpLalJ6d0tCZ1FEK0ZmUjcyckIzODdnVEJUYVFcbnlUdDVo",
            "akhtWkIxbVFVL29UMWtxQXVUdUxBVzRPbkJQV2tDbWxXdWFSOHNhazlkSnJQbnVDS1ROaFYr",
            "aTFvOXNcXCBuYXdSeVZ2Q0RZbnBGSHYvM01lVGFidkpEVXByQ0J6aEpmZExBVkdmZjZpUzdq",
            "bG5udmJPd3FKLzRNU29jUkxzVlxcU3hMUEZiZGdoY09JTmdwUVpqMll4d3lGWHdLQmdRRFZv",
            "aDlzbm03U3lCdTlvb3MvVTMzb1didkZUT0p2b3JqRlxucFF2bDZkeCsvWExTUStZWnVSWDIx",
            "M2E5VkRSbVVwNHFDOTdrVzIyMFAyemtHUHdlY2tweTltMEw3UVdrQ1V3TVxuY1RKMW1ROXB2",
            "UUxiQnVKTFYrWDNBWkRsNHB0eGNSUEdSY2VabzREVkxic2tOdDlKNU9RWTRQUER4UVB0QW1N",
            "QVxuMldFM1lUVUZid0tCZ1FET0c2MG8wdXNYUXFKcysydVo0MExWZjEvM0Rmc3pPWTZDWlRs",
            "bGd0ZUZ4RHdYaDRBWFxuUHBUM0RIb3V1bEl0Q3dRMmhaUnYzSjhqQUMvbC9icDJMaEY3VnI3",
            "Zk5RRU9GT2w1OGdVOGs0Yjl5WUkwSm5zb1xuVW1LbEZWTDF0Zzk1L1MwODZRdGNJRTB6blY0",
            "VmRFTjJNR0hmampRa25oMVEzdFZiQnJTc3U3cVNiUUtCZ1FDQVxudmtZZnlFN1RPZ0wxd21v",
            "V1RMT1kvZExaOFI2WTFrQng0NmdLODJlTkpDSTVNdkFOV213eEtPSUc4U0x1OHlVY1xuQTdG",
            "Y2Z2amE0a28ySUJSNEtMcFRFOHpkbmdhRE41TWNBRysvVFBGcjhKc3k4YkFZWmExUnNTRG9X",
            "U3NDTDNvU1xuUitVazR0TDJKYXdkQS9DR2NLbEJrUGQyYUZtWVVKTG5aUmxnTFhXdGd3S0Jn",
            "RGgxVW9ZSHl0cjUycHM5bGVob1xuZll3QXZaVlhHZDBIcXY0c2RpK1lXekdjUUtKMzBzZ0hm",
            "UVVPeE5nTW8xL0FWVmRtK3huK3N2SWsxOG5WdmZqbFxubURHQ3hCSVFnMjd0RWZaYXNPVndR",
            "bGtVd1VMdk45VVhZTmdQUGMyOEUva3JoVlZkV3QyZm95NkowaU55ZTk3TlxuOXI3T292UWRU",
            "Q0JmVDBzcnZJTmxRcEVrXG4tLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tXG4iLCAiY2xpZW50",
            "X2VtYWlsIjogIjk3MjAyMDUwMDQ0LWNvbXB1dGVAZGV2ZWxvcGVyLmdzZXJ2aWNlYWNjb3Vu",
            "dC5jb20iLCAiY2xpZW50X2lkIjogIjEwNjU5MTA2MTczNTE1NTg0ODQwMyIsICJhdXRoX3Vy",
            "aSI6ICh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS8vby9vYXV0aDIvYXV0aCIsICJ0b2tl",
            "bl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLCAiYXV0aF9w",
            "cm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29h",
            "dXRoMi92MS9jZXJ0cyIsICJjbGllbnRfeDUwOV9jZXJ0X3VybCI6ICJodHRwczovL3d3dy5n",
            "b29nbGVhcGlzLmNvbS9yb2JvdC92MS9tZXRhZGF0YS94NTA5Lzk3MjAyMDUwMDQ0LWNvbXB1",
            "dGUlNDBkZXZlbG9wZXIuZ3NlcnZpY2VhY2NvdW50LmNvbSIsICJ1bml2ZXJzZV9kb21haW4i",
            "OiAiZ29vZ2xlYXBpcy5jb20ifQ=="
        ]
        
        # 1. 포장된 암호문을 하나로 합쳐서 풉니다.
        full_b64 = "".join(b64_parts)
        json_str = base64.b64decode(full_b64).decode('utf-8')
        info = json.loads(json_str)
        
        # 2. 인증서를 생성합니다.
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.error(f"❌ 보안 시스템 최종 해독 실패: {e}")
        return None

client = get_final_client()

st.title("⚖️ Legal_AI: 서비스 가동 중")

if client:
    st.success("✅ 시스템이 드디어 정상 가동됩니다!")
    uploaded_file = st.file_uploader("분석할 서류(PDF/이미지)를 업로드하세요", type=["pdf", "png", "jpg"])
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
                
                st.subheader("📝 분석 결과")
                st.text_area("인식된 내용", text, height=500)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
