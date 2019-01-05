from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'user-detail', views.UserDetailsView.as_view()),
    url(r'user-detail/(?P<pk>\d+)/$', views.UserDetailsView.as_view()),
]