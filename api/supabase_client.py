"""
Supabase client singleton for SafeHer
"""
from django.conf import settings

_client = None
_service_client = None


def get_supabase():
    """Returns the anon/public Supabase client."""
    global _client
    if _client is None:
        from supabase import create_client
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _client


def get_supabase_service():
    """Returns the service-role Supabase client (admin access)."""
    global _service_client
    if _service_client is None:
        from supabase import create_client
        key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
        _service_client = create_client(settings.SUPABASE_URL, key)
    return _service_client
