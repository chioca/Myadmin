from django.contrib import admin
from django.urls import include, path
from user.views import LoginView, CaptchaView

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('test',TestView.as_view(),name='Test'),
    # path('jwt_test',JwtTestView.as_view(),name='Test'),
    path('login',LoginView.as_view(),name='Login'),
    path('captcha',CaptchaView.as_view(),name='Captcha')
]
