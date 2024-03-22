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
import os
from FTPtest import sendCSV,downloadCSV
import schedule
import time
import datetime

def convert_date(date:str):
    res = ""
    results = re.findall("\d+",date)
    for i in range(len(results)):
        if(len(results[i]) < 2):
            results[i] = "0"+ results[i]
        res += results[i]
    return res

abs_dir = os.path.dirname(os.path.abspath(__file__))

netkeiba = r"https://db.netkeiba.com"

model1 = lgb.Booster(model_file = abs_dir + r"\Dataset\model.txt")

loop_is = True

jockeys = {}
with open(abs_dir +  r"\Dataset\Jockey.csv",encoding="utf-8") as f:
    reader = csv.reader(f)
    reader.__next__()
    for row in reader:
        s = row[1].replace(" ","")
        jockeys[s] = int(row[0])

netkeiba = "https://db.netkeiba.com"
root = os.path.dirname(os.path.abspath(__file__))

columns_name = ["日付","レース番号","レース種類","方向","レース距離","天候","馬場",
               "着順","枠番","馬番","年齢","性別","斤量","騎手","タイム","着差","通過","上り",
               "単勝オッズ","人気","馬体重","優勝賞金","頭数"]
row_data = [pd.DataFrame(columns=columns_name,index=[-1]) for i in range(3)]
row_data.append(pd.DataFrame(columns=["総レース数","連対率","脚質"],index=[-1]))

