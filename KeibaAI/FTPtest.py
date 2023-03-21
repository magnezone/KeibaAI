import ftplib
import csv


ipAddress = "sv7.wp.xdomain.ne.jp"
userName = "tomsky.wp.xdomain.jp"
password = "Magnez0ne765pro"

ftp = ftplib.FTP(ipAddress)
ftp.set_pasv('true')
ftp.login(userName,password)

file_list = ftp.dir("wp-content/themes/twentytwentyone/")
print(file_list)

#ダウンロード
#with open("temp.php","wb") as f:
#    ftp.retrbinary("RETR wp-content/themes/twentytwentyone/functions.php",f.write)

#アップロード
with open("race.csv","rb") as f:
    ftp.storbinary("STOR toms-dir/race.csv",f)

ftp.quit()