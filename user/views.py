import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from bpmappers.djangomodel import ModelMapper
from user.models import SysUser
from rest_framework_jwt.settings import api_settings
from user.decorators import standard_api_response
# Create your views here.

class SysUserMapper(ModelMapper):
    class Meta:
        model = SysUser


class LoginView(View):
    @standard_api_response
    def post(self,request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        print(username)
        print(password)
        user = SysUser.objects.get(username=username, password=password)
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return {'token':token}

class TestView(View):
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:  # 更简洁的判断
            return JsonResponse({
                'code': 401,
                'msg': '没有访问权限',
                'data': None
            }, status=401)  

        try:
            query_set = SysUser.objects.all()
            users = [SysUserMapper(user).as_dict() for user in query_set]  # 列表推导简化
            return JsonResponse({
                'code': 200,
                'msg': '成功',
                'data': users  # 实际数据放在 data 字段
            })
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'msg': f'服务器错误: {str(e)}',
                'data': None
            }, status=500)

class JwtTestView(View):
    def get(self,request):
        user = SysUser.objects.get(username='marry',password=123456)
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return JsonResponse({'code':200,'token':token})