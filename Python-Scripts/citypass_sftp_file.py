import datetime
import json
import paramiko
import requests


def get_date(file_name: str, url: str, now_date: str):
    """
    获取数据生成文件
    :param file_name: 生成文件名
    :param url: 获取数据地址
    :return: None
    """
    try:
        url = url
        repo_data = json.loads(requests.get(url).text)
        if repo_data['errMsg'] == "9999":
            temp_list = []
            temp_str = ''
            # 取dict值加入list
            for value in repo_data['data'].values():
                temp_list.append(value)
            # 拼接要求值
            for i in temp_list:
                temp_str += str(i) + ','
            temp_str += now_date
            # 把值写入文件
            with open(file_name, 'w+') as f:
                f.write(str(temp_str))
        else:
            message = repo_data['errMsg']
            raise Exception(message)
    except Exception as e:
        raise e


def put_file(host, port, username, password, file_name, file_only_name, remote_path):
    """
    上传文件到SFTP服务器
    :param host: sftp主机
    :param port: sftp端口
    :param username: sftp用户名
    :param password: sftp密码
    :param file_name: 要传输的文件名
    :param remote_path: sftp目标地址
    :return: Boolean
    """
    flag = False
    try:
        connect = paramiko.Transport((host, port))
        connect.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(connect)
        final_file_path = remote_path + file_only_name
        sftp.put(file_name, final_file_path)
        flag = True
        sftp.close()
    except Exception as e:
        raise e
    finally:
        return flag


def send_msg(webhook):
    try:
        message = {
            "msgtype": "text",
            "text": {
                "content": "CityPass数据文件发送失败"
            },
            "at": {
                "atMobiles": ['x'],
                "isAtAll": False
            }
        }
        headers = {'Content-Type': 'application/json'}
        requests.post(webhook, data=json.dumps(message), headers=headers)
    except Exception as e:
        raise e


if __name__ == "__main__":
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    file_name = 'D:\\tools\\metro_citypass_' + now_date + '.txt'
    file_only_name = 'metro_citypass_' + now_date + '.txt'
    #remote_path = "/app/sftp/duchang/download/backup/"
    remote_path = "/download/backup/"
    # 正式地址
    url = "http://x.x.x.x:x/dingdingData"
    get_date(file_name, url, now_date)

    flag = put_file("172.19.44.101", 22, "duchang", "duchang", file_name, file_only_name, remote_path)
    if not flag:
        webhook = "https://oapi.dingtalk.com/robot/send?access_token=x"
        send_msg(webhook)
        print("发送失败")
    else:
        print("发送成功")
