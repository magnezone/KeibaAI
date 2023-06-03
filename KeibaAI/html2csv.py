from os import PathLike, name
from bs4 import BeautifulSoup
import glob
import requests
import csv
import os
import pandas as pd
import re
import sys

netkeiba = "https://db.netkeiba.com"
root = os.path.dirname(os.path.abspath(__file__))

columns_name = ["日付","レース番号","レース種類","方向","レース距離","天候","馬場",
               "着順","枠番","馬番","年齢","性別","斤量","騎手","タイム","着差","通過","上り",
               "単勝オッズ","人気","馬体重","優勝賞金"]
row_data = [pd.DataFrame(columns=columns_name,index=[-1]) for i in range(3)]
row_data.append(pd.DataFrame(columns=["総レース数","連対率","脚質"],index=[-1]))

output = None

for year in range(2010,2022):
    for month in range(1,13):
        files = glob.glob(root+"\\Dataset\\重賞201001-202112\\"+str(year)+"\\"+str(month)+"\\*.html")
        for file_ in files:
            with open(file_,encoding="euc-jp") as f:
                html = f.read()
            soup = BeautifulSoup(html,"html.parser")
            date = soup.find("li",class_="result_link").find("a").text[0:10]
            date = date.translate(str.maketrans({"年":"/","月":"/"}))
            row_data[0]["日付"] = date
            table = soup.find("table",class_="race_table_01 nk_tb_common")
            elements = table.findAll("tr")
            row_data[0]["レース番号"] = os.path.split(file_)[1][:-5]
            a = soup.select_one("#main > div > div > div > diary_snap > div > div > dl > dd > p > diary_snap_cut > span")
            row_data[0]["レース種類"] = a.text[0]
            row_data[0]["方向"] = a.text[1]
            row_data[0]["レース距離"] = re.search(r"\d+m",a.text).group()[:-1]
            b = re.search(r"/\xa0天候 : .{1,2}\xa0/",a.text).group()
            row_data[0]["天候"] = re.search(r" .{1,2}\xa0",b).group()[1:-1]
            b = re.search(r"/\xa0(芝|ダート) : .{1,2}\xa0/",a.text).group()
            row_data[0]["馬場"] = re.search(r" .{1,2}\xa0",b).group()[1:-1]
            win_prize = elements[1].findAll("td")[20].text
            for element in elements[1:]:
                try: 
                    line = element.findAll("td")
                    row_data[0]["着順"] = int(line[0].text)
                    row_data[0]["枠番"] = int(line[1].text)
                    row_data[0]["馬番"] = int(line[2].text)
                    horse_name = line[3].text[1:-1]
                    print(horse_name)
                    row_data[0]["年齢"] = int(line[4].text[1])
                    row_data[0]["性別"] = line[4].text[0]
                    row_data[0]["斤量"] = float(line[5].text)
                    row_data[0]["騎手"] = line[6].text[1:-1]
                    row_data[0]["タイム"] =line[7].text
                    row_data[0]["着差"] = line[8].text
                    row_data[0]["通過"] = line[10].text
                    row_data[0]["上り"] = line[11].text
                    row_data[0]["単勝オッズ"] = line[12].text
                    row_data[0]["人気"] =line[13].text
                    row_data[0]["馬体重"] = line[14].text
                    row_data[0]["優勝賞金"] = win_prize
                    horse_detail = line[3].find("a")
                    res = requests.get(netkeiba+horse_detail.get("href"))
                    res.encoding = res.apparent_encoding
                    soup = BeautifulSoup(res.text,"html.parser")
                    table = soup.find("table",class_="db_h_race_results nk_tb_common")
                    horse_elements = table.findAll("tr")
                    place_number = 0
                    flag = -1
                    row_data[3]["脚質"] = soup.find("table",class_="tekisei_table").findAll("tr")[2].findAll("img")[1].get("width")
                    for horse_element in horse_elements[1:]:
                        try:
                            horse_line = horse_element.findAll("td")
                            if(flag > -1):
                                if(flag == 0 or flag == 1):
                                    index = flag+1
                                    race_detail = horse_line[4].find("a")
                                    res = requests.get(netkeiba+race_detail.get("href"))
                                    res.encoding = res.apparent_encoding
                                    soup = BeautifulSoup(res.text,"html.parser")
                                    date2 = soup.find("li",class_="result_link").find("a").text[0:10]
                                    date2 = date2.translate(str.maketrans({"年":"/","月":"/"}))
                                    row_data[index]["日付"] = date2
                                    table = soup.find("table",class_="race_table_01 nk_tb_common")
                                    elements = table.findAll("tr")
                                    row_data[index]["レース番号"] = os.path.split(file_)[1][:-5]
                                    a = soup.select_one("#main > div > div > div > diary_snap > div > div > dl > dd > p > diary_snap_cut > span")
                                    row_data[index]["レース種類"] = a.text[0]
                                    row_data[index]["方向"] = a.text[1]
                                    row_data[index]["レース距離"] = re.search(r"\d+m",a.text).group()[:-1]
                                    b = re.search(r"/\xa0天候 : .{1,2}\xa0/",a.text).group()
                                    row_data[index]["天候"] = re.search(r" .{1,2}\xa0",b).group()[1:-1]
                                    b = re.search(r"/\xa0(芝|ダート) : .{1,2}\xa0/",a.text).group()
                                    row_data[index]["馬場"] = re.search(r" .{1,2}\xa0",b).group()[1:-1]
                                    element = table.find(name="a",text=horse_name).parent.parent
                                    line = element.findAll("td")
                                    row_data[index]["着順"] = int(line[0].text)
                                    row_data[index]["枠番"] = int(line[1].text)
                                    row_data[index]["馬番"] = int(line[2].text)
                                    row_data[index]["年齢"] = int(line[4].text[1])
                                    row_data[index]["性別"] = line[4].text[0]
                                    row_data[index]["斤量"] = float(line[5].text)
                                    row_data[index]["騎手"] = line[6].text[1:-1]
                                    row_data[index]["タイム"] =line[7].text
                                    row_data[index]["着差"] = line[8].text
                                    row_data[index]["通過"] = line[10].text
                                    row_data[index]["上り"] = line[11].text
                                    row_data[index]["単勝オッズ"] = line[12].text
                                    row_data[index]["人気"] =line[13].text
                                    row_data[index]["馬体重"] = line[14].text
                                    row_data[index]["優勝賞金"] =elements[1].findAll("td")[20].text
                                else:
                                    try:
                                        if(int(horse_line[11].text) <= 3):
                                            place_number += 1
                                    except:
                                        flag -= 1
                                flag += 1
                            elif(horse_line[0].text == date):
                                flag += 1
                        except Exception as e:
                            print("horse_error")
                            print(e)
                    race_count = flag
                    if(race_count == 0):
                        raise ZeroDivisionError
                    win2_ratio = place_number/race_count
                    row_data[3]["総レース数"] = race_count
                    row_data[3]["連対率"] = win2_ratio
                    r1 = row_data[1].add_prefix("前走")
                    r2 = row_data[2].add_prefix("前前走")
                    a = pd.concat([row_data[0],r1,r2,row_data[3]],axis=1)  
                    if(type(output) == type(None)):
                        output = a.copy()
                    else:
                        output = pd.concat([output,a],axis=0,ignore_index=True)                        
                except Exception as e:
                    print("race_error")
                    print(e)
output.to_csv(root+"\\Dataset\\重賞データ.csv",header=True,index=False)
            

                        


