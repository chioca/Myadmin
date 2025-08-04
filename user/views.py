import json
from django.http import JsonResponse
from django.views import View
from user.models import SysUser, SysUserSerializer, SysUserMapper
from rest_framework_jwt.settings import api_settings
from user.decorators import standard_api_response
from menu.models import SysMenu, SysMenuSerializer
from role.models import SysRole
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
            
            print(f"Raw menus: {menus}")  

            sorted_menus = sorted(menus, key=lambda x: x.id) 
            menu_tree = self.buildTreeMenu(sorted_menus)  
            
            print(f"Menu tree: {menu_tree}")  

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