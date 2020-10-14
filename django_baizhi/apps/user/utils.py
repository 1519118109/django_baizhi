from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework.views import APIView

from user.models import UserInfo


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': user.username,
        # "id": user.id
    }


def get_user_by_account(account):
    "获取用户对象的方法"
    try:
        user = UserInfo.objects.filter(Q(username=account) | Q(phone=account)).first()
    except UserInfo.DoesNotExist:
        return None
    else:
        return user

class UserAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        根据账号信息来获取用户对象
        :param request:
        :param username: 前端输入的账号信息  手机号  用户名  邮箱
        :param password: 密码
        :return:  查询出的用户
        """

        user = get_user_by_account(username)
        if not password:
            return user

        # 获取到用户信息后开始校验
        if user and user.check_password(password) and user.is_authenticated:
            return user
        else:
            return None
