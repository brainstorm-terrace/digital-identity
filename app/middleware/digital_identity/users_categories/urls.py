from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'user-detail', views.UserDetailsView.as_view()),
]