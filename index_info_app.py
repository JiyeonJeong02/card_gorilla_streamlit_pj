import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
from elastic_api import search_index, search_index_with_date_range
import requests
# 트러블슈팅 1) category의 benefit까지 뎁스를 들어갈 수 없어 크롤링으로 해결하는것으로 방향을 전환
# BeautifulSoup을 이용하여 웹피이지의 HTML 파싱을 시도
from bs4 import BeautifulSoup

def get_html_from_url(url):
    try:
        # URL에 GET 요청을 보냅니다
        response = requests.get(url)
        
        # 요청이 성공적이었는지 확인합니다
        response.raise_for_status()
        
        # 응답의 텍스트(HTML)를 반환합니다
        return response.text
    except requests.RequestException as e:
        print(f"에러 발생: {e}")
        return None

st.title("엘라스틱서치에 저장된 인덱스 조회") 
st.markdown(
    """     <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{width:250px;}     </style>
    """, unsafe_allow_html=True )

# card 데이터에 맞게 인덱스명과 필드명 변경 (ex. stock_info -> card_info)
st.sidebar.header("조회하고 싶은 인덱스명을 입력하세요")
index_name = st.sidebar.text_input('인덱스명', value="card_info").lower()
field_name = st.sidebar.text_input('필드명', value="category.class")
match_name = st.sidebar.text_input('조회하려는 내용', value="할인")
# 버튼 클릭했을때 이벤트를 트리거하기 위한 플래그 "clicked1"
clicked1 = st.sidebar.button("해당 정보 확인")

# category 필드 형식 변환 함수 생성
def process_category(category):
    if isinstance(category, list):
        return [{'class': c.get('class', ''), 'benefit': c.get('benefit', '')} for c in category]
    return []

if(clicked1 == True):
    result = search_index(index_name, field_name, match_name)     
    #st.write(result.to_dict()["hits"]["hits"])

    source_data = [entry["_source"] for entry in result.to_dict()["hits"]["hits"]]
    df = pd.DataFrame(source_data)
    
    df['category'] = df['category'].apply(process_category)
    
    # 'card_link'를 이용한 HTML 페이지의 카드 이미지 불러오기
    for i in range(len(df)):
        url = df['card_link'][i]
        html_content = get_html_from_url(url)

        if html_content:
            # BeautifulSoup 객체 생성
            soup = BeautifulSoup(html_content, 'html.parser')

            # og:image 메타 태그 찾기
            og_image = soup.find('meta', property='og:image')
            og_desc = soup.find('meta', property='og:description')

            # 태그가 존재하면 content 속성 값 출력
            if og_image:
                image_url = og_image['content']
                desc = og_desc['content']
                #트러블 슈팅 2) 카드 혜택 키워드를 분리하기 위해 ","를 기준으로 하니 '6,000원'도 분리가 됐었음
                # desc = desc.split(", ")와 같이 ","뒤에 띄어쓰기를 추가하여 금액 단위 구분은 분리되지 않도록 해결함
                desc = desc.split(", ")
                #st.image(image_url, width=150)
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f'<a href="{url}" target="_blank"><img src="{image_url}" style="width: 250px; height: auto;"></a>', unsafe_allow_html=True)
                    # st.markdown(f'<a href="{url}" target="_blank"><img src="{image_url}" width="250"></a>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<p style="font-size: 20px; font-weight: bold;">{df["card_name"][i]}</p>', unsafe_allow_html=True)
                    for j in desc:
                        st.text(j)
                st.text('\n')

            else:
                print("og:image 메타 태그를 찾을 수 없습니다.")
        else:
            print("HTML을 가져오는 데 실패했습니다.")
    
    # 검색 결과 표로 생성
    category_data = []
    for _, row in df.iterrows():
        for category in row['category']:
            category_data.append({
                'card_name': row['card_name'],
                'category_class': category['class'],
                'category_benefit': category['benefit']
            })
    
    category_df = pd.DataFrame(category_data)
    
    st.write("카드 기본 정보:")
    st.dataframe(df.drop('category', axis=1))
    
    st.write("카드 카테고리 정보:")
    st.dataframe(category_df)


# Kibana 대쉬보드 로드 버튼 추가
clicked2 = st.sidebar.button("Kibana 대쉬보드 로드")

# Kibana 대쉬보드 iframe
iframe_code = '''
<iframe src="http://localhost:5601/app/dashboards#/view/7ddb280d-fb4b-4ca5-ad33-b384cda13b30?_g=(refreshInterval%3A(pause%3A!t%2Cvalue%3A60000)%2Ctime%3A(from%3A'2017-07-31T01%3A33%3A56.307Z'%2Cto%3Anow))&show-query-input=true&show-time-filter=true" height="600" width="800" style="border:none;"></iframe>
'''

# 버튼 클릭 시 대쉬보드 로드
if clicked2:
    st.markdown(iframe_code, unsafe_allow_html=True)


#     # 발전 방향성
#     # 사이드바에서 -> 카드순위 실시간 확인
#     # 
#     # 사이드바에 선택 옵션 만들기
# option1 = st.sidebar.selectbox(
#     '실시간 카드 순위 TOP 100',
#     ('신용카드','체크카드')
# )

# option2 = st.sidebar.selectbox(
#     '혜택별 인기차트 TOP 10',
#     ('통신+공과금','주유+차량정비', '항공마일리지', '첨심+교통', '구독+스트리밍',
#      '해외직구', '배달앱+간편결제','편의점+카페', '마트+교육비', '여행+바우처', '제휴/PLCC','증권사CMA')
# )