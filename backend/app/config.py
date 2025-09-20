import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./homework_app.db")
    
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24 * 7  # 7 days
    
    # Google OAuth
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")

settings = Settings()