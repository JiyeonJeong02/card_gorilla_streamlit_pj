# card_gorilla_streamlit_pj
Implementation of CardGorilla Website Crawling and Streamlit Application Utilizing Kibana Dashboards

---
**트러블슈팅 1)** category의 benefit까지 뎁스를 들어갈 수 없어 크롤링으로 해결하는것으로 방향을 전환
- BeautifulSoup을 이용하여 웹피이지의 HTML 파싱을 시도

**트러블 슈팅 2)** 카드 혜택 키워드를 분리하기 위해 ","를 기준으로 하니 '6,000원'도 분리가 됐었음
- desc = desc.split(", ")와 같이 ","뒤에 띄어쓰기를 추가하여 금액 단위 구분은 분리되지 않도록 해결함

**향후 발전 방향**
- 사이드바에서 -> 카드순위 실시간 확인
- 사이드바에 선택 옵션 만들기
```
 option1 = st.sidebar.selectbox(
     '실시간 카드 순위 TOP 100',
     ('신용카드','체크카드')
 )

 option2 = st.sidebar.selectbox(
     '혜택별 인기차트 TOP 10',
     ('통신+공과금','주유+차량정비', '항공마일리지', '첨심+교통', '구독+스트리밍',
      '해외직구', '배달앱+간편결제','편의점+카페', '마트+교육비', '여행+바우처', '제휴/PLCC','증권사CMA')
)
```
