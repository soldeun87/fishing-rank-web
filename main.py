import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# --- [보안 설정: 관리자 설정창에서 키를 가져옵니다] ---
try:
    CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
    MASTER_PASSWORD = st.secrets["APP_PASSWORD"] # 접속 비밀번호
except:
    st.error("보안 설정(Secrets)이 완료되지 않았습니다.")
    st.stop()

st.set_page_config(page_title="피싱템 보안 레이더", layout="wide")

# --- [간이 로그인 기능] ---
st.sidebar.title("🔐 보안 접속")
user_pw = st.sidebar.text_input("비밀번호를 입력하세요", type="password")

if user_pw != MASTER_PASSWORD:
    st.info("왼쪽 사이드바에 비밀번호를 입력해야 수색을 시작할 수 있습니다.")
    st.stop()

# --- [메인 화면] ---
st.title("🚀 피싱템 전용 초고속 레이더")
keyword = st.text_input("수색할 키워드", value="타이라바로드")

if st.button("수색 시작"):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={keyword}&display=100"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    
    if "items" in data:
        all_results = []
        found_my_items = []
        for idx, item in enumerate(data['items']):
            title = item['title'].replace("<b>", "").replace("</b>", "")
            item_data = {"순위": idx + 1, "상품명": title, "판매처": item['mallName']}
            if "피싱템" in item['mallName'] or "피싱템" in title:
                found_my_items.append(item_data)
            all_results.append(item_data)

        if found_my_items:
            st.success(f"우리 상품 발견! {found_my_items[0]['순위']}위 노출 중")
            st.table(pd.DataFrame(found_my_items))
        
        # 엑셀 다운로드
        df = pd.DataFrame(all_results)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📁 전체 결과 엑셀 저장", output.getvalue(), f"{keyword}_순위.xlsx")
