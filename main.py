import streamlit as st
import pandas as pd
import requests

# --- [1. 보안 및 상호명 설정] ---
# 상호명은 이제 화면에 노출하지 않고 코드가 내부적으로 기억합니다.
TARGET_STORE = "피싱템"

try:
    CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
    MASTER_PASSWORD = st.secrets["APP_PASSWORD"]
except:
    st.error("보안 설정(Secrets)이 완료되지 않았습니다.")
    st.stop()

# --- [2. 로그인 로직: 입력하면 사라지게 설정] ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("🔐 피싱템 보안 접속")
    pwd_input = st.text_input("접속 비밀번호를 입력하세요", type="password")
    if st.button("로그인"):
        if pwd_input == MASTER_PASSWORD:
            st.session_state['authenticated'] = True
            st.rerun() # 화면을 새로고침하여 비밀번호 창을 없앱니다.
        else:
            st.error("비밀번호가 틀렸습니다.")
    st.stop()

# --- [3. 메인 화면: 로그인 성공 시에만 나타남] ---
st.set_page_config(page_title="피싱템 순위 추적기", layout="wide")
st.title("🎣 피싱템 순위 레이더")

# 검색창 (상호명 입력칸은 삭제했습니다)
keyword = st.text_input("수색할 키워드를 입력하세요 (예: 타이라바 로드)")

if st.button("🚀 순위 수색 시작"):
    if not keyword:
        st.warning("키워드를 입력해주세요.")
    else:
        # 네이버 쇼핑 API 호출
        url = f"https://openapi.naver.com/v1/search/shop.json?query={keyword}&display=100"
        headers = {
            "X-Naver-Client-Id": CLIENT_ID,
            "X-Naver-Client-Secret": CLIENT_SECRET
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            items = response.json().get('items', [])
            found_items = []

            for index, item in enumerate(items):
                mall_name = item.get('mallName', '')
                if TARGET_STORE in mall_name:
                    clean_title = item['title'].replace('<b>', '').replace('</b>', '')
                    found_items.append({
                        "순위": index + 1,
                        "상품명": clean_title,
                        "판매처": mall_name,
                        "링크": item['link']
                    })

            # 요청 기능 1: 비노출 시 알림
            if not found_items:
                st.error(f"⚠️ 현재 '{TARGET_STORE}' 상품이 100위 내에 비노출 중입니다.")
            else:
                st.success(f"✅ 총 {len(found_items)}개의 상품을 발견했습니다!")
                
                # 요청 기능 2: 클릭 시 이동 (가장 확실한 마크다운 테이블 방식)
                # 표 형식으로 예쁘게 보여주면서 링크 클릭이 무조건 작동하게 만듭니다.
                md_table = "| 순위 | 상품명 (클릭 시 이동) | 판매처 |\n| :--- | :--- | :--- |\n"
                for item in found_items:
                    md_table += f"| {item['순위']} | [{item['상품명']}]({item['링크']}) | {item['판매처']} |\n"
                
                st.markdown(md_table)
        else:
            st.error("API 연결 실패. 설정을 확인해주세요.")