def get_predict(path):
    print(path)
    output = None
    while(True):
        try:
            res = requests.get(path)
            break
        except:
            "Request Error"
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text,"html.parser")
    date = soup.find("dd",class_="Active")
    date = path[52:56]+"年"+date.text[:-4]

    first_date = datetime.datetime.strptime(date,"%Y年%m月%d").strftime("%Y/%m/%d")
    row_data[0]["日付"] = first_date
    a = soup.find("div",class_="RaceData01")
    row_data[0]["レース番号"] = "a"
    direction1 = a.text.find("右")
    direction2 = a.text.find("左")
    if(direction1 != -1):
        row_data[0]["方向"] = "左"
    elif(direction2 != -1):
        row_data[0]["方向"] = "右"
    else:
        row_data[0]["方向"] = "直"
    text = a.text.replace("\n","")
    row_data[0]["レース種類"] = re.search(r".\d+m",text).group()[0]
    row_data[0]["レース距離"] = re.search(r"\d+m",text).group()[:-1]
    b = re.search(r"天候:.+/",text).group()
    row_data[0]["天候"] = re.search(r":.{1,2}/",b).group()[1:-1]
    b = re.search(r"馬場:.+",text).group()
    if(re.search(r":.{1,2}",b).group()[1:] == "稍"):
        row_data[0]["馬場"] = "稍重"
    elif(re.search(r":.{1,2}",b).group()[1:] == "不"):
        row_data[0]["馬場"] = "不良"
    else:
        row_data[0]["馬場"] = re.search(r":.{1,2}",b).group()[1:] 
    a = soup.find("div",class_="RaceData02")
    a = a.find_all("span")
    win_prize = re.search(r":\d+,",a[8].text).group()[1:-1]
    horse_num = int(a[7].text[:-1])
    table = soup.find("div",class_="RaceTableArea")
    elements = table.find_all("tr")
    for element in elements[2:]:
        try: 
            line = element.findAll("td")
            row_data[0]["枠番"] = int(line[0].text)
            row_data[0]["馬番"] = int(line[1].text)
            horse_name = line[3].text[3:-3]
            print(horse_name)
            row_data[0]["年齢"] = int(line[4].text[1])
            row_data[0]["性別"] = line[4].text[0]
            row_data[0]["斤量"] = float(line[5].text)
            row_data[0]["騎手"] = line[6].text[1:-1]
            row_data[0]["馬体重"] = line[8].text[1:-1]
            row_data[0]["優勝賞金"] = win_prize
            row_data[0]["頭数"] = horse_num
            horse_detail = line[3].find("a")
            res = requests.get(horse_detail.get("href"))
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text,"html.parser")
            table = soup.find("table",class_="db_h_race_results nk_tb_common")
            horse_elements = table.findAll("tr")
            place_number = 0
            flag = -1
            second_date = horse_elements[1].findAll("td")[0].text
            f_first_date = time.strptime(first_date,"%Y/%m/%d")
            f_second_date = time.strptime(second_date,"%Y/%m/%d")
            if(f_first_date > f_second_date):
                flag = 0
            row_data[3]["脚質"] = soup.find("table",class_="tekisei_table").findAll("tr")[2].findAll("img")[1].get("width")
            for horse_element in horse_elements[1:]:
                try:
                    horse_line = horse_element.findAll("td")
                    if(flag > -1):
                        if(flag == 0 or flag == 1):
                            index = flag+1
                            horse_num = int(horse_line[6].text)
                            race_detail = horse_line[4].find("a")
                            res = requests.get(netkeiba+race_detail.get("href"))
                            res.encoding = res.apparent_encoding
                            soup = BeautifulSoup(res.text,"html.parser")
                            date2 = re.search("\d+年\d+月\d+日",soup.find("p",class_="smalltxt").text).group()
                            date2 = datetime.datetime.strptime(date2,"%Y年%m月%d日").strftime("%Y/%m/%d")
                            row_data[index]["日付"] = date2
                            table = soup.find("table",class_="race_table_01 nk_tb_common")
                            elements = table.findAll("tr")
                            row_data[index]["レース番号"] = "b"
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
                            row_data[index]["頭数"] = horse_num
                            try:
                                if(int(horse_line[11].text) <= 3):
                                    place_number += 1
                            except:
                                flag -= 1
                        else:
                            try:
                                if(int(horse_line[11].text) <= 3):
                                    place_number += 1
                            except:
                                flag -= 1
                        flag += 1
                    elif(horse_line[0].text == first_date):
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
    columns = output

    for i in columns.index:
        flag = False
        if(columns.at[i,"レース種類"] in ["障","Φ"]):
            flag = True
        elif(columns.at[i,"前走レース種類"] in ["障","Φ"]):
            flag = True
        elif(columns.at[i,"前前走レース種類"] in ["障","Φ"]):
            flag = True
        elif(columns.at[i,"方向"] == "直"):
            flag = True
        elif(columns.at[i,"前走方向"] == "直"):
            flag = True
        elif(columns.at[i,"前前走方向"] == "直"):
            flag = True
        elif(columns.at[i,"天候"] == " "):
            flag = True
        elif(columns.at[i,"前走天候"] == " "):
            flag = True
        elif(columns.at[i,"前前走天候"] == " "):
            flag = True
        elif(columns.at[i,"馬体重"] == "計不"):
            flag = True
        elif(columns.at[i,"前走馬体重"] == "計不"):
            flag = True
        elif(columns.at[i,"前前走馬体重"] == "計不"):
            flag = True
        if(flag):
            columns = columns.drop(i)

    columns.insert(0,"体重増加量",0)
    columns.insert(0,"前走体重増加量",0)
    columns.insert(0,"前前走体重増加量",0)

    for i in columns.index:
        for j in ["","前走","前前走"]:

            if(columns.at[i,j+"騎手"] == "Ｍデムーロ" ):
                columns.at[i,j+"騎手"] = "Ｍ．デム"
            if(type(columns.at[i,j+"騎手"]) == type(str)):
                for k in jockeys:
                    if(re.match(columns.at[i,j+"騎手"],k) != None):
                        if(columns.at[i,j+"騎手"] == re.match(columns.at[i,j+"騎手"],k).group()):
                            columns.at[i,j+"騎手"] = k
                            break
            #騎手
            if(columns.at[i,j+"騎手"] in jockeys):
                columns.at[i,j+"騎手"] = jockeys[columns.at[i,j+"騎手"]]
            else:
                columns.at[i,j+"騎手"] = -1
            a = ["芝","ダ"]
            columns.at[i,j+"レース種類"] = a.index(columns.at[i,j+"レース種類"])
            a = ["右","左"]
            columns.at[i,j+"方向"] = a.index(columns.at[i,j+"方向"])
            a = ['晴','曇','雨','小雨','小雪','雪']
            columns.at[i,j+"天候"] = a.index(columns.at[i,j+"天候"])
            a = ['良','稍重','不良','重']
            columns.at[i,j+"馬場"] = a.index(columns.at[i,j+"馬場"])
            a = ["牡","牝","セ"]
            columns.at[i,j+"性別"] = a.index(columns.at[i,j+"性別"])
            #体重増加量
            #体重増加量
            try:
                columns.at[i,j+"体重増加量"] = float(columns.at[i,j+"馬体重"][4:-1])
            except:
                try:
                    columns.at[i,j+"体重増加量"] = float(columns.at[i,j+"馬体重"][5:-1])
                except:
                    columns.at[i,j+"体重増加量"] = 0
            columns.at[i,j+"馬体重"] = columns.at[i,j+"馬体重"][:3]
            columns.at[i,j+"優勝賞金"] = float(str(columns.at[i,j+"優勝賞金"]).replace(",",""))
        columns.at[i,"前走タイム"] = 60*float(columns.at[i,"前走タイム"][0])+float(columns.at[i,"前走タイム"][2:])
        columns.at[i,"前前走タイム"] = 60*float(columns.at[i,"前前走タイム"][0])+float(columns.at[i,"前前走タイム"][2:])
            
    for i  in ["レース種類","方向","天候","馬場","騎手","馬体重","優勝賞金","性別","体重増加量","レース距離","上り"]:
        for j in ["","前走","前前走"]:
            columns[j+i] = columns[j+i].astype('float')
    columns["前走タイム"] = columns["前走タイム"].astype('float')
    columns["前前走タイム"] = columns["前前走タイム"].astype('float')

    for i in ["","前走","前前走"]:
        for j in ["日付","レース番号","人気","単勝オッズ","通過","着差"]:
            columns = columns.drop(i+j,axis=1)
    columns = columns.drop("タイム",axis=1)
    columns = columns.drop("脚質",axis=1)
    columns = columns.drop("上り",axis=1)
    columns = columns.drop("着順",axis=1)

    columns = columns.reset_index(drop = True)
    print(columns.loc[0,:])
#    try:
    y_pred = model1.predict(columns,num_iteration=model1.best_iteration)
    srt = np.argsort(-y_pred[:,0])
    res = [int(columns.at[i,"馬番"]) for i in srt]
    probability = [round(y_pred[i,0]*100/np.sum(y_pred[:,0]),2) for i in srt]
#    except:
#        return ["",""]
    print(res)
    print(probability)
    print(y_pred[:,0])
    return [res,probability]

def get_result(path,row_num,column_num):
    res,probability = get_predict(path)
    downloadCSV()

    with open("race.csv","r",encoding="utf8") as f:
        reader = csv.reader(f)
        race_data = [i for i in reader]

    print(race_data)
    race_data[row_num][column_num] = "-".join(map(str,res)) + " " + "-".join(map(str,probability))

    with open("race.csv","w",newline="",encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerows(race_data)

    sendCSV()

    return schedule.CancelJob


if __name__ == "__main__":
    while(loop_is):
        try:
            url = input("urlを入力してください．")
            if("result" in url):
                url = url.replace("result","shutuba")
            get_predict(url)
        except Exception as e:
            print("不正な入力です")
            print(e)