from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework import settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

# Create your models here.


class UserInfo(AbstractUser):
    """用户模型"""
    phone = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    user_head = models.ImageField(upload_to="user", verbose_name="用户头像", null=True, blank=True)

    class Meta:
        db_table = "bz_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
