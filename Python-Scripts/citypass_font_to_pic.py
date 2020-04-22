import datetime
import json
import requests
from matplotlib import pylab


def get_date(url: str):
    """
    返回json格式数据
    :param url: 获取数据API
    :return: dict
    """
    message = ''
    try:
        url = url
        repo_date = json.loads(requests.get(url).text)
        if repo_date['errMsg'] == "9999":
            store_date = {
                'yesterdayBuyNum': repo_date['data']['yesterdayBuyNum'],
                'yesterdayUseNum': repo_date['data']['yesterdayUseNum'],
                'yesterdayUseAmount': repo_date['data']['yesterdayUseAmount'],
                'totalUseAmount': repo_date['data']['totalUseAmount'],
                'totalBuyNum': repo_date['data']['totalBuyNum'],
                'totalUseNum': repo_date['data']['totalUseNum'],
            }
            return store_date
        else:
            message = repo_date['errMsg']
    except:
        raise Exception(message)


def make_text(date: dict):
    """
    返回拼装数据
    :param yesterdayBuyNum: 当日旅游套票销售数量
    :param yesterdayUseNum: 当日使用套票乘车人数
    :param yesterdayUseAmount: 当日使用套票乘车金额
    :param totalUseAmount: 累计使用套票乘车金额
    :param totalBuyNum: 累计旅游套票销售数量
    :param totalUseNum: 累计使用套票乘车人数
    :return: str
    """
    week = {'1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '0': '日'}
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    num_week = datetime.datetime.now().strftime('%w')
    now_week = week[num_week]
    title_text = "x旅游套票信息\n当日旅游套票销售数量: {0}套".format(date['yesterdayBuyNum'])
    content_text = ""
    content_text += "当日旅游套票销售数量: {0}套\n" \
                    "当日使用套票乘车人数: {1}人\n" \
                    "当日使用套票乘车金额: {2}元\n" \
                    "------------------------------\n" \
                    "累计旅游套票销售数量: {3}套\n" \
                    "累计使用套票乘车人数: {4}人\n" \
                    "累计使用套票乘车金额: {5}元\n" \
                    "------------------------------\n" \
                    "信息来源: x\n" \
                    "({6} 星期{7})".format(date['yesterdayBuyNum'], date['yesterdayUseNum'], date['yesterdayUseAmount'],
                                         date['totalUseAmount'], date['totalBuyNum'], date['totalUseNum'], now_date,
                                         now_week)
    return (title_text, content_text)


def change_style(title_text: str, content_text: str):
    """
    处理文本转为图片
    :param title_text: 标题
    :param content_text: 文本
    :return: None
    """
    # 图片名
    n_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    pic_name = 'citypass' + n_date + '.png'
    font_title = {
        'family': 'KaiTi',
        'style': 'italic',
        'weight': 'black',
        'color': 'black',
        'size': 24
    }
    font_text = {
        'family': 'KaiTi',
        'style': 'normal',
        'weight': 'normal',
        'color': 'black',
        'size': 20
    }
    pylab.axis('off')
    pylab.text(0, 0.9, title_text, fontdict=font_title)
    pylab.text(0.05, 0, content_text, fontdict=font_text)
    pylab.savefig(pic_name)
    return pic_name


def send_msg(webhook, message: str):
    News = {
        "msgtype": "markdown",
        "markdown": {
            "title": "x数据",
            "text": ">![screenshot](%s)" % (message)
        }
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(webhook, data=json.dumps(News), headers=headers)


if __name__ == "__main__":
    url = "http://x.x.x.x:x/dingdingData"
    res_title_text, res_text = make_text(get_date(url))
    pic_name = change_style(res_title_text, res_text)
    # 配置nginx图片链接
    message = 'http://x.x.x.x:x/citypass/' + pic_name
    # 钉钉机器人测试
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=x"
    send_msg(webhook=webhook, message=message)
