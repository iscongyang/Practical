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
    查询开发数据库获取数据返回
    :return: tuple
    """
    # 今天日期YYYY-MM-DD
    today_date = datetime.date.today()
    # 昨天日期
    yesterday_date = today_date - datetime.timedelta(1)
    yesterday_date_fmt = yesterday_date.strftime('%Y%m%d')
    # 查询地铁宝只读库
    host = 'xxx'
    port = 3306
    user = 'xxx'
    password = 'xxx'
    dbname = 'xxx'
    db = mysqlconnect(host, port, user, password, dbname)
    db.cursor()
    # 查询当日机构ID
    sql_select = "SELECT x FROM `x` WHERE `x` = 'x' AND x = '{}';".format(yesterday_date_fmt)
    jigou_id = db.get(sql_select)[0]
    jigou_str = format_string(jigou_id)
    # 根据查询的机构ID查询当日乘车
    sql_select = "SELECT COUNT(*) AS ride_num, ifnull(SUM(x), 0) AS ride_money FROM x WHERE x IN ('{}') AND x > 0".format(jigou_str)
    ride_totle = db.get(sql_select)[0]
    # 昨日乘车人数
    ride_num = ride_totle[0]
    # 昨日乘车金额 单位:角
    ride_money = ride_totle[1]
    # ========================查询第二个数据源==========================
    host = 'xxx'
    port = 3306
    user = 'xxx'
    password = 'xxx'
    dbname = 'xxx'
    db2 = mysqlconnect(host, port, user, password, dbname)
    db2.cursor()
    # 昨日开通人数
    sql_select = "SELECT COUNT(*) FROM x WHERE x = 'x' AND TO_DAYS(x) = TO_DAYS('{}');".format(yesterday_date_fmt)
    register_num = db2.get(sql_select)[0][0]
    # 返回 [昨日开通人数, 昨日乘车人数, 昨日乘车金额]
    return register_num, ride_num, ride_money


def push_yunwei_db():
    """
    获取开发库的前一日数据处理后插入运维库
    :return: tuple
    """
    # 今天日期YYYY-MM-DD
    today_date = datetime.date.today()
    # 前天日期
    two_days_ago = today_date - datetime.timedelta(2)
    # 昨天日期
    one_day_ago = today_date - datetime.timedelta(1)
    # 前天日期YYYYMMDD
    two_days_ago_fmt = two_days_ago.strftime('%Y%m%d')
    # 昨天日期YYYYMMDD
    one_day_ago_fmt = one_day_ago.strftime('%Y%m%d')
    # 查数据库
    host = 'x'
    port = 3306
    user = 'x'
    password = 'x'
    dbname = 'x'
    db = mysqlconnect(host, port, user, password, dbname)
    db.cursor()

    # 判断数据库中是否存在one_day_ago_fmt的数据
    sql_select = "SELECT count(1) FROM x WHERE create_time = '{}' LIMIT 1".format(one_day_ago_fmt)
    results = db.get(sql_select)[0][0]
    if results == 0 or results == "NULL":
        temp_data = make_data()
        # 昨日开通人次
        yesterday_register = temp_data[0]
        # 昨天乘车人数
        yesterday_ride_num = temp_data[1]
        # 昨天乘车金额  单位:角
        yesterday_ride_money = temp_data[2]

        # 查询数据库前天累计开通人数,累计乘车人数,累计开通金额
        sql_select = "SELECT x,x,x FROM `x` WHERE create_time='{}';".format(two_days_ago_fmt)
        ride_full_totle = db.get(sql_select)[0]
        # 前天累计开通人数
        old_full_register = ride_full_totle[0]
        # 前天累计乘车人数
        old_full_ride_num = ride_full_totle[1]
        # 前天累计乘车金额 单位:角
        old_full_ride_money = ride_full_totle[2]

        # 昨天累计开通人数
        full_register = yesterday_register + old_full_register
        # 昨天累计乘车人数
        full_ride_num = yesterday_ride_num + old_full_ride_num
        # 昨天累计乘车金额 单位: 角
        full_ride_money = yesterday_ride_money + old_full_ride_money

        # 插入运维数据库
        sql_insert = "INSERT INTO x (daily_register,daily_ride_num,daily_ride_money,full_register,full_ride_num,full_ride_money,create_time) VALUES({},{},{},{},{},{},{})".format(
            yesterday_register, yesterday_ride_num, yesterday_ride_money, full_register, full_ride_num, full_ride_money, one_day_ago_fmt)
        db.excute(sql_insert)
        # 返回[昨日开通人次, 昨天乘车人数, 昨天乘车金额, 昨天累计开通人数, 昨天累计乘车人数, 昨天累计乘车金额]
        return yesterday_register, yesterday_ride_num, yesterday_ride_money, full_register, full_ride_num, full_ride_money
    else:
        # 数据库中存在one_day_ago_fmt数据, 直接查询
        sql_select = "SELECT daily_register, daily_ride_num, daily_ride_money, full_register, full_ride_num, full_ride_money FROM `yiyou_app` WHERE create_time='{}';".format(one_day_ago_fmt)
        totle_data = db.get(sql_select)[0]
        yesterday_register = totle_data[0]
        yesterday_ride_num = totle_data[1]
        yesterday_ride_money = totle_data[2]
        full_register = totle_data[3]
        full_ride_num = totle_data[4]
        full_ride_money = totle_data[5]
        # 返回[昨日开通人次, 昨天乘车人数, 昨天乘车金额, 昨天累计开通人数, 昨天累计乘车人数, 昨天累计乘车金额]
        return yesterday_register, yesterday_ride_num, yesterday_ride_money, full_register, full_ride_num, full_ride_money


def pz_data():
    """
    格式化数据返回
    :return: str
    """
    # 今天日期YYYY-MM-DD
    today_date = datetime.date.today()
    # 昨天日期
    yesterday_date = today_date - datetime.timedelta(1)
    try:
        temp_data = push_yunwei_db()
        week = {'1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '0': '日'}
        num_week = yesterday_date.strftime('%w')
        yesterday_week = week[num_week]
        info = "### x\n\n"
        info += "------------------------------\n\n"
        info += "### x: {}人\n\n".format(temp_data[0])
        info += "### x: {}次\n\n".format(temp_data[1])
        info += "### x: {}元\n\n".format(temp_data[2]/100)
        info += "------------------------------\n\n"
        info += "x: {}人\n\n".format(temp_data[3])
        info += "x: {}次\n\n".format(temp_data[4])
        info += "x: {}元\n\n".format(temp_data[5]/100)
        info += "------------------------------\n\n"
        info += "x: x\n\n"
        info += "({} 星期{})".format(yesterday_date, yesterday_week)
        return info
    except Exception as e:
        raise (e)


def send_msg(message):
    # 获取当前小时
    now_hour = datetime.datetime.now().hour
    print(now_hour)
    if now_hour == 14:
        print(111)
        # 发测试
        webhook = 'https://oapi.dingtalk.com/robot/send?access_token=x'
        api2(webhook=webhook, message=message)
    elif now_hour == 9:
        # 发正式
        webhook = 'https://oapi.dingtalk.com/robot/send?access_token=x'
        api(webhook=webhook, message=message)


def api(webhook, message: str):
    # url api的地址  type：是发text还是makdown格式的信息（mkdown 不支持@人） secret：建机器人时的签名 url：钉钉机器人url
    # title：标题  mobiles：@的人（列表 仅支持text）
    url = 'http://x.x.x.x:x/dingding/ding/'
    news = {'type': 'markdown', 'secret': 'x',
            'url': webhook,
            'title': 'x', 'message': message, }
    requests.post(url, json=news)

def api2(webhook, message: str):
    # url api的地址  type：是发text还是makdown格式的信息（mkdown 不支持@人） secret：建机器人时的签名 url：钉钉机器人url
    # title：标题  mobiles：@的人（列表 仅支持text）
    url = 'http://x.x.x.x:x/dingding/ding/'
    news = {'type': 'markdown',
            'url': webhook,
            'title': 'x', 'message': message, }
    requests.post(url, json=news)


if __name__ == '__main__':
    info = pz_data()
    print(info)
    send_msg(info)
    # 报警测试
    # webhook = "https://oapi.dingtalk.com/robot/send?access_token=x"
    # send_msg(webhook=webhook, message=info)
    # webhook = 'https://oapi.dingtalk.com/robot/send?access_token=x'
    # api(webhook=webhook, message=info)
