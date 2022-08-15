# KeibaAI

## About
3着以内に入る馬を予想します．

## Requirements
python 3.8

ライブラリはrequirements.txtを参照

## How to use
GetUrls.py:レースURLを取得

↓

url2html.py：レースURLからHTMLを保存

↓

html2csv.py:HTMLからデータを抽出しcsvで保存

↓

LightGBM_clustering1.py:csvデータを用いて学習

↓

run_clustering_future.py:レース予想
