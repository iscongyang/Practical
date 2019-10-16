#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: congyang
# Description: This script converts the acquired data into a picture and alarm
# Note that the server needs to install the simkai.ttf font.

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
    :param yesterdayBuyNum: 自定义1
    :param yesterdayUseNum: 自定义2
    :param yesterdayUseAmount: 自定义3
    :param totalUseAmount: 自定义4
    :param totalBuyNum: 自定义5
    :param totalUseNum: 自定义6
    :return: str
    """
    week = {'1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '0': '日'}
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    num_week = datetime.datetime.now().strftime('%w')
    now_week = week[num_week]
    title_text = "test旅游信息\ntest销售数量: {0}套".format(date['yesterdayBuyNum'])
    content_text = ""
    content_text += "自定义1: {0}套\n" \
                    "自定义2: {1}人\n" \
                    "自定义3: {2}元\n" \
                    "------------------------------\n" \
                    "自定义4: {3}套\n" \
                    "自定义5: {4}人\n" \
                    "自定义6: {5}元\n" \
                    "------------------------------\n" \
                    "信息来源: xxxx\n" \
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
            "title": "test数据",
            "text": ">![screenshot](%s)" % (message)
        }
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(webhook, data=json.dumps(News), headers=headers)


if __name__ == "__main__":
    # 获取数据API
    url = "http://xxx"
    res_title_text, res_text = make_text(get_date(url))
    pic_name = change_style(res_title_text, res_text)
    # 图片链接, xxxx换成自己Nginx配置的路径
    message = 'http://xxxx' + pic_name
    # 钉钉报警, xxxxx换成自己的token
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=xxxxx"
    send_msg(webhook=webhook, message=message)
