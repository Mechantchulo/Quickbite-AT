from app.core.config import settings

def build_at_headers() -> dict[str, str]:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    
    if settings.AT_AUTH_TOKEN and settings.AT_AUTH_TOKEN.strip():
        headers["authToken"] = settings.AT_AUTH_TOKEN.strip()
    elif settings.AT_API_KEY and settings.AT_API_KEY.strip():
        headers["apiKey"] = settings.AT_API_KEY.strip()
    else:
        raise ValueError("Missing AT_API_KEY or AT_AUTH_TOKEN")
    return headers
