from django_baizhi.settings import constanst
from django_baizhi.utils.send_msg import Message
from my_task.main import app


# celery的任务必须写在tasks文件中  别的文件不识别
@app.task(name="send_sms")  # name 可以指定当前的任务名称，如果不写，则使用默认的函数名作为任务名
def send_sms(phone,code):
    message = Message(constanst.API_KEY)
    res = message.send_message(phone, code)
    print(res)
    return "短信发送成功"
# @app.task()
# # app.task(name="send_mail")
# def send_mail():
#     print("邮件发送成功")
#
#     return "mail"