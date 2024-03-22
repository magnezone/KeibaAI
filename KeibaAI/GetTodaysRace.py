import requests
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import schedule
import time
from run_clustering_future import get_result
import csv
from FTPtest import sendCSV
import os
import chromedriver_binary

JST = datetime.timezone(datetime.timedelta(hours=+9),'JST')

#このファイルがあるパスを取得
abs_dir = os.path.dirname(os.path.abspath(__file__))

#driver_path
#driver_path = "../../chromedriver_win32/chromedriver"
#seleniumの各種設定
options = Options()
options.add_argument('--headless')    # ヘッドレスモードに
#service = Service(executable_path = driver_path)
print(abs_dir+r"/chromedriver")
driver = webdriver.Chrome(executable_path=abs_dir+r"/chromedriver",options=options) 
#アクセス間隔：1s
wait = WebDriverWait(driver,1000)

def todayDateString():
    today = datetime.datetime.now(JST)
    month = today.month
    day = today.day
    weekday = today.weekday()
    if(weekday == 5):
        weekday = "土"
    elif(weekday == 6):
        weekday = "日"
    else:
        return "3月17日(日)"
        return None
    res = str(month) + "月" + str(day) + "日" + "(" + weekday + ")"
    return res

#hh:mmから40分引いた時間を出力
def getSettingTime(run_time):
    a = datetime.datetime.now(JST)
    a = a.replace(hour = int(run_time[0:2]),minute = int(run_time[3:]))
    b = a - datetime.timedelta(minutes=40)
    res = b.strftime('%H:%M')
    return res

def getTodayRaceDetails():
    url1 = "https://race.netkeiba.com/top/"
    driver.get(url1)
    dateListSub = driver.find_element(By.ID,"date_list_sub")
    a = dateListSub.find_elements(By.CLASS_NAME,"ui-tabs-anchor")
    raceData = [["" for j in range(3)] for i in range(13)]
    for i in a:
        print(i.text,todayDateString())
        if(i.text == todayDateString()):
            html = requests.get(i.get_attribute("href"))
            html.encoding = html.apparent_encoding
            soup = BeautifulSoup(html.text,"html.parser")
            raceList = soup.find_all("dl",class_="RaceList_DataList")
            raceCourceNum = len(raceList)
            raceData = [["" for j in range(raceCourceNum)] for i in range(13)]
            for j in range(raceCourceNum):
                raceTimes = raceList[j].find_all("span",class_="RaceList_Itemtime") 
                raceUrls = raceList[j].find_all("a",class_="")
                for k in range(13):
                    setting_time = getSettingTime(raceTimes[k-1].text[:-1])
                    print(setting_time)
                    url = "https://race.netkeiba.com/"+raceUrls[k-1]["href"].replace("result","shutuba")[3:-13]
                    print(url,k,j)
                    if(k == 0):
                        raceData[k][j] = raceList[j].find("p",class_="RaceList_DataTitle").text.split(" ")[1]
                    elif(todayDateString()[-2:-1] == "土"):
                        schedule.every().saturday.at(setting_time).do(get_result,path = url,row_num = k,column_num = j,location = raceData[0][j])
                    elif(todayDateString()[-2:-1] == "日"):
                        schedule.every().sunday.at(setting_time).do(get_result,path = url,row_num = k,column_num = j,location = raceData[0][j])
            break
    with open("race.csv","w",newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(raceData)
    sendCSV()
    
if __name__ == "__main__":
    getTodayRaceDetails()
    while(True):
        print(schedule.idle_seconds())
        if(schedule.idle_seconds() == None):
            break
        elif(int(schedule.idle_seconds()) > 86400):
            schedule.run_all()
            break
        schedule.run_pending()
        time.sleep(1)