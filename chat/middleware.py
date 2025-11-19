import jwt
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.conf import settings

@database_sync_to_async
def _decode_token(token):
    try:
        if settings.JWT_ALGORITHM.upper() == "RS256" and settings.JWT_PUBLIC_KEY:
            payload = jwt.decode(token, settings.JWT_PUBLIC_KEY, algorithms=["RS256"])
        else:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception:
        return None

class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        qs = parse_qs(scope.get("query_string", b"").decode())
        token = qs.get("token", [None])[0]
        if not token:
            # try headers
            headers = dict(scope.get("headers", []))
            auth = headers.get(b"authorization")
            if auth:
                try:
                    token = auth.decode().split("Bearer ")[1]
                except Exception:
                    token = None

        scope["auth_user"] = None
        if token:
            payload = await _decode_token(token)
            if payload:
              
                scope["auth_user"] = {
                    "user_id": str(payload.get("user_id") or payload.get("sub")),
                    "username": payload.get("username") or payload.get("email") or "",
                    "raw_payload": payload,
                    "token": token,
                }
        return await super().__call__(scope, receive, send)

def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(inner)




# ws://127.0.0.1:8000/ws/chat/1/