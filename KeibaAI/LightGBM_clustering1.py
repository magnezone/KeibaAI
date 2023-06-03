from collections import UserDict
import csv
import re
import matplotlib.pyplot as plt
import random
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.metrics import accuracy_score
import optuna.integration.lightgbm as lgb
import os
import pandas as pd
import numpy as np

root = os.path.dirname(os.path.abspath(__file__))

# データフレームを綺麗に出力する関数
import IPython
def display(*dfs, head=True):
    for df in dfs:
        IPython.display.display(df.head() if head else df)

#columns_name = ["日付","レース番号","レース種類","方向","レース距離","天候","馬場",
#                "着順","枠番","馬番","年齢","性別","斤量","騎手","タイム","着差","通過","上り",
#                "単勝オッズ","人気","馬体重","優勝賞金"]

columns = pd.read_csv(root + "\\Dataset\\重賞データ.csv")

jockeys = {}
with open(root + "\\Dataset\\Jockey.csv") as f:
    reader = csv.reader(f)
    reader.__next__()
    for row in reader:
        s = row[1].replace(" ","")
        jockeys[s] = int(row[0])

for i in ["","前走","前前走"]:
    for j in ["日付","レース番号","枠番","馬番","人気","単勝オッズ","通過","着差"]:
        columns = columns.drop(i+j,axis=1)
columns = columns.drop("タイム",axis=1)
columns = columns.drop("脚質",axis=1)

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
            columns.at[i,j+"体重増加量"] = columns.at[i,j+"馬体重"][4:-1]
        except:
            columns.at[i,j+"体重増加量"] = columns.at[i,j+"馬体重"][5:-1]
        columns.at[i,j+"馬体重"] = columns.at[i,j+"馬体重"][:3]
        columns.at[i,j+"優勝賞金"] = float(str(columns.at[i,j+"優勝賞金"]).replace(",",""))
    columns.at[i,"前走タイム"] = 60*float(columns.at[i,"前走タイム"][0])+float(columns.at[i,"前走タイム"][2:])
    columns.at[i,"前前走タイム"] = 60*float(columns.at[i,"前前走タイム"][0])+float(columns.at[i,"前前走タイム"][2:])
    if(columns.at[i,"着順"] != 1):
        columns.at[i,"着順"] = 0
        
for i  in ["レース種類","方向","天候","馬場","騎手","馬体重","優勝賞金","性別","体重増加量"]:
    for j in ["","前走","前前走"]:
        columns[j+i] = columns[j+i].astype('float')
columns["前走タイム"] = columns["前走タイム"].astype('float')
columns["前前走タイム"] = columns["前前走タイム"].astype('float')

a = columns[columns["着順"] == 1]
b = columns[columns["着順"] == 0]
b = b.sample(len(a.index))
c = pd.concat([a,b],ignore_index=True)
print(c)
X = c.drop("着順",axis=1)
Y = c["着順"].values



x_train,x_test,y_train,y_test = train_test_split(X,Y,stratify=Y,train_size=0.8,random_state=0)
train_set = lgb.Dataset(x_train,y_train)
valid_set = lgb.Dataset(x_test,y_test)

params = {
    "objective":"multiclass",
    "metric":"multi_logloss",
    'boosting_type': 'gbdt',  # default = 'gbdt'
    'num_class': 2, 
    'num_leaves': 63,         # default = 31,
    'learning_rate': 0.01,    # default = 0.1
    'feature_fraction': 0.8,  # default = 1.0
    'bagging_freq': 1,        # default = 0
    'bagging_fraction': 0.8,  # default = 1.0
    'random_state': 0,        # default = None
}
result_data = {}
model = lgb.train(
    params = params,
    valid_names=["train","valid"],
    train_set = train_set,
    valid_sets = [train_set,valid_set],
    num_boost_round = 20000,
    early_stopping_rounds = 10,
    verbose_eval = 50,
    evals_result = result_data
)

model.save_model(root+"\\Dataset\\model.txt")
plt.plot(result_data["train"]["multi_logloss"], color = "red", label = "train")
plt.plot(result_data["valid"]["multi_logloss"], color = "blue", label = "valid")
plt.legend()
plt.show()
importance = model.feature_importance()
print(columns)
print(importance)

y_pred = model.predict(x_test, num_iteration=model.best_iteration)
y_pred = y_pred.round(0)
accuracy = accuracy_score(y_pred, y_test)
print(f"accuracy score: {accuracy:0.4f}")
