import re

from django.contrib.auth.hashers import make_password
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from user.models import UserInfo
from user.utils import get_user_by_account


class CheckUserModelSerializer(ModelSerializer):
    """用户序列化器"""

    class Meta:
        model = UserInfo
        fields = ( "phone",)