import requests

a = requests.get("https://www.jra.go.jp/keiba/calendar2024/2024/3/0309.html")
a.encoding = a.apparent_encoding 
print(a.text)
with open("test.html", "w",encoding=a.encoding) as f:
    f.write(a.text)

print("書き込みが完了しました")

