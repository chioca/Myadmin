from django.contrib import admin
from django.urls import include, path
from user.views import LoginView, CaptchaView, SaveView, EditPasswordView, AvatarView, EditImageView, SearchView

urlpatterns = [
    path('login',LoginView.as_view(),name='Login'), # 登录
    path('captcha',CaptchaView.as_view(),name='Captcha'), # 获取验证码
    path('save', SaveView.as_view(), name='save'), # 保存用户信息
    path('updateUserPwd', EditPasswordView.as_view(), name='updateUserPwd'), # 修改用户密码
    path('uploadImage', EditImageView.as_view(), name='uploadImage'), # 上传头像
    path('updateAvatar', AvatarView.as_view(), name='updateAvatar'), # 更新头像
    path('search', SearchView.as_view(), name='search'), # 用户信息查询
]
