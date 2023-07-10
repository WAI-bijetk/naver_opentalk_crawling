# 네이버 오픈톡 크롤링

## 파일 정보

- naver_opentalk_crawling.py : 네이버 오픈톡을 크롤링하는 코드

- naver_opentalk_result.csv : 예시) "이번 생도 잘부탁해"에서 수집한 댓글

  

## 실행방법

python naver_opentalk_crawling.py --url="수집하려는 드라마 컨텐츠 홈의 오픈톡 url" --comment_num=수집하려는 댓글 개수

Ex. python naver_opentalk_crawling.py --url="https://program.naver.com/p/28694187/talk" --comment_num=1500



## 실행 전 필독사항

1. 13번째  CHROME_DRIVER_PATH 경로 수정

   chromedriver.exe 파일의 경로를 넣어주시면 됩니다.

   크롬의 버전(설정 - chrome 정보)과 드라이버 버전이 맞지 않을 경우 오류가 발생하니 버전이 맞는지 확인이 필요합니다. 

2. 드라마의 네이버 컨텐츠홈의 대표 오픈톡의 내용을 수집합니다.

3. 각 댓글의 고유 번호, 작성자 닉네임, 글 작성 시간, 작성한 글 내용, 총 4가지를 수집한 후, 데이터프레임으로 결과를 리턴합니다.

4. 데이터프레임(csv)파일은 naver_opentalk_crawling.py 파일이 있는 경로에 naver_opentalk_result.csv라는 이름으로 저장.

5. Ryzen7 4800U(8C 16T), 16GB RAM 환경에서 오픈톡 글 10000개 수집 시 1812초 소요
