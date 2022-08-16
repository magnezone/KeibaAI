import enum
from os import PathLike
from bs4 import BeautifulSoup
import glob
import requests
import csv
import re
import lightgbm as lgb
import pandas as pd
import numpy as np

netkeiba = r"https://db.netkeiba.com"
path = r"https://race.netkeiba.com/race/shutuba.html?race_id=202204030212"

model1 = lgb.Booster(model_file = "model_clusterring.txt")
model2 = lgb.Booster(model_file = "model_regression2.txt")

jockeys = {}
with open(r"Dataset/Jockey.csv") as f:
    reader = csv.reader(f)
    reader.__next__()
    for row in reader:
        s = row[1].replace(" ","")
        jockeys[s] = int(row[0])

columns = ["race_type","length","age","sex","burden","jockey","horse_number","head_count",
            "horse_weight","horse_weight_diff","prev_head_count","prev_horse_number","prev_prize",
            "prev_race_type","prev_length","prev_time","prev_time_diff","prev_last3f","prev_result",
            "preprev_head_count","preprev_horse_number","preprev_prize",
            "preprev_race_type","preprev_length","preprev_time","preprev_time_diff",
            "preprev_last3f","preprev_result","race_count","win2_ratio","legquality"]

date = 0
race_num = 0
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
legquality = 0

#"日付","レース番号","種類","距離","年齢","性別","斤量","騎手","馬番","頭数","馬体重",
#"単勝オッズ","着順","前走頭数","前走馬番","前走優勝金額","前走種類","前走距離","前走タイム",
#"前走タイム差","前走後3Fタイム","前走着順","前々走頭数","前々走馬番","前々走優勝金額",
#"前々走種類","前々走距離","前々走タイム","前々走タイム差","前々走後3Fタイム",
#"前々走着順","レース回数","連対率"

data = []

res = requests.get(path)
res.encoding = res.apparent_encoding
soup = BeautifulSoup(res.text,"html.parser")
date = soup.find("dd",class_="Active").find("a").text
race_num = path[-12:]
race_type = soup.find("div",class_="RaceData01").findAll("span")[0].text[1]
if(race_type == "ダ"):
    race_type = "ダート"
length = soup.find("div",class_="RaceData01").findAll("span")[0].text[1:]
length = re.search(r"\d{4}m",length).group()[:-1]
head_count = soup.find("div",class_="RaceData02").findAll("span")[7].text
head_count = int(re.search(r"\d+頭",head_count).group()[:-1])
elements = soup.find("div",class_="RaceTableArea").findAll("tr",class_="HorseList")
for element in elements:
    try: 
        line = element.findAll("td")
        horse_number = line[1].text
        sex = line[4].text[0]
        age = line[4].text[1:]
        burden = line[5].text
        jockey = line[6].text[1:-1]
        if(jockey == "Ｍデムーロ" ):
            jockey = "Ｍ．デム"
        for i in jockeys:
            if(re.match(jockey,i) != None):
                if(jockey == re.match(jockey,i).group()):
                    jockey = i
                    break
        print(jockey)
        win_odds = line[9].text
        horse_weight = line[8].text[1:-1]
        horse_detail = line[3].find("a")
        res = requests.get(horse_detail.get("href"))
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text,"html.parser")
        table = soup.find("table",class_="db_h_race_results nk_tb_common")
        horse_elements = table.findAll("tr")
        place_number = 0
        flag = 0
        legquality = soup.find("table",class_="tekisei_table").findAll("tr")[2].findAll("img")[1].get("width")
        for horse_element in horse_elements[1:]:
            try:
                horse_line = horse_element.findAll("td")
                if(flag == 0):
                    prev_result = horse_line[11].text
                    prev_head_count = horse_line[6].text
                    prev_horse_number = horse_line[8].text
                    if(horse_line[14].text[0] == "ダ"):
                            prev_race_type = "ダート"
                    else:
                        prev_race_type = horse_line[14].text[0]
                    prev_length = horse_line[14].text[1:]
                    prev_time = "0"+horse_line[17].text
                    prev_time_diff = horse_line[18].text
                    prev_last3f = float(horse_line[22].text)
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
                    preprev_time = "0"+horse_line[17].text
                    preprev_time_diff = horse_line[18].text
                    preprev_last3f = float(horse_line[22].text)
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
            except:
                print("horse_error")
        race_count = flag
        if(race_count < 2):
            continue
        win2_ratio = place_number/race_count
        column = [date,race_num,race_type,length,age,sex,burden,jockey,horse_number,head_count,horse_weight,
            win_odds,result,prev_head_count,prev_horse_number,prev_prize,prev_race_type,
            prev_length,prev_time,prev_time_diff,prev_last3f,prev_result,preprev_head_count,preprev_horse_number,preprev_prize,preprev_race_type,
            preprev_length,preprev_time,preprev_time_diff,preprev_last3f,preprev_result,race_count,win2_ratio,legquality]
        data.append(column)
        print(column)
    except Exception as e:
        print("race_error")
        print(e)

x_data = []
y_data = []
for row in data:
    try:
        line = []
        #種類
        #芝＝１，ダート＝２
        if(row[2] == "芝"):
            line.append(1)
        elif(row[2] == "ダート"):
            line.append(2)
        else:
            continue
        #距離
        line.append(float(row[3]))
        #年齢
        line.append(float(row[4]))
        #性別
        #牡，セ＝１，牝＝２
        if(row[5] == "牝"):
            line.append(2)
        else:
            line.append(1)
        #斤量
        line.append(float(row[6]))
        #騎手
        if(row[7] in jockeys):
            line.append(jockeys[row[7]])
        else:
            line.append(-1)
        #馬番
        line.append(float(row[8]))
        #頭数
        line.append(float(row[9]))
        #馬体重
        line.append(float(row[10][0:3]))
        #体重増加量
        try:
            line.append(float(row[10][4:-1]))
        except:
            try:
                line.append(float(row[10][5:-1]))
            except:
                line.append(0)
        #単勝オッズ
        #line.append(float(row[11]))
        #前走頭数
        line.append(float(row[13]))
        #前走馬番
        line.append(float(row[14]))
        #前走優勝賞金
        line.append(float(row[15].replace(",","")))
        #前走種類
        #芝＝１，ダート＝２
        if(row[16] == "芝"):
            line.append(1)
        elif(row[16] == "ダート"):
            line.append(2)
        else:
            line.append(3)
        #前走距離
        line.append(float(row[17]))
        #前走タイム
        time = 60*int(row[18][1])+float(row[18][3:])
        line.append(time)
        #前走タイム差
        line.append(float(row[19]))
        #前走後3Fタイム
        line.append(float(row[20]))
        #前走着順
        line.append(float(row[21]))
        #前々走頭数
        line.append(float(row[22]))
        #前々走馬番
        line.append(float(row[23]))
        #前々走優勝賞金
        line.append(float(row[24].replace(",","")))
        #前々走種類
        #芝＝１，ダート＝２，障害＝３
        if(row[25] == "芝"):
            line.append(1)
        elif(row[25] == "ダート"):
            line.append(2)
        else:
            line.append(3)
        #前々走距離
        line.append(float(row[26]))
        #前々走タイム
        time = 60*int(row[27][1])+float(row[27][3:])
        line.append(time)
        #前々走タイム差
        line.append(float(row[28]))
        #前々走後3Fタイム
        line.append(float(row[29]))
        #前々走着順
        line.append(float(row[30]))
        #レース回数
        line.append(float(row[31]))
        #連対率
        line.append(float(row[32]))
        #脚質
        line.append(int(row[33]))
        #入力データ
        x_data.append(line)
        y_data.append(int(row[12]))
    except:
        print("error")

df = pd.DataFrame(x_data,columns=columns)
y_pred = model1.predict(df,num_iteration=model1.best_iteration)
srt = np.argsort(-y_pred[:,0])
res = [int(x_data[i][6]) for i in srt]
probability = [round(y_pred[i,0]*100/np.sum(y_pred[:,0]),2) for i in srt]
print(res)
print(probability)
print(y_pred[:,0])

y_all = dict()
for i,j in enumerate(res):
    y_all[j] = i

y_pred = model2.predict(df,num_iteration=model2.best_iteration)
srt = np.argsort(y_pred)
res = [int(x_data[i][6]) for i in srt]
print(res)
print(y_pred)

for i,j in enumerate(res):
    y_all[j] += i

print(sorted(y_all.items(),key=lambda x:x[1]))