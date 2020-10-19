from bemoss_lib.utils import security
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User

from jose import jwt
import time
import settings


def get_token(user):
    expiry_time =  time.time() + 25 * 60 * 60
    information = {'user_id': user.id, 'exp': expiry_time, 'iss': 'tokenIssuer1', 'iat': time.time()}
    token = jwt.encode(information, key=settings.SECRET_KEY)
    return token, expiry_time

def check_token(token):
    try:
        info = jwt.decode(token,settings.SECRET_KEY,algorithms='HS256')
        if time.time() < info.get('exp'): #if token is not expired
            return info.get('user_id')
        else:
            return None
    except jwt.JWTError:
        return None

def get_user(token,UserClass):

    user_id = check_token(token)
    if user_id:
        try:
            users = UserClass.objects.all()
            for u in users:
                if u.id == user_id:
                    return u
            return None
        except UserClass.DoesNotExist:
            return  None
    else:
        return  None

def authorize_request(request):

    if 'token' in request.query_params:
        token = request.query_params['token']
    elif 'token' in request.data:
        token = request.data['token']
    else:
        return False, Response({"message": "Token missing"}, status=status.HTTP_400_BAD_REQUEST), None

    user = get_user(token,UserClass=User)
    if user is None:
        return False, Response({"message":"Invalid Token"}, status=status.HTTP_400_BAD_REQUEST), None

    return True, None, user