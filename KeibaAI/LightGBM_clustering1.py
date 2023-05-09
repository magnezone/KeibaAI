from collections import UserDict
import csv
from re import X
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.layers import Activation, Dropout, Flatten, Dense
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.utils import to_categorical
from tensorflow import keras
import random
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.metrics import accuracy_score
import optuna.integration.lightgbm as lgb

path = __file__+"\\..\\Dataset\\Data1600-500.csv"

# データフレームを綺麗に出力する関数
import IPython
def display(*dfs, head=True):
    for df in dfs:
        IPython.display.display(df.head() if head else df)

#入力データ形式
#[種類，距離，年齢，性別，斤量，馬番，頭数，馬体重，体重増加量，単勝オッズ，前走頭数，前走馬番，
#前走優勝賞金，前走種類，前走距離，前走タイム差，前走後3Fタイム，連対率]

random.seed(1)

columns = ["race_type","length","age","sex","burden","jockey","horse_number","head_count",
            "horse_weight","horse_weight_diff","odds","prev_head_count","prev_horse_number","prev_prize",
            "prev_race_type","prev_length","prev_time","prev_time_diff","prev_last3f","prev_result",
            "preprev_head_count","preprev_horse_number","preprev_prize",
            "preprev_race_type","preprev_length","preprev_time","preprev_time_diff",
            "preprev_last3f","preprev_result","race_count","win2_ratio","legquality","weight"]

columns = ["race_type","length","age","sex","burden","jockey","horse_number","head_count",
            "horse_weight","horse_weight_diff","prev_head_count","prev_horse_number","prev_prize",
            "prev_race_type","prev_length","prev_time","prev_time_diff","prev_last3f","prev_result",
            "preprev_head_count","preprev_horse_number","preprev_prize",
            "preprev_race_type","preprev_length","preprev_time","preprev_time_diff",
            "preprev_last3f","preprev_result","race_count","win2_ratio","legquality","weight"]

jockeys = {}
with open(path) as f:
    reader = csv.reader(f)
    reader.__next__()
    for row in reader:
        s = row[1].replace(" ","")
        jockeys[s] = int(row[0])

x_data = []
y_data = []
#Data1_mod2.csvから障害レース以外を読み込み
with open(path,newline='') as f:
    reader = csv.reader(f)
    reader.__next__()
    for row in reader:
        line = []
        if(row[0][0:4] == "2020" or row[0][0:4] == "2021"):
            continue
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
            line.append(float(row[10][5:-1]))
        #単勝オッズ
        #line.append(float(row[11]))
        #前走頭数
        line.append(int(row[14]))
        #前走馬番
        line.append(float(row[15]))
        #前走優勝賞金
        line.append(float(row[16].replace(",","")))
        #前走種類
        #芝＝１，ダート＝２
        if(row[17] == "芝"):
            line.append(1)
        elif(row[17] == "ダート"):
            line.append(2)
        else:
            line.append(3)
        #前走距離
        line.append(float(row[18]))
        #前走タイム
        try:
            prev_time = 60*int(row[28][1])+float(row[28][3:])
        except:
            continue
        line.append(prev_time)
        #前走タイム差
        line.append(float(row[20]))
        #前走後3Fタイム
        line.append(float(row[21]))
        #前走着順
        line.append(int(row[22]))
        #前々走頭数
        line.append(float(row[23]))
        #前々走馬番
        line.append(float(row[24]))
        #前々走優勝賞金
        line.append(float(row[25].replace(",","")))
        #前々走種類
        #芝＝１，ダート＝２，障害＝３
        if(row[26] == "芝"):
            line.append(1)
        elif(row[26] == "ダート"):
            line.append(2)
        else:
            line.append(3)
        #前々走距離
        line.append(float(row[27]))
        #前々走タイム
        try:
            time = 60*int(row[28][1])+float(row[28][3:])
        except:
            continue
        line.append(time)
        #前々走タイム差
        line.append(float(row[29]))
        #前々走後3Fタイム
        line.append(float(row[30]))
        #前々走着順
        try:
            line.append(int(row[31]))
        except:
            continue
        #レース回数
        line.append(float(row[32]))
        #連対率
        line.append(float(row[33]))
        #脚質
        line.append(float(row[34]))
        #重み
        if(int(row[12]) <= 3 and float(row[11]) > 10):
            line.append(1)
        else:
            line.append(1)
        #入力データ
        x_data.append(line)
        #出力データ
        if(int(row[12]) <= 3):
            y_data.append(0)
        elif(int(row[12])-3<=(int(row[14])-3)/2):
            y_data.append(1)
        else:
            y_data.append(2)

high = [x_data[i] for i in range(len(x_data)) if(y_data[i] == 0)]
middle = [x_data[i] for i in range(len(x_data)) if(y_data[i] == 1)]
low = [x_data[i] for i in range(len(x_data)) if(y_data[i] == 2)]
use_middle = random.sample(middle,len(high))
use_low = random.sample(low,len(high))
UseData = high+use_middle+use_low
UseLabel = [i//len(high)for i in range(len(UseData))]
df = pd.DataFrame(UseData,columns=columns)
df["target"] = UseLabel
display(df)
X = df.drop("target",axis=1)
Y = df["target"].values

x_train,x_test,y_train,y_test = train_test_split(X,Y,stratify=Y,train_size=0.8,random_state=0)
train_set = lgb.Dataset(x_train.drop("weight",axis=1),y_train,weight = x_train["weight"])
valid_set = lgb.Dataset(x_test.drop("weight",axis=1),y_test,weight = x_test["weight"])

params = {
    "objective":"multiclass",
    "metric":"multi_logloss",
    'boosting_type': 'gbdt',  # default = 'gbdt'
    'num_class': 3, 
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

model.save_model("model_low.txt")
print(result_data)
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
