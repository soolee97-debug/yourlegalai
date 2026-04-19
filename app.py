import streamlit as st
import json
from google.cloud import vision
from google.oauth2 import service_account
import fitz

st.set_page_config(page_title="Legal_AI: 최종 승인", layout="wide")

st.sidebar.title("🔑 보안 인증")
# [최종 정공법] 복잡한 설정을 거치지 않고, 화면에서 직접 키를 입력받습니다.
json_input = st.sidebar.text_area("1. JSON 파일 내용 전체를 여기에 붙여넣으세요", height=300, help="구글에서 다운받은 .json 파일을 메모장으로 열어 전체 복사-붙여넣기 하세요.")

def get_client(json_text):
    try:
        info = json.loads(json_text)
        creds = service_account.Credentials.from_service_account_info(info)
        return vision.ImageAnnotatorClient(credentials=creds)
    except Exception as e:
        st.sidebar.error(f"⚠️ 인증 대기 중: {e}")
        return None

client = None
if json_input:
    client = get_client(json_input)

st.title("⚖️ Legal_AI: 서비스 가동")

if client:
    st.success("✅ 인증 성공! 이제 서류를 분석할 수 있습니다.")
    uploaded_file = st.file_uploader("2. 법인등기부 PDF 또는 이미지를 업로드하세요", type=["pdf", "png", "jpg"])
    
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
                
                st.subheader("📝 분석 결과")
                st.text_area("인식된 텍스트", full_text, height=500)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
else:
    st.info("👈 왼쪽 사이드바에 구글 JSON 키 내용을 붙여넣으시면 분석 창이 나타납니다.")
    st.image("https://www.gstatic.com/lamda/images/sparkle_v2_dark_rdm_600x337.png", caption="인증을 기다리고 있습니다.")
