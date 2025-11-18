










# messaging_services/chat/auth_client.py

import httpx
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

# Enable debug for now - remove these after testing
DEBUG_MODE = True

def get_auth_url():
    """Get the auth service URL from settings"""
    url = getattr(settings, "AUTH_API_URL", "http://authservice:8080")
    if DEBUG_MODE:
        print(f"📍 AUTH_API_URL from settings: {url}")
    return url

def get_profile_endpoint():
    """Get the profile endpoint from settings"""
    endpoint = getattr(settings, "AUTH_PROFILE_ENDPOINT", "api/users/profile/")
    if DEBUG_MODE:
        print(f"📍 AUTH_PROFILE_ENDPOINT from settings: {endpoint}")
    return endpoint


def fetch_profile_sync(token):
    """
    Fetch user profile from auth service synchronously.
    
    Args:
        token: JWT access token
        
    Returns:
        dict: User profile data with keys: id, username, email
        None: If authentication fails or user not found
    """
    if not token:
        logger.error("No token provided to fetch_profile_sync")
        return None
    
    auth_url = get_auth_url()
    endpoint = get_profile_endpoint()
    
    # Construct URL carefully
    url = f"{auth_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {"Authorization": f"Bearer {token}"}
    
    if DEBUG_MODE:
        print("=" * 70)
        print("🔍 FETCHING USER PROFILE")
        print(f"   URL: {url}")
        print(f"   Token: {token[:50]}...{token[-10:]}")
        print("=" * 70)
    
    try:
        response = httpx.get(url, headers=headers, timeout=10.0)
        
        if DEBUG_MODE:
            print(f"📥 Response Status: {response.status_code}")
            print(f"📥 Response Headers: {dict(response.headers)}")
            print(f"📥 Response Body: {response.text[:500]}")
            print("=" * 70)
        
        if response.status_code == 200:
            try:
                profile = response.json()
                logger.info(f"✓ Successfully fetched profile for user ID: {profile.get('id')}")
                
                if DEBUG_MODE:
                    print(f"✅ Profile fetched successfully: {profile}")
                
                return profile
                
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                if DEBUG_MODE:
                    print(f"❌ JSON parse error: {e}")
                return None
        
        elif response.status_code == 401:
            logger.warning(f"Authentication failed: {response.text[:200]}")
            if DEBUG_MODE:
                print(f"❌ 401 Unauthorized: {response.text[:200]}")
            return None
            
        elif response.status_code == 404:
            logger.warning(f"Profile endpoint not found: {url}")
            if DEBUG_MODE:
                print(f"❌ 404 Not Found: {url}")
            return None
            
        else:
            logger.error(f"Auth service returned status {response.status_code}: {response.text[:200]}")
            if DEBUG_MODE:
                print(f"❌ Unexpected status {response.status_code}: {response.text[:200]}")
            return None
            
    except httpx.ConnectError as e:
        logger.error(f"Cannot connect to auth service at {url}: {str(e)}")
        if DEBUG_MODE:
            print(f"❌ CONNECTION ERROR: Cannot reach {url}")
            print(f"   Error: {str(e)}")
        return None
        
    except httpx.TimeoutException:
        logger.error(f"Auth service request timed out: {url}")
        if DEBUG_MODE:
            print(f"❌ TIMEOUT: Request to {url} took too long")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error fetching profile: {type(e).__name__}: {str(e)}")
        if DEBUG_MODE:
            print(f"❌ UNEXPECTED ERROR: {type(e).__name__}")
            print(f"   Message: {str(e)}")
            import traceback
            traceback.print_exc()
        return None


def verify_user_exists(user_id, token):
    """
    Verify a specific user exists in auth service.
    
    Args:
        user_id: User ID to verify
        token: JWT access token
        
    Returns:
        bool: True if user exists and is accessible, False otherwise
    """
    if not user_id or not token:
        logger.error("Missing user_id or token in verify_user_exists")
        return False
    
    auth_url = get_auth_url()
    url = f"{auth_url.rstrip('/')}/api/users/{user_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    
    if DEBUG_MODE:
        print(f"🔍 Verifying user {user_id} at: {url}")
    
    try:
        response = httpx.get(url, headers=headers, timeout=5.0)
        
        if DEBUG_MODE:
            print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            logger.debug(f"✓ User {user_id} exists")
            if DEBUG_MODE:
                print(f"   ✅ User {user_id} verified")
            return True
        elif response.status_code == 404:
            logger.warning(f"User {user_id} not found in auth service")
            if DEBUG_MODE:
                print(f"   ❌ User {user_id} not found (404)")
            return False
        elif response.status_code == 401:
            logger.warning(f"Unauthorized when verifying user {user_id}")
            if DEBUG_MODE:
                print(f"   ❌ Unauthorized (401)")
            return False
        else:
            logger.error(f"Auth service returned {response.status_code} for user {user_id}")
            if DEBUG_MODE:
                print(f"   ❌ Unexpected status: {response.status_code}")
            return False
            
    except httpx.ConnectError as e:
        logger.error(f"Cannot connect to auth service: {str(e)}")
        if DEBUG_MODE:
            print(f"   ❌ Connection error: {str(e)}")
        return False
        
    except Exception as e:
        logger.error(f"Error verifying user {user_id}: {type(e).__name__}: {str(e)}")
        if DEBUG_MODE:
            print(f"   ❌ Error: {type(e).__name__}: {str(e)}")
        return False


async def fetch_profile_async(token):
    """
    Fetch user profile from auth service asynchronously.
    Used by WebSocket consumers.
    
    Args:
        token: JWT access token
        
    Returns:
        dict: User profile data
        None: If authentication fails
    """
    if not token:
        logger.error("No token provided to fetch_profile_async")
        return None
    
    auth_url = get_auth_url()
    endpoint = get_profile_endpoint()
    url = f"{auth_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {"Authorization": f"Bearer {token}"}
    
    if DEBUG_MODE:
        print(f"🔍 [ASYNC] Fetching profile from: {url}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers)
            
            if DEBUG_MODE:
                print(f"📥 [ASYNC] Status: {response.status_code}")
            
            if response.status_code == 200:
                profile = response.json()
                logger.info(f"✓ [ASYNC] Fetched profile for user ID: {profile.get('id')}")
                return profile
            else:
                logger.warning(f"[ASYNC] Auth failed with status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"[ASYNC] Error fetching profile: {str(e)}")
            if DEBUG_MODE:
                print(f"❌ [ASYNC] Error: {str(e)}")
            return None