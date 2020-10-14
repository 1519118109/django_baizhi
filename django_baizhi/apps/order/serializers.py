import time
from datetime import datetime
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django_redis import get_redis_connection
from django.db import transaction

from course.models import Course, CourseExpire
from order.models import Order, OrderDetail


class OrderModelSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "order_number", "pay_type")

        extra_kwargs = {
            "id": {"read_only": True},
            "order_number": {"read_only": True},
            "pay_type": {"write_only": True},
        }

    def validate(self, attrs):
        """对数据进行验证"""
        pay_type = attrs.get("pay_type")
        try:
            Order.pay_choices[pay_type]
        except Order.DoesNotExist:
            raise serializers.ValidationError("您当前选择的支付方式不被允许")

        return attrs

    def create(self, validated_data):
        """生成订单  与  订单详情"""

        # 获取购物车信息
        redis_connection = get_redis_connection("cart")

        # 获取用户信息 context
        user_id = self.context['request'].user.id
        incr = redis_connection.incr('order')

        # 生成唯一的订单号  时间戳  用户id  随机字符串
        order_number = datetime.now().strftime("%Y%m%d%H%M%S") + "%06d" % user_id + "%06d" % incr
        print(order_number)

        # 生成订单
        order = Order.objects.create(
            order_title="百知教育在线课程订单",
            total_price=0,
            real_price=0,
            order_number=order_number,
            order_status=0,
            pay_type=validated_data.get("pay_type"),
            credit=0,
            coupon=0,
            order_desc="学完这个课程你即将踏入技术的巅峰",
            user_id=user_id,
        )
        # 订单有效期
        from my_task.change_order.tasks import check_order
        check_order.delay()
        # 获取订单详情相关的信息
        cart_list = redis_connection.hgetall("cart_%s" % user_id)
        select_list = redis_connection.smembers("select_%s" % user_id)

        # TODO 判断课程是否被勾选，如果被勾选，则判断该课程的有效期id是否大于0

        for course_id_byte, expire_id_byte in cart_list.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)

            if course_id_byte in select_list:

                try:
                    # 获取购物车中所有的商品信息
                    course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                except Course.DoesNotExist:
                    """课程不存在则不作任何操作"""
                    continue

                # 如果有效期的id大于0 则需要计算商品的价格 id不大于0则代表永久 需要默认值
                origin_price = course.price
                expire_text = "永久有效"

                if expire_id > 0:
                    try:
                        course_expire = CourseExpire.objects.get(pk=expire_id)

                        # 有效期对应的价格
                        origin_price = course_expire.price
                        expire_text = course_expire.expire_text

                    except CourseExpire.DoesNotExist:
                        pass

                    # 根据已勾选的商品的对应有效期的价格计算最终勾选商品的价格
                    expire_real_price = course.expire_real_price(expire_id)

                    try:
                        # 生成订单详情
                        OrderDetail.objects.create(
                            order=order,
                            course=course,
                            expire=expire_id,
                            price=origin_price,
                            real_price=expire_real_price,
                            discount_name=course.discount_name,
                        )
                    except:
                        # 一旦发生异常  回滚
                        raise serializers.ValidationError("订单创建失败")

                else:
                    expire_real_price = float(course.real_price())
                    try:
                        # 生成订单详情
                        OrderDetail.objects.create(
                            order=order,
                            course=course,
                            expire=expire_id,
                            price=course.price,
                            real_price=expire_real_price,
                            discount_name=course.discount_name,
                        )
                    except:
                        # 一旦发生异常  回滚
                        raise serializers.ValidationError("订单创建失败")

                # TODO 将已经生成订单的课程从购物车移除
                try:
                    # 将商品的信息储移除redis
                    redis_connection = get_redis_connection("cart")
                    # redis的管道
                    pipeline = redis_connection.pipeline()
                    # 开启管道
                    pipeline.multi()
                    # 商品的信息以及对应的有效期   cart_1    1   0

                    pipeline.hdel("cart_%s" % user_id, course_id)
                    pipeline.srem("select_%s" % user_id, course_id)

                    # 执行
                    pipeline.execute()

                except:

                    raise serializers.ValidationError("订单创建失败")

                # 计算订单的总价
                order.total_price += float(origin_price)
                order.real_price += float(expire_real_price)

            order.save()
        return order
