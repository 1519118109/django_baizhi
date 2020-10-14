import random

from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as http_status

from django_baizhi.libs.geetest import GeetestLib
from django_baizhi.settings import constanst
from django_baizhi.utils.send_msg import Message
from user.check_serialziers import CheckUserModelSerializer
from user.models import UserInfo
from user.serialziers import UserModelSerializer
from user.utils import get_user_by_account

pc_geetest_id = "da6978ac632f7f57cd26232a2c3086f9"
pc_geetest_key = "819a301d46b3f07b9ddfba7f9e4d0add"


class CaptchaAPIView(APIView):
    """极验验证码"""

    user_id = 0
    status = False

    def get(self, request, *args, **kwargs):
        """获取验证码"""
        username = request.query_params.get("username")
        user = get_user_by_account(username)

        if user is None:
            return Response({"message": "用户不存在"}, status=http_status.HTTP_404_NOT_FOUND)

        self.user_id = user.id

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        self.status = gt.pre_process(self.user_id)
        response_str = gt.get_response_str()
        return Response(response_str)

    # pc端在ajax请求下用于比对验证码的方法
    def post(self, request, *args, **kwargs):

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')

        # 判断用户是否存在
        if self.user_id:
            result = gt.success_validate(challenge, validate, seccode, self.user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}
        return Response(result)

class UserAPIView(CreateAPIView):
    """用户注册"""
    queryset = UserInfo.objects.all()
    serializer_class = UserModelSerializer
class CheckUserAPIView(APIView):
    """用户注册检测"""
    def get(self,request,*args,**kwargs):
        print('111')
        phone= request.query_params.get('phone')
        print(phone)
        user = UserInfo.objects.filter(phone=phone).first()
        data = CheckUserModelSerializer(user).data
        if user:
            return Response({
                "status": 200,
                "message": "用户已存在",
            })
        else:
            return Response({
                "status": 400,
                "message": "用户可用",
            })

class SendMessageAPIVIew(APIView):
    times=0

    def get(self, request):
        """
        获取验证码  为手机号生成验证码并发送
        :param request:
        :return:
        """
        phone = request.query_params.get("phone")
        #  获取redis连接
        redis_connection = get_redis_connection("sms")

        #  1. 判断手机号是否发送过验证码
        phone_code = redis_connection.get("sms_%s" % phone)

        if phone_code is not None:
            return Response({"message": "您已经在60s内发送过短信了，请稍等"},
                            status=http_status.HTTP_400_BAD_REQUEST)

        #  2. 生成随机验证码
        code = "%06d" % random.randint(0, 999999)
        print(code)

        #  3. 将随机验证码按照一定的格式来存入redis
        redis_connection.setex("sms_%s" % phone, constanst.SMS_EXPIRE_TIME, code)  # 60s内不允许发送
        redis_connection.setex("mobile_%s" % phone, constanst.MOBILE_EXPIRE_TIME, code)  # 10分钟有效期

        #  4. 完成短信发送
        try:
            # message = Message(constanst.API_KEY)
            # res = message.send_message(phone, code)
            # print(res)
            from my_task.sms.tasks import send_sms
            send_sms.delay(phone, code)
            # send_mail.delay()
        except:
            return Response({"message": "短信发送失败"}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 响应前端
        return Response({"message": "短信发送成功"}, status=http_status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        code = request.data.get("code")
        phone = request.data.get("phone")
        print(code,phone)
        #  获取redis连接
        redis_connection = get_redis_connection("sms")

        #  1. 判断手机号是否发送过验证码
        # phone_code = redis_connection.get("sms_%s" % phone)
        phone_time = redis_connection.get("mobile_%s" % phone).decode(encoding='utf-8')
        self.times+=1
        print(self.times,phone_time)
        if self.times==5:
            return Response({"message": "访问次数已达上限"},
                            status=http_status.HTTP_400_BAD_REQUEST)
        if phone_time != code:
            return Response({"message": "验证码不正确"},
                            status=http_status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response({"message": "短信验证成功"}, status=http_status.HTTP_200_OK)

