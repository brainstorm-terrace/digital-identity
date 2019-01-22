from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'user-profile', views.UserProfileView.as_view()),
]
