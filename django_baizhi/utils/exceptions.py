import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status

logger = logging.getLogger("django")


def exception_handler(exc, context):
    # 格式化异常信息
    error = "%s %s %s" % (context['view'], context['request'].method, exc)
    print(error)

    # 先调用drf本身处理异常的方法
    response = drf_exception_handler(exc, context)
    # 如果返回值为None，代表发生了DRF无法处理的异常，需要自定义处理
    if response is None:
        # 将错误信息记录到日志中
        logger.error(error)
        return Response(
            {"error_message": "尊敬的上帝请稍等，后台程序猿小哥哥飞速处理中~"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, exception=None)

    # 如果返回值不为空，则说明异常已经被DRF处理  无需干预
    return response
