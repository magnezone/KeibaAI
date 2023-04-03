import ftplib

ipAddress = "sv7.wp.xdomain.ne.jp"
userName = "tomsky.wp.xdomain.jp"
password = "Magnez0ne765pro"

#ダウンロード
#with open("temp.php","wb") as f:
#    ftp.retrbinary("RETR wp-content/themes/twentytwentyone/functions.php",f.write)

#アップロード
def sendCSV():
    ftp = ftplib.FTP(ipAddress)
    ftp.set_pasv('true')
    ftp.login(userName,password)
    with open("race.csv","rb") as f:
        ftp.storbinary("STOR toms-dir/race.csv",f)
    ftp.quit()

def downloadCSV():
    ftp = ftplib.FTP(ipAddress)
    ftp.set_pasv('true')
    ftp.login(userName,password)
    with open("race.csv","wb") as f:
        ftp.retrbinary("RETR toms-dir/race.csv",f.write)
    ftp.quit()

if __name__ == "__main__":
    downloadCSV()