from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'user-profile/$', views.UserProfileView.as_view()),
    url(r'user-profile/(?P<pk>\d+)/$', views.UserProfileView.as_view()),
]
