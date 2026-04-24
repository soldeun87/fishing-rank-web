import streamlit as st
import pandas as pd
import requests

# --- [1. 보안 설정] ---
try:
    CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
    MASTER_PASSWORD = st.secrets["APP_PASSWORD"]
except:
    st.error("보안 설정(Secrets)이 완료되지 않았습니다.")
    st.stop()

# --- [2. 화면 구성] ---
st.set_page_config(page_title="피싱템 순위 추적기", layout="wide")
st.title("🎣 피싱템 순위 검색기 (초간편 버전)")

# 비밀번호 확인
pwd = st.text_input("접속 비밀번호를 입력하세요", type="password")
if pwd != MASTER_PASSWORD:
    st.info("비밀번호를 입력하면 검색창이 나타납니다.")
    st.stop()

# 검색창 레이아웃
col1, col2 = st.columns(2)
with col1:
    keyword = st.text_input("검색할 키워드 (예: 타이라바 로드)")
with col2:
    target_store = st.text_input("찾을 상호명", value="피싱템")

if st.button("🚀 순위 수색 시작"):
    if not keyword:
        st.warning("키워드를 입력해주세요.")
    else:
        # 네이버 쇼핑 API 호출 (1~100위 수집)
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
                if target_store in mall_name:
                    # 필요한 정보만 추출 (태그 제거 포함)
                    clean_title = item['title'].replace('<b>', '').replace('</b>', '')
                    found_items.append({
                        "순위": index + 1,
                        "상품명": clean_title,
                        "판매처": mall_name,
                        "링크": item['link'] # 링크 데이터 저장
                    })

            # --- [요청 기능 1: 비노출 시 팝업 알림] ---
            if not found_items:
                st.error(f"⚠️ '{target_store}' 상점의 상품이 100위 내에 비노출 중입니다.")
            else:
                st.success(f"✅ 총 {len(found_items)}개의 상품을 발견했습니다!")
                
                # --- [요청 기능 2: 상품명 클릭 시 페이지 이동] ---
                df = pd.DataFrame(found_items)
                
                # 데이터프레임 시각화 (상품명에 링크 연결)
                st.dataframe(
                    df,
                    column_config={
                        "상품명": st.column_config.LinkColumn(
                            "상품명 (클릭 시 이동)",
                            display_text=r"(.+)", # 상품명 텍스트 그대로 표시
                        ),
                        "링크": None # 링크 컬럼은 숨김 처리
                    },
                    hide_index=True,
                    use_container_width=True
                )
        else:
            st.error("API 연결 실패. 네이버 아이디/시크릿을 확인해주세요.")
