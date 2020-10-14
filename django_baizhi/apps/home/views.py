from rest_framework.generics import ListAPIView

from django_baizhi.settings.constanst import BANNER_LENGTH, HEADER_LENGTH, FOOTER_LENGTH
from home.models import Banner, Nav
from home.serializers import BannerModelSerializer, HeaderModelSerializer


class BannerListAPIView(ListAPIView):
    """轮播图"""
    queryset = Banner.objects.filter(is_delete=False, is_show=True).order_by("-id")[:BANNER_LENGTH]
    serializer_class = BannerModelSerializer

class HeaderListAPIView(ListAPIView):
    """轮播图"""
    queryset = Nav.objects.filter(is_delete=False, is_show=True,position=1).order_by("-id")[:HEADER_LENGTH]
    serializer_class = HeaderModelSerializer

class FooterListAPIView(ListAPIView):
    """轮播图"""
    queryset = Nav.objects.filter(is_delete=False, is_show=True,position=2).order_by("-id")[:FOOTER_LENGTH]
    serializer_class = HeaderModelSerializer

