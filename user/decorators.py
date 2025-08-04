from functools import wraps
from django.db import DatabaseError
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied

def standard_api_response(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        try:
            # 调用原始视图函数
            response = view_func(request, *args, **kwargs)
            
            # 如果视图已经返回 JsonResponse，直接透传
            if isinstance(response, JsonResponse):
                return response
                
            # 统一成功响应格式
            return JsonResponse({
                "code": 200,
                "message": "success",
                "data": response if response is not None else {}
            })
            
        except Http404 as e:
            # 处理 404 错误
            return JsonResponse({
                "code": 404,
                "message": str(e) or "Resource not found",
                "data": {}
            }, status=404)
            
        except PermissionDenied as e:
            # 处理 403 权限错误
            return JsonResponse({
                "code": 403,
                "message": str(e) or "Permission denied",
                "data": {}
            }, status=403)
            
        except DatabaseError as e:
            # 处理数据库错误
            return JsonResponse({
                "code": 500,
                "message": "Database error",
                "data": {}
            }, status=500)
            
        except Exception as e:
            # 捕获其他未处理的异常
            return JsonResponse({
                "code": 500,
                "message": str(e) or "Internal server error",
                "data": {}
            }, status=500)
    
    return wrapped_view