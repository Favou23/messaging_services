import os
import httpx
from django.conf import settings

AUTH_API_URL = getattr(settings, "AUTH_API_URL", "http://auth_service:8080")
AUTH_PROFILE_ENDPOINT = getattr(settings, "AUTH_PROFILE_ENDPOINT", "api/users/profile/")

async def fetch_profile_async(token):
    if not AUTH_API_URL:
        return None
    url = AUTH_API_URL.rstrip("/") + "/" + AUTH_PROFILE_ENDPOINT.lstrip("/")
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.get(url, headers=headers)
            if r.status_code == 200:
                return r.json()
        except Exception:
            return None
    return None
    

def fetch_profile_sync(token):
    if not AUTH_API_URL:
        return None
    url = AUTH_API_URL.rstrip("/") + "/" + AUTH_PROFILE_ENDPOINT.lstrip("/")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = httpx.get(url, headers=headers, timeout=5.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None
