import base64
import datetime
from io import BytesIO
import json
import random
import uuid
from django.http import JsonResponse
from django.views import View
from django.core.cache import cache
from user.models import SysUser, SysUserSerializer, SysUserMapper
from rest_framework_jwt.settings import api_settings
from user.decorators import standard_api_response
from menu.models import SysMenu, SysMenuSerializer
from role.models import SysRole
from captcha.image import ImageCaptcha
from base64 import *
# Create your views here.




class LoginView(View):
    def buildTreeMenu(self, sysMenuList:SysMenu):
        resultMenuList: list[SysMenu] = list()
        for menu in sysMenuList:
            for e in sysMenuList:
                if e.parent_id == menu.id:
                    if not hasattr(menu, "children"):
                        menu.children = list()
                    menu.children.append(e)
            if menu.parent_id == 0:
                resultMenuList.append(menu)
        return resultMenuList
        
    @standard_api_response
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        try:
            user = SysUser.objects.get(username=username, password=password)
            
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            role_ids = SysRole.objects.filter(
                sysuserrole__user_id=user.id
            ).values_list('id', flat=True)  
            

            menus = SysMenu.objects.filter(
                sysrolemenu__role_id__in=role_ids
            ).distinct()  
            

            sorted_menus = sorted(menus, key=lambda x: x.id) 
            menu_tree = self.buildTreeMenu(sorted_menus)  
            

            serialized_menus = [
                SysMenuSerializer(menu).data for menu in menu_tree
            ]
            
            return {
                'token': token,
                'user': SysUserSerializer(user).data,
                'menuList': serialized_menus
            }

        except Exception as e:
            raise Exception(str(e))  # 异常由装饰器统一处理

class SaveView(View):
    @standard_api_response
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        if data['id'] == -1:
            pass
        else:
            obj_sysuser = SysUser(id=data['id'], username=data['username'], password=data['password'], avatar=data['avatar'], email=data['email'], phonenumber=data['phonenumber'], login_data=data['login_data'], status=data['status'], create_time=data['create_time'], update_time=data['update_time'], remark=data['remark'])
            obj_sysuser.update_time = datetime.now().date()
            obj_sysuser.save()
        return JsonResponse({'code':200, 'message':'Success'})
    
class EditPasswordView(View):
    
    @standard_api_response
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        oldPwd = data['oldPassword']
        newPwd = data['newPassword']
        obj_user = SysUser.objects.get(id=id)
        if obj_user.password == oldPwd:
            obj_user.password = newPwd
            obj_user.update_time = newPwd
            obj_user.save()
            return JsonResponse({'code':200})
        else :
            return JsonResponse({'code':500, 'message':'原密码错误'})

# class TestView(View):
#     def get(self, request):
#         token = request.META.get('HTTP_AUTHORIZATION')
#         if not token:  # 更简洁的判断
#             return JsonResponse({
#                 'code': 401,
#                 'msg': '没有访问权限',
#                 'data': None
#             }, status=401)  

#         try:
#             query_set = SysUser.objects.all()
#             users = [SysUserMapper(user).as_dict() for user in query_set]  # 列表推导简化
#             return JsonResponse({
#                 'code': 200,
#                 'msg': '成功',
#                 'data': users  # 实际数据放在 data 字段
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'code': 500,
#                 'msg': f'服务器错误: {str(e)}',
#                 'data': None
#             }, status=500)

# class JwtTestView(View):
#     def get(self,request):
#         user = SysUser.objects.get(username='marry',password=123456)
#         jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
#         jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#         payload = jwt_payload_handler(user)
#         token = jwt_encode_handler(payload)
#         return JsonResponse({'code':200,'token':token})
    
class CaptchaView(View):

    def get(self, request):
        characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        data = ''.join(random.sample(characters, 4))
        captcha = ImageCaptcha()
        imageData: BytesIO = captcha.generate(data)
        base64_str = base64.b64encode(imageData.getvalue()).decode()
        random_uuid = uuid.uuid4()  # 生成一个随机数
        cache.set(random_uuid, data, timeout=300)  # 存到redis缓存中 有效期5分钟
        return JsonResponse({'code': 200, 'base64str': 'data:image/png;base64,' + base64_str, 'uuid': random_uuid})
    