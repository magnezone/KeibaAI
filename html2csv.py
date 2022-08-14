from os import PathLike
from bs4 import BeautifulSoup
import glob
import requests
import csv
import os

netkeiba = r"https://db.netkeiba.com"
root = r"../../Dataset/new/"

#日付,年齢,性別,斤量,騎手,馬番,馬体重,単勝オッズ,前走馬番,前走着順
#前走優勝賞金,前走距離,前走タイム差,前走後3Fタイム,連対率,着順
date = 0
race_number = 0
race_type = 0
length = 0
age = 0
sex = 0
burden = 0
jockey = 0
horse_number = 0
head_count = 0
horse_weight = 0
win_odds = 0
result = 0
time = 0

prev_head_count = 0
prev_horse_number = 0
prev_prize = 0
prev_race_type = 0
prev_length = 0
prev_time = 0
prev_time_diff = 0
prev_last3f = 0
prev_result = 0

preprev_head_count = 0
preprev_horse_number = 0
preprev_prize = 0
preprev_race_type = 0
preprev_length = 0
preprev_time = 0
preprev_time_diff = 0
preprev_last3f = 0
preprev_result = 0

race_count = 0
win2_ratio = 0

LegQuality = 0

data = ["日付","レース番号","種類","距離","年齢","性別","斤量","騎手","馬番","頭数","馬体重","単勝オッズ","着順","タイム","前走頭数","前走馬番","前走優勝賞金","前走種類","前走距離","前走タイム","前走タイム差","前走後3Fタイム","前走着順","前々走頭数","前々走馬番","前々走優勝賞金","前々走種類","前々走距離","前々走タイム","前々走タイム差","前々走後3Fタイム","前々走着順","総レース数","連対率"]

with open(r"../../Dataset/Data1600-500.csv","w",newline = "")as f1:
    writer = csv.writer(f1)
    writer.writerow(data)
    for year in range(2010,2022):
        for month in range(1,13):
            files = glob.glob(root+str(year)+"/"+str(month)+"/*")
            for file_ in files:
                print(file_)
                with open(file_,encoding="euc-jp") as f:
                    html = f.read()
                soup = BeautifulSoup(html,"html.parser")
                date = soup.find("li",class_="result_link").find("a").text[0:10]
                date = date.translate(str.maketrans({"年":"/","月":"/"}))
                table = soup.find("table",class_="race_table_01 nk_tb_common")
                elements = table.findAll("tr")
                race_number = os.path.split(file_)[1][:-5]
                for element in elements[1:]:
                    try: 
                        line = element.findAll("td")
                        result = int(line[0].text)
                        horse_number = line[2].text
                        sex = line[4].text[0]
                        age = line[4].text[1]
                        burden = line[5].text
                        jockey = line[6].text[1:-1]
                        time = line[7].text
                        win_odds = line[12].text
                        horse_weight = line[14].text
                        horse_detail = line[3].find("a")
                        res = requests.get(netkeiba+horse_detail.get("href"))
                        res.encoding = res.apparent_encoding
                        soup = BeautifulSoup(res.text,"html.parser")
                        table = soup.find("table",class_="db_h_race_results nk_tb_common")
                        horse_elements = table.findAll("tr")
                        place_number = 0
                        flag = -1
                        LegQuality = soup.find("table",class_="tekisei_table").findAll("tr")[2].findAll("img")[1].get("width")
                        for horse_element in horse_elements[1:]:
                            try:
                                horse_line = horse_element.findAll("td")
                                if(flag > -1):
                                    if(flag == 0):
                                        prev_result = horse_line[11].text
                                        prev_head_count = horse_line[6].text
                                        prev_horse_number = horse_line[8].text
                                        if(horse_line[14].text[0] == "ダ"):
                                                prev_race_type = "ダート"
                                        else:
                                            prev_race_type = horse_line[14].text[0]
                                        prev_length = horse_line[14].text[1:]
                                        prev_time = horse_line[17].text
                                        prev_time_diff = horse_line[18].text
                                        prev_last3f = horse_line[22].text
                                        if(int(horse_line[11].text) <= 3):
                                            place_number += 1
                                        race_detail = horse_line[4].find("a")
                                        res = requests.get(netkeiba+race_detail.get("href"))
                                        res.encoding = res.apparent_encoding
                                        soup = BeautifulSoup(res.text,"html.parser")
                                        table = soup.find("table",class_="race_table_01 nk_tb_common")
                                        elements = table.findAll("tr")
                                        prev_prize = elements[1].findAll("td")[20].text
                                    elif(flag == 1):
                                        preprev_result = horse_line[11].text
                                        preprev_head_count = horse_line[6].text
                                        preprev_horse_number = horse_line[8].text
                                        if(horse_line[14].text[0] == "ダ"):
                                                preprev_race_type = "ダート"
                                        else:
                                            preprev_race_type = horse_line[14].text[0]
                                        preprev_length = horse_line[14].text[1:]
                                        preprev_time = horse_line[17].text
                                        preprev_time_diff = horse_line[18].text
                                        preprev_last3f = horse_line[22].text
                                        if(int(horse_line[11].text) <= 3):
                                            place_number += 1
                                        race_detail = horse_line[4].find("a")
                                        res = requests.get(netkeiba+race_detail.get("href"))
                                        res.encoding = res.apparent_encoding
                                        soup = BeautifulSoup(res.text,"html.parser")
                                        table = soup.find("table",class_="race_table_01 nk_tb_common")
                                        elements = table.findAll("tr")
                                        preprev_prize = elements[1].findAll("td")[20].text
                                    else:
                                        if(int(horse_line[11].text) <= 3):
                                            place_number += 1
                                    flag += 1
                                if(horse_line[0].text == date):
                                    head_count = horse_line[6].text
                                    if(horse_line[14].text[0] == "ダ"):
                                        race_type = "ダート"
                                    else:
                                        race_type = horse_line[14].text[0]
                                    length = horse_line[14].text[1:]
                                    flag += 1
                            except:
                                print("horse_error")
                                pass
                        race_count = flag
                        win2_ratio = place_number/race_count
                        column = [date,race_number,race_type,length,age,sex,burden,jockey,horse_number,head_count,
                              horse_weight,win_odds,result,time,prev_head_count,prev_horse_number,prev_prize,
                              prev_race_type,prev_length,prev_time,prev_time_diff,prev_last3f,prev_result,
                              preprev_head_count,preprev_horse_number,preprev_prize,preprev_race_type,preprev_length,
                              preprev_time,preprev_time_diff,preprev_last3f,preprev_result,race_count,win2_ratio,LegQuality]
                        print(column)
                        writer.writerow(column)
                    except:
                        print("race_error")