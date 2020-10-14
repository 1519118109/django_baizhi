import logging

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticated

from course.models import Course, CourseExpire
from django_baizhi.settings.constanst import IMAGE_SRC

logger = logging.getLogger("django")


class CartViewSet(ViewSet):
    """购物车相关的业务"""

    # 只允许已登录且认证成功的用户访问
    permission_classes = [IsAuthenticated]

    def add_cart(self, request):
        """
        将用户提交的课程添加进购物车
        :param request: 用户id  课程id  勾选状态  有效期
        :return:
        """
        course_id = request.data.get("course_id")
        select = request.data.get("checked")
        print(course_id,select,type(select))
        user_id = request.user.id
        # 是否勾选
        # if select:
        #     select = True
        # y有效期
        expire = 0

        # 被勾选的商品
        if not course_id:

            try:
                # 将商品的信息储存至redis
                redis_connection = get_redis_connection("cart")
                # redis的管道
                pipeline = redis_connection.pipeline()
                # 开启管道
                pipeline.multi()
                if select == False:
                    select_list = redis_connection.smembers("select_%s" % user_id)
                    print(select_list)
                    for course_id_byte in select_list:
                        course_id=course_id_byte.decode('utf-8')
                        print(course_id)
                        pipeline.srem("select_%s" % user_id, course_id)
                else:
                    cart_list = redis_connection.hgetall("cart_%s" % user_id)
                    for course_id_byte, expire_id_byte in cart_list.items():
                        # print(int(course_id_byte),user_id,int(course_id_byte))
                        pipeline.sadd("select_%s" % user_id, int(course_id_byte))
                # 执行
                pipeline.execute()

                # 获取购物车商品数量
                cart_length = redis_connection.hlen("cart_%s" % user_id)

            except:
                logger.error("购物车数据储存失败")
                return Response({"message": "参数有误，添加购物车失败"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 校验前端传递的参数
            try:
                Course.objects.get(is_show=True, is_delete=False, pk=course_id)
            except Course.DoesNotExist:
                return Response({"message": "参数有误，课程不存在"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # 将商品的信息储存至redis
                redis_connection = get_redis_connection("cart")
                # redis的管道
                pipeline = redis_connection.pipeline()
                # 开启管道
                pipeline.multi()
                # 商品的信息以及对应的有效期   cart_1    1   0
                pipeline.hset("cart_%s" % user_id, course_id, expire)

                if select == False:
                    pipeline.srem("select_%s" % user_id, course_id)
                else:
                    pipeline.sadd("select_%s" % user_id, course_id)
                # 执行
                pipeline.execute()

                # 获取购物车商品数量
                cart_length = redis_connection.hlen("cart_%s" % user_id)

            except:
                logger.error("购物车数据储存失败")
                return Response({"message": "参数有误，添加购物车失败"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "添加购物车成功", "cart_length": cart_length}, status=status.HTTP_200_OK)

    def list_cart(self, request):
        """展示购物车"""
        user_id = request.user.id
        redis_connection = get_redis_connection('cart')
        cart_list_bytes = redis_connection.hgetall("cart_%s" % user_id)
        select_list_bytes = redis_connection.smembers("select_%s" % user_id)

        # 循环从mysql中查询出商品的信息
        data = []
        for course_id_byte, expire_id_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)

            try:
                # 获取购物车中所有的商品信息
                course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                print(type(course))
            except Course.DoesNotExist:
                continue

            data.append({
                'id':course.id,
                'real_price': course.expire_real_price(expire_id),
                "course_img": IMAGE_SRC + course.course_img.url,
                "name": course.name,
                "expire_id": expire_id,
                "selected": True if course_id_byte in select_list_bytes else False,
                # 课程对应的有效期选项
                "expire_list": course.expire_list,
            })
        # 获取购物车商品数量
        cart_length = redis_connection.hlen("cart_%s" % user_id)
        return Response({"message": data, "cart_length": cart_length}, status=status.HTTP_200_OK)
    def del_cart(self,request):
        course_id = request.query_params.get('course_id')
        user_id = request.user.id
        try:
            Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            return Response({"message": "参数有误，课程不存在"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 将商品的信息储存至redis
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

            # 获取购物车商品数量
            cart_length = redis_connection.hlen("cart_%s" % user_id)

        except:
            logger.error("购物车数据删除失败")
            return Response({"message": "参数有误，删除购物车失败"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "删除购物车成功", "cart_length": cart_length}, status=status.HTTP_200_OK)

    def change_expire(self, request):
        """改变redis的课程有效期"""
        user_id = request.user.id
        course_id = request.data.get("course_id")
        expire_id = request.data.get("expire_id")
        print(expire_id, "expire_id")

        try:
            course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)

            # 如果前端传递的有效期选项不是0  则修改对应的有效
            if expire_id > 0:
                expire_item = CourseExpire.objects.filter(is_delete=False, is_show=True, pk=expire_id)
                if not expire_item:
                    raise CourseExpire.DoesNotExist()
        except Course.DoesNotExist:
            return Response({"message": "操作的课程不存在"}, status=status.HTTP_400_BAD_REQUEST)

        redis_connection = get_redis_connection("cart")
        redis_connection.hset("cart_%s" % user_id, course_id, expire_id)

        # TODO  重新计算修改有效期的课程的价格

        return Response({"message": "切换有效期成功", "price": course.expire_real_price(expire_id)})
    def get_select_course(self, request):
        """获取所有被选中的课程"""
        user_id = request.user.id
        redis_connection = get_redis_connection("cart")

        # 获取当前登录用户的购物车的所有商品
        cart_list = redis_connection.hgetall("cart_%s" % user_id)
        select_list = redis_connection.smembers("select_%s" % user_id)

        total_price = 0  # 已勾选的商品总价
        data = []
        print(cart_list)
        for course_id_byte, expire_id_byte in cart_list.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)
            print(course_id,expire_id)

            if course_id_byte in select_list:

                try:
                    # 获取购物车中所有的商品信息
                    course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                except Course.DoesNotExist:
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

                data.append({
                    'id': course.id,
                    # 'price': course.real_price(),
                    "course_img": IMAGE_SRC + course.course_img.url,
                    "name": course.name,
                    # 课程对应的有效期文本
                    "expire_text": expire_text,
                    # 获取有效期真实价格
                    "real_price": "%.2f" % float(expire_real_price),
                    # 原价
                    "price": origin_price,
                })

                # 商品所有的总价
                total_price += float(expire_real_price)

        total_price = "%.2f" % float(total_price)

        return Response({"course_list": data, "total_price": total_price, "message": "获取成功"})
