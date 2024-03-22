import ftplib
import json
import os

abs_dir = os.path.dirname(os.path.abspath(__file__))
with open(abs_dir + r"/info.json") as f:
    info = json.load(f)
ipAddress = info["ipaddress"]
userName = info["username"]
password = info["password"]

print(ipAddress)
print(userName)
print(password)

#ダウンロード
#with open("temp.php","wb") as f:
#    ftp.retrbinary("RETR wp-content/themes/twentytwentyone/functions.php",f.write)

#アップロード
def sendCSV():
    ftp = ftplib.FTP(ipAddress)
    ftp.set_pasv('true')
    ftp.login(userName,password)
    with open("race.csv","rb") as f:
        ftp.storbinary("STOR race.csv",f)
    ftp.quit()

def downloadCSV():
    ftp = ftplib.FTP(ipAddress)
    ftp.set_pasv('true')
    ftp.login(userName,password)
    with open("race.csv","wb") as f:
        ftp.retrbinary("RETR race.csv",f.write)
    ftp.quit()

if __name__ == "__main__":
    sendCSV()
    #downloadCSV()