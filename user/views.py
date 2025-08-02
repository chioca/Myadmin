from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from bpmappers.djangomodel import ModelMapper
from user.models import SysUser

# Create your views here.

class SysUserMapper(ModelMapper):
    class Meta:
        model = SysUser
class TestView(View):
    def get(self,request):
        query_set = SysUser.objects.all()
        # print(query_set)
        # userList_dict = query_set.values() #
        # print(userList_dict)
        users = []
        for user in query_set:
            users.append(SysUserMapper(user).as_dict())
        return JsonResponse(users,safe=False)