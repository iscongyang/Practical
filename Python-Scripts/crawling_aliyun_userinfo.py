# coding=utf-8
__author__ = "cong.yang"
__version__ = 1.0
__discription__ = "此脚本是爬取阿里云堡垒机用户相关信息的"

import json
from urllib.request import Request, urlopen
import ssl
import csv


def getContent(url):
    """
    拼接请求头获取返回数据
    :param url:
    :return: data or 0
    """
    req = Request(url)
    req.add_header('Accept-Language', 'zh-CN,zh;q=0.9')
    req.add_header('Cookie', 'DBAPPUSM=你的Cookie; cname=你的Cookie')
    req.add_header('User-Agent', '你的Agent')
    try:
        resp = urlopen(req)
        buff = resp.read()
        data = buff.decode("UTF-8")
        resp.close()
    except Exception as e:
        print(e)
        return "0"
    return data


def get_id_name():
    """
    获取阿里云授权组ID_NAME
    url是要获取的用户页面地址
    :return: dict
    """
    rule_list_url = "https://*.*.*.*/index.php/rule/rule_list?search_keyword=&offset=0&limit=20&count=0&ctoken=***&_=1565920631979"
    rule_list_content = getContent(rule_list_url)
    rule_list_json = json.loads(rule_list_content)
    dict = {}
    for item in rule_list_json[1]:
        gid = item["id"]
        dict[gid] = item
    return dict


def get_info(url, gid):
    """
    根据传入的url获取页面信息
    :param url: 获取的页面
    :param gid: 用户组的gid
    :return: json
    """
    all_json = []
    info_url = url
    info_url_content = getContent(info_url)
    info_url_json = json.loads(info_url_content)
    for item in info_url_json[0]:
        dict = {}
        dict[gid] = item
        all_json.append(dict)
    return all_json


def get_data():
    """
    依次获取主机组, 用户组, 授权组信息
    :return: json
    """
    ssl._create_default_https_context = ssl._create_unverified_context
    rule_list_dict = get_id_name()  # 获取组id和组name
    ecs_bastion = []
    for gid in rule_list_dict:
        json_ecs = {}
        host_url = "https://*/index.php/rule/get_host?search_keyword=&zone=&network=&status=1&ruleid={}&ctoken=*&_=1565870316907".format(
            gid)
        host_dict = get_info(host_url, gid)
        user_url = "https://*/index.php/rule/get_user?search_keyword=&auth_type=&status=1&ruleid={}&ctoken=*&_=1565875792151".format(
            gid)
        user_dict = get_info(user_url, gid)
        pingju_url = "https://*/index.php/rule/get_credential?search_keyword=&credential=&status=1&ruleid={}&ctoken=*&_=1565876044231".format(
            gid)
        pingju_dict = get_info(pingju_url, gid)
        name = []
        for i in user_dict:
            name.append(i[gid]["name"])
        loginname = []
        for i in pingju_dict:
            loginname.append(i[gid]["loginname"])
        InstanceName = []
        PublicIpAddress = []
        for i in host_dict:
            InstanceName.append(i[gid]['InstanceName'])
            if i[gid]['PublicIpAddress'] == "":
                PublicIpAddress.append(i[gid]['PrivateIpAddress'])
            else:
                PublicIpAddress.append(i[gid]['PublicIpAddress'])
        json_ecs['name'] = name
        json_ecs['loginname'] = loginname
        json_ecs['InstanceName'] = InstanceName
        json_ecs['PublicIpAddress'] = PublicIpAddress
        json_ecs["gid"] = gid
        ecs_bastion.append(json_ecs)
    return ecs_bastion


def save_data():
    """
    生成CSV文件
    :return:
    """
    headers = ['name', 'loginname', 'InstanceName', 'PublicIpAddress', 'gid']
    all_list = get_data()
    # TODO This is a question ?
    rows = dict(all_list)
    with open('a.csv', 'a+') as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(rows)


if __name__ == '__main__':
    save_data()
