from django.utils.deprecation import MiddlewareMixin
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError
from django.http import HttpResponse
from rest_framework_jwt.settings import api_settings
class JwtAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        white_list = ['/user/login']
        path = request.path
        if path not in white_list and not path.startswith('/media'):
            token = request.META.get('HTTP_AUTHORIZATION')
            try:
                jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
                jwt_decode_handler(token)
            except ExpiredSignatureError:
                return HttpResponse('Token过期,请重新登录!')
            except InvalidTokenError:
                return HttpResponse('Token验证失败!')
            except PyJWTError:
                return HttpResponse('Token验证异常!')
                
            
        