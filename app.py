import streamlit as st
import json
import base64
from google.cloud import vision
from google.oauth2 import service_account
import fitz  # PyMuPDF

st.set_page_config(page_title="Legal_AI: 문서 자동화", layout="wide")

# [우주 최강 종결] 복사 시 글자가 깨지지 않도록 암호화(Base64) 처리한 키입니다.
def get_final_client():
    try:
        # 이 암호문은 복사 중에 글자가 깨질 확률이 0%입니다.
        b64_key = (
            "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogImZvcm1hbC1mYWNl"
            "dC00NjkxMDktbjkiLCAicHJpdmF0ZV9rZXlfaWQiOiAiYTc1ZDVjNjEzMzg2ZTU0OTQ1OGI3"
            "ZjljZTc0MjkwNTNmYTY5MDYwMSIsICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZB"
            "VEUgS0VZLS0tLS1cbiJzYmI3ZkpMQUFvSUJBUURVQ1MyQU9uTG12VzdKY2RIUE1yL1Ivb2ZZ"
            "eWV6VlZERklFQ0tGRmxOQWtFNWRqWXdaWmFyU01sQkFMczNVL0FHRlNTaDlJWFhDeVFWNmhj"
            "VXJhem51bEZBcUJOTEtGR2NBQ2NmdWtvU0poRzF3anY5QTlEM1hCZnp6NldERGRCZ3lyTW82"
            "V2Vtb0VrS2E5MkdVN3ZPUFlxQmtJK1czdXExQ0ppZFRQRnN3SHdoeWtJSk4wVG54bkNVN3Vx"
            "cjFleVc5YWtWK01CWExtSFJOd1pVRWlPcVdyQlB5VTJZY0c3NWlIcmFIMjRNbkJUMlYvcysr"
            "dDBIbW9adStnbHJpaktkK3JMQzN0NTJ6TjhknhSNEhXZW9wSVcrUmVqYXR1OWxFOE90Zm5J"
            "SUlNbzFLMjFnbGdsT3daTWhYQkhCUXZMVTcycWk4YkZzdkpROVdTNnNvczY4eEFnTUJBQUVD"
            "Z2dFQUcxU3BoRWRFYTBDbXFMT2VvUkNLRUNmV1c5ZS9Tc29rNVllVlBoSk45L0I4aVllSW1I"
            "cjhGY2k1L3IvRTFMVUkveVNzYnVDaXZMNUxreStIYkM3UWsxT1R0NjdTZXREQmJBeFd0SVkz"
            "UmtDOHQ3Nys0T0Q2blo0OGVqWWhVQTArMXpMVmZjclhKcmxmMDNqQ243OWpMcDdBYE5nUnNx"
            "cUJ6YTU4VUNyTitDbGR
