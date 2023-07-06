from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import argparse
import warnings
import time
import re
from datetime import datetime, timedelta
import pandas as pd

warnings.filterwarnings('ignore')
CHROME_DRIVER_PATH = 'C:/Workspace/7. API/Driver/chromedriver.exe'  # 크롬드라이버 경로 지정

def crawling_opentalk(driver, sub_soup, result_list, last_item_key, date_key, month, day):
    # 오픈톡 내용을 크롤링 하는 코드

    while True:
        ## class = date의 키값은 xxxxx.9001이라서, xxxxx부분만 추출하고, 댓글의 키값이 xxxxx이면 날짜를 하루 전으로 돌림
        if last_item_key == date_key:
            month, day = get_previous_day(month, day)

        find_result = sub_soup.find_all("div", {"data-item-key":last_item_key})     # find_all의 길이가 0 = 그 키값의 댓글이 없음 -> 페이지업을 눌러서 새로운 댓글을 불러와야함
        
        if len(find_result) != 0:
            try:
                message_findall = sub_soup.find("div", {"data-item-key":last_item_key}).find_all("span", {"class":"bubble_message"})
                # 메세지의 경우 3가지 종류가 있음.
                ## 1. 이모티콘일 경우 -> bubble_message가 없어서 길이가 0
                ## 2. 평범한 댓글
                ## 3. 남의 댓글에 대한 답글 <- 이경우는 bubble_message가 2개라서 마지막거를 불러와야함.
                if len(message_findall) == 0:   # 이모티콘일 경우 예외처리해서 다음으로 넘김.
                    raise Exception('이모티콘.')
                else:
                    message = message_findall[-1].text.strip()
                    
                # 닉네임 : 이어진 댓글일 경우 닉네임이 비어있음 -> 이 경우는 None으로 처리하고 나중에 fill_none 함수를 사용해서 빈 닉네임 채워줌
                try:
                    nickname = sub_soup.find("div", {"data-item-key":last_item_key}).find("em", {"class":"nickname"}).text.strip()
                except:
                    nickname = None
                # 시간 : "오후 aa:bb" 형식으로 추출되는데 change_time_Format 함수로 형식을 바꿔줌.
                writing_time = sub_soup.find("div", {"data-item-key":last_item_key}).find("span", {"class":"info_writing_time"}).text.strip()
                formatted_time = change_time_format(month, day, writing_time)
                result_list.append([last_item_key, nickname, formatted_time, message])
                print(last_item_key)
                last_item_key -= 1
            except Exception as b:
                last_item_key -= 1
                # continue
        else:
            # 키값의 댓글이 없을때, 페이지업을 눌러서 화면을 올려서 새로 댓글을 불러오고, 새로운 sub_soup 선언
            for i in range(7):
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_UP)
            time.sleep(1)
            sub_soup = BeautifulSoup(driver.page_source, "html.parser")
            return sub_soup, result_list, last_item_key, month, day
        
def get_previous_day(month, day):
    # 입력된 월과 일을 datetime 객체로 변환
    date = datetime(year=2023, month=month, day=day)

    # 하루 전의 날짜를 계산
    previous_day = date - timedelta(days=1)

    # 하루 전의 월과 일을 출력
    previous_month = previous_day.month
    previous_day = previous_day.day

    return previous_month, previous_day

def change_time_format(month, day, wr_time):
    wr_time = wr_time.replace("오후", "PM").replace("오전","AM")
    # 시간 문자열을 datetime 객체로 변환
    time_obj = datetime.strptime(wr_time, "%p %I:%M")

    # 원하는 날짜 정보 설정
    desired_date = datetime(2023, month, day, time_obj.hour, time_obj.minute)

    # 날짜와 시간을 원하는 형식으로 변환
    formatted_date = desired_date.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    return formatted_date


def fill_none(temp_list):
    # 닉네임이 None인 경우, 그 이전에 닉네임이 있는곳 까지 가서 닉네임으로 none값 교체
    i = 0
    while i < len(temp_list)-1:
        if temp_list[i][1] is None:
            j = i + 1
            while j < len(temp_list) and temp_list[j][1] is None:
                j += 1
            if j < len(temp_list):
                nickname = temp_list[j][1]
                temp_list[i][1] = nickname
        i += 1
    return temp_list

def main(main_url : str, count : int) -> list:
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, chrome_options=options)
    driver.maximize_window()    # 전체화면으로 실행


    # 톡 페이지 진입
    driver.get(main_url)
    time.sleep(3)
    
    main_source = driver.page_source
    soup = BeautifulSoup(main_source, "html.parser")
    soup_string = str(soup)

    
    # if 오픈톡 표시가 있으면,
    # 클릭해야할 오픈톡 클래스 이름 찾기
    opentalk_title_pattern = r"TitleOpenTalk_title__\w{5}"
    title_match = re.search(opentalk_title_pattern, soup_string)
    
    if title_match != None:
        driver.find_element(By.CLASS_NAME, title_match[0]).click()
        time.sleep(2)
        ## 새 창으로 전환
        driver.switch_to.window(driver.window_handles[1]) 
        
        driver.find_element(By.CLASS_NAME, "nchat_msg_room").click()
        # if len(driver.find_elements(By.CLASS_NAME, "civ__viewer_class")) != 0:
        #     driver.find_elements(By.CLASS_NAME, "civ__viewer_class").click()
        
        time.sleep(2)
        sub_source = driver.page_source
        sub_soup = BeautifulSoup(sub_source, "html.parser")
        last_item_key = int(sub_soup.find_all("div",{"class":"nchat_msg_item"})[-1].attrs["data-item-key"])
        # print(last_item_key)

        month = int(sub_soup.find("div", {"class":"nchat_msg_date_floating"}).text.split(".")[0])
        day = int(sub_soup.find("div", {"class":"nchat_msg_date_floating"}).text.split(".")[1])

        result_list = list()
        end = last_item_key - int(count)
        while last_item_key > end:
            if len(sub_soup.find_all("div", {"class":"nchat_msg_date item"})) == 1:
                date_key = int(sub_soup.find_all("div", {"class":"nchat_msg_date item"})[0].attrs["data-item-key"].split(".")[0])
            else:
                date_key = -1
            
            sub_soup, result_list, last_item_key, month, day = crawling_opentalk(driver, sub_soup, result_list, last_item_key, date_key, month, day)
            print(last_item_key)
            
        result_list =  fill_none(result_list)
        
        return result_list
    
    else:
        pass

if __name__ == "__main__":
    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--comment_num', required=True)
    args = parser.parse_args()
    result_list = main(args.url, args.comment_num)
    result_df = pd.DataFrame(result_list)
    result_df.columns = ["comment_no","nicname","date","comment"]
    result_df.to_csv("naver_opentalk_result.csv", index = None, encoding = "utf-8-sig")
    end_time = time.time()
    
    total_time = int(end_time - start_time)
    print(f"======================{total_time} 초 걸림 =========================")
    
    # 4시 40분 시작