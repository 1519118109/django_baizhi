import requests


class Message(object):

    def __init__(self, api_key):
        # 账号的唯一标识
        self.api_key = api_key
        # 单条发送短息的接口
        self.single_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_message(self, phone, code):
        """
        短信发送的实现
        phone: 前端传递的手机号
        code: 随机验证码
        :return:
        """
        params = {
            "apikey": self.api_key,
            "mobile": phone,
            "text": "【毛信宇test】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }

        # 将包含参数的请求发送出去
        res = requests.post(self.single_send_url, data=params)
        print(res)


if __name__ == '__main__':
    message = Message("40d6180426417bfc57d0744a362dc108")
    message.send_message("18339180139", "888888")
