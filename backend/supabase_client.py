import os
from functools import lru_cache

from supabase import create_client, Client


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Return a cached instance of the Supabase client.

    The function expects two environment variables to be set:
    SUPABASE_URL: The unique project URL, e.g. https://xyzcompany.supabase.co
    SUPABASE_KEY: The anon or service role key. **Never** hard-code the key –
        it should be provided via environment variables or secret managers.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY environment variables must be set to initialise the Supabase client."
        )

    return create_client(url, key)


__all__ = ["get_supabase_client"]
