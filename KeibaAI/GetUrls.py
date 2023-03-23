import time
import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

#データを保存する場所
data_path = "../../Dataset/"

#chromedriver.exeのパス
#変更して使用してください
driver_path = r"../../chromedriver_win32/chromedriver"

#netkeibaのデータベースURL
URL = "https://db.netkeiba.com/?pid=race_search_detail"

#seleniumの各種設定
options = Options()
#options.add_argument('--headless')    # ヘッドレスモードに
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(driver_path,chrome_options=options) 
wait = WebDriverWait(driver,1000)
driver.get(URL)
time.sleep(1)
wait.until(EC.presence_of_all_elements_located)

# 期間を選択
begin_year = 2010
begin_month = 1
end_year = 2021
end_month = 12
start_year_element = driver.find_element_by_name('start_year')
start_year_select = Select(start_year_element)
start_year_select.select_by_value(str(begin_year))
start_mon_element = driver.find_element_by_name('start_mon')
start_mon_select = Select(start_mon_element)
start_mon_select.select_by_value(str(begin_month))
end_year_element = driver.find_element_by_name('end_year')
end_year_select = Select(end_year_element)
end_year_select.select_by_value(str(end_year))
end_mon_element = driver.find_element_by_name('end_mon')
end_mon_select = Select(end_mon_element)
end_mon_select.select_by_value(str(end_month))

# 中央競馬場をチェック
for i in range(1,11):
    terms = driver.find_element_by_id("check_Jyo_"+ str(i).zfill(2))
    terms.click()

# 重賞を選択
class_element = driver.find_elements_by_xpath('//*[@id="db_search_detail_form"]/form/table/tbody/tr[8]/td//input')
select_element = class_element[0]
select_element.click()
select_element = class_element[1]
select_element.click()
select_element = class_element[2]
select_element.click()

# 表示件数を選択(20,50,100の中から最大の100へ)
list_element = driver.find_element_by_name('list')
list_select = Select(list_element)
list_select.select_by_value("100")

# フォームを送信
frm = driver.find_element_by_css_selector("#db_search_detail_form > form")
frm.submit()
time.sleep(5)
wait.until(EC.presence_of_all_elements_located)

#保存ファイル名を指定
file_name = str(begin_year)+str(begin_month)+"-"+str(end_year)+str(end_month)+".txt"

with open(os.path.join(data_path,file_name),mode='w') as f:
    while True:
        time.sleep(10)
        wait.until(EC.presence_of_all_elements_located)
        all_rows = driver.find_element_by_class_name('race_table_01').find_elements_by_tag_name("tr")
        for row in range(1, len(all_rows)):
            race_href=all_rows[row].find_elements_by_tag_name("td")[4].find_element_by_tag_name("a").get_attribute("href")
            f.write(race_href+"\n")
        try:
            target = driver.find_elements_by_link_text("次")[0]
            driver.execute_script("arguments[0].click();", target) #javascriptでクリック処理
        except IndexError:
            break
