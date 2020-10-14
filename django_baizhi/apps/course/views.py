from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView,RetrieveAPIView

from course.models import CourseCategory, Course, CourseChapter
from course.pagination import CoursePageNumber
from course.serializers import CourseCategoryModelSerializer, CourseModelSerializer, CourseDetailModelSerializer, \
    CourseChapterModelSerializer,  OrderCourseSerializer
from payments.models import UserCourse


class CourseCategoryAPIView(ListAPIView):
    """课程分类信息查询"""
    queryset = CourseCategory.objects.filter(is_show=True, is_delete=False).order_by("orders")
    serializer_class = CourseCategoryModelSerializer


class CourseAPIView(ListAPIView):
    """课程信息查询"""
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by("orders")
    serializer_class = CourseModelSerializer


class CourseFilterAPIView(ListAPIView):
    """课程信息查询"""
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by("orders")
    serializer_class = CourseModelSerializer

    # 根据不同的分类查询对应的课程
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # 前端分类查询传递的参数
    filter_fields = ("course_category",)

    # 排序
    ordering = ("id", "students", "price")

    # 分页
    pagination_class = CoursePageNumber

class CourseDetailAPIView(RetrieveAPIView):
    """课程信息查询"""
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by("orders")
    serializer_class = CourseDetailModelSerializer
    # lookup_field = 'id'

class CourseChapterLessonAPIView(ListAPIView):
    """课程章节  课程章节对应课时的查询"""
    queryset = CourseChapter.objects.filter(is_show=True, is_delete=False).order_by("orders", "id")
    serializer_class = CourseChapterModelSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['course']

class UserCourseAPIView(ListAPIView):
    queryset = UserCourse.objects.filter(is_show=True, is_delete=False)
    serializer_class = OrderCourseSerializer