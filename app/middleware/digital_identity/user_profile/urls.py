from django.conf.urls import url, include

from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register('profile', views.UserProfileViewSet)
router.register('login', views.LoginViewSet, base_name='login')
urlpatterns = [
    url(r'', include(router.urls)),
    url(r'user-profile', views.UserProfileView.as_view()),
]
