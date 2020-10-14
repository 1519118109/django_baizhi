from django.urls import path

from home import views

urlpatterns = [
    path("banners/", views.BannerListAPIView.as_view()),
    path("header/", views.HeaderListAPIView.as_view()),
    path("footer/", views.FooterListAPIView.as_view()),
]