"""
JWT helpers for SafeHer
"""
import jwt
import datetime
from django.conf import settings
from rest_framework.response import Response
from functools import wraps


def generate_token(payload: dict, hours: int = None) -> str:
    expiry = hours or settings.JWT_EXPIRY_HOURS
    payload = {**payload, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expiry)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request(request) -> str | None:
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth[7:]
    return None


def require_auth(view_func):
    """Decorator: requires valid user JWT."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = get_token_from_request(request)
        if not token:
            return Response({'error': 'Authentication required'}, status=401)
        payload = decode_token(token)
        if not payload or payload.get('role') not in ('user', 'admin'):
            return Response({'error': 'Invalid or expired token'}, status=401)
        request.user_payload = payload
        return view_func(request, *args, **kwargs)
    return wrapper


def require_admin(view_func):
    """Decorator: requires valid admin JWT."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = get_token_from_request(request)
        if not token:
            return Response({'error': 'Admin authentication required'}, status=401)
        payload = decode_token(token)
        if not payload or payload.get('role') != 'admin':
            return Response({'error': 'Admin access required'}, status=403)
        request.user_payload = payload
        return view_func(request, *args, **kwargs)
    return wrapper
