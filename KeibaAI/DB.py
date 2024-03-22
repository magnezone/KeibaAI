import mysql.connector

def add_DB(race_id,race_date,race_location,race_number,race_result):

    # MySQLに接続
    conn = mysql.connector.connect(
        host="localhost",
        user="tomsky_wp1",
        password="Magnez0ne765pro",
        database="tomsky_wp1"
    )
    # カーソルを取得
    cursor = conn.cursor()
    # データベース作成
    query = "insert into race_table(\
                race_id,\
                race_date,\
                race_location,\
                race_number,\
                race_result)\
            values(%s,%s,%s,%s,%s)\
            on duplicate key update\
                race_id = values(race_id)"
    cursor.execute(query,(race_id,race_date,race_location,race_number,race_result))
    conn.commit()
    print(f"{cursor.rowcount} records inserted.")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    add_DB(1,"1999-09-22","b",1,"c")