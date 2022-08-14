import os
import requests
import time
from bs4 import BeautifulSoup
from requests.models import Response
import re

begin_year = 2010
begin_month = 1
end_year = 2021
end_month = 12

root = "../../"

#フォルダ作成
year = begin_year
month = begin_month
while(year <= end_year):
    while(month <= end_month):
        save_dir = root+"Dataset/"+"new"+"/"+str(year)+"/"+str(month)
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
        print(year,month)
        month = month+1
        if(month > 12):
            month = month%12
            year = year+1
            break

with open(root+"Dataset/"+str(begin_year)+str(begin_month)+"-"+str(end_year)+str(end_month)+"1600万-500万"+".txt", "r") as f:
    urls = f.read().splitlines()
    for url in urls:
        list = url.split("/")
        race_id = list[-2]
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text,"html.parser")
        repatter = re.compile("\d{4}年\d+月")
        date = soup.find("a",text = repatter)
        print(date.getText())
        year = re.compile("\d{4}年").search(date.getText())[0][0:-1]
        month = re.compile("[1][012]月|[1-9]月").search(date.getText())[0][0:-1]
        save_dir = root+"Dataset/"+"new"+"/"+str(year)+"/"+str(month)
        save_file_path = save_dir+"/"+race_id+'.html'
        html = response.text
        time.sleep(1)
        with open(save_file_path, 'w',encoding = response.apparent_encoding) as file:
            file.write(html)