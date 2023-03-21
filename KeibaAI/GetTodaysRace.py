import requests
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import schedule
import time

raceData = [["" for j in range(3)] for i in range(13)]
print(raceData)
input()

#driver_path
driver_path = r"../../chromedriver_win32/chromedriver"
#seleniumの各種設定
options = Options()
#options.add_argument('--headless')    # ヘッドレスモードに
#ログが出ないように
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(driver_path,chrome_options=options) 
#アクセス間隔：1s
wait = WebDriverWait(driver,1000)

def todayDateString():
    today = datetime.date(2023,3,19)
    month = today.month
    day = today.day
    weekday = today.weekday()
    if(weekday == 5):
        weekday = "土"
    elif(weekday == 6):
        weekday = "日"
    else:
        return None
    res = str(month) + "月" + str(day) + "日" + "(" + weekday + ")"
    return res

def getTodayRaceDetails():
    url1 = "https://race.netkeiba.com/top/"
    driver.get(url1)
    dateListSub = driver.find_element(By.ID,"date_list_sub")
    a = dateListSub.find_elements(By.CLASS_NAME,"ui-tabs-anchor")
    for i in a:
        print(i.text,todayDateString())
        if(i.text == todayDateString()):
            html = requests.get(i.get_attribute("href"))
            html.encoding = html.apparent_encoding
            with open("yahoo_news.html","w",encoding="utf-8")as f:
                f.write(html.text)


            break

if __name__ == "__main__":
    getTodayRaceDetails()