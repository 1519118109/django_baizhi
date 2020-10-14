from django.urls import path

from course import views

urlpatterns = [
    path("category/", views.CourseCategoryAPIView.as_view()),
    path("detail/<str:pk>/", views.CourseDetailAPIView.as_view()),
    path("filter_course/", views.CourseFilterAPIView.as_view()),
    path("filter_course/<str:pk>/", views.CourseFilterAPIView.as_view()),
    path("chapter/", views.CourseChapterLessonAPIView.as_view()),
    path('user_course/',views.UserCourseAPIView.as_view())
]
