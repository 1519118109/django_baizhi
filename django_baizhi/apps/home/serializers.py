from rest_framework.serializers import ModelSerializer

from home.models import Banner, Nav


class BannerModelSerializer(ModelSerializer):
    """轮播图序列化器"""

    class Meta:
        model = Banner
        fields = ("img", "link")

class HeaderModelSerializer(ModelSerializer):
    """轮播图序列化器"""

    class Meta:
        model = Nav
        fields = ("title", "link","is_site")
