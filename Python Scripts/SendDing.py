import json
import time
import hmac
import hashlib
import urllib.request as urllibreq
import base64
import requests


class SendDingUtils:
    def __init__(self, token, secret):
        self.__timestamp = int(time.time() * 1000)
        self.__sign = "{}\n{}".format(self.__timestamp, secret)
        __secret_enc = secret.encode(encoding='UTF-8', errors='strict')
        __sign_enc = self.__sign.encode(encoding='UTF-8', errors='strict')
        __hmac_code = hmac.new(__secret_enc, __sign_enc, digestmod=hashlib.sha256).digest()
        sign_base64 = urllibreq.quote(base64.b64encode(__hmac_code))
        default_url = "https://oapi.dingtalk.com/robot/send?access_token"
        self.mysign = "{}={}&timestamp={}&sign={}".format(default_url, token, self.__timestamp, sign_base64)

    def __text(self, *args, **kwargs):
        text_msg = {
            "msgtype": "text",
            "text": {
                "content": args[0]
            },
            "at": {
                "atMobiles": [
                    "{}".format(kwargs["tel"])
                ],
                "isAtAll": "{}".format(kwargs["at"])
            }
        }
        requests.post(self.mysign, json=text_msg)


    def __markdown(self, *args):
        markdown_msg = {
            "msgtype": "markdown",
            "markdown": {
                "title": args[0],
                "text": args[1]
            }
        }
        requests.post(self.mysign, json=markdown_msg)

    types = {
        'text': __text,
        'markdown': __markdown,
    }

    def send(self, mytype, *args, **kwargs):
        if mytype == "text":
            self.__text(*args, **kwargs)
        elif mytype == "markdown":
            self.__markdown(*args)
        else:
            return -1


if __name__ == "__main__":
    # 自定义机器人webhook的token
    token = "xxx"
    # 加签密钥
    secret = "xxx"
    s = SendDingUtils(token, secret)
    # 被@的电话, 是否at全部人
    others = {"tel": "1**********", "at": "false"}
    s.send("text", "测试text", **others)
    s.send("markdown", "测试markdown", "xxx")
