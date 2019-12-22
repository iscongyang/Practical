import json
import mysql.connector
import datetime
import requests


class mysqlconnect:
    # 连接数据库
    def __init__(self, host, port, user, passwd, db):
        self.db = mysql.connector.connect(host=host, port=port, user=user, passwd=passwd, db=db)

    # 获取游标
    def cursor(self):
        return self.db.cursor()

    # 查询数据
    def get(self, sql):
        cursor = self.cursor()
        try:
            cursor.execute(sql, None)
            result = cursor.fetchall()
        except Exception as e:
            return e
        else:
            return result
        finally:
            cursor.close()

    # 增删改数据
    def excute(self, sql):
        cursor = self.cursor()
        try:
            cursor.execute(sql, None)
            self.db.commit()
            affect_row = cursor.rowcount
        except Exception as e:
            return e
        else:
            return affect_row
        finally:
            cursor.close()

    def __del__(self):
        self.db.close()


def format_string(args: tuple):
    """
    传入一个元组,拼接成字符串
    :param args: 机构ID元组
    :return: str
    """
    jigou_str = ""
    # 拼接要求值
    for index, i in enumerate(args):
        if index == len(args) - 1:
            jigou_str += str(i)
        else:
            jigou_str += str(i) + ','
    return jigou_str


def make_data():
    """
    查询数据库获取数据返回
    :return: tuple
    """
    host = 'xxx'
    port = 3306
    user = 'xxx'
    password = 'xxx'
    dbname = 'xxx'
    db = mysqlconnect(host, port, user, password, dbname)
    db.cursor()
    sql_select = "SELECT * FROM `*` WHERE `*` = '*' AND * = '{}';".format(yesterday_date_fmt)
    jigou_id = db.get(sql_select)[0]
    jigou_str = format_string(jigou_id)
    sql_select = "SELECT COUNT(*) AS * FROM * WHERE * IN ('{}')".format(jigou_str)
    ride_totle = db.get(sql_select)[0]
    ride_num = ride_totle[0]
    ride_money = format(float(ride_totle[1]) / 100, '.2f')
    # ========================查询第二个数据源==========================
    host = 'xxx'
    port = 3306
    user = 'xxx'
    password = 'xxx'
    dbname = 'xxx'
    db2 = mysqlconnect(host, port, user, password, dbname)
    db2.cursor()
    sql_select = "xxx".format(yesterday_date_fmt)
    register_num = db2.get(sql_select)[0][0]
    return ride_num, ride_money, register_num


def pz_data():
    try:
        temp_data = make_data()
        week = {'1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '0': '日'}
        num_week = yesterday_date.strftime('%w')
        yesterday_week = week[num_week]
        info = "### X: {}\n\n".format(temp_data[0])
        info += "### X: {}\n\n".format(temp_data[1])
        info += "### X: {}\n\n".format(temp_data[2])
        info += "------------------------------\n\n"
        info += "({} 星期{})".format(yesterday_date, yesterday_week)
        return info
    except Exception as e:
        raise (e)


def send_msg(webhook, message: str):
    News = {
        "msgtype": "markdown",
        "markdown": {
            "title": "数据展示",
            "text": message
        }
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(webhook, data=json.dumps(News), headers=headers)


if __name__ == '__main__':
    # 今天日期YYYY-MM-DD
    today_date = datetime.date.today()
    # 日期差值
    day_date = datetime.timedelta(1)
    # 事件开始日期
    yesterday_date = today_date - day_date
    # 事件开始日期YYYYMMDD
    yesterday_date_fmt = today_date.strftime('%Y%m%d')
    info = pz_data()
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=xxx"
    send_msg(webhook=webhook, message=info)