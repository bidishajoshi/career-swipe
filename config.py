import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "careerswipe-dev-secret-2026")

    # ── Database ──────────────────────────────────────────────────────────────
    # Use DATABASE_URL if available (Production/Render), otherwise fallback to SQLite
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if DATABASE_URL:
        # Render provides DATABASE_URL starting with postgres://, SQLAlchemy requires postgresql://
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or "sqlite:///careerswipe.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Production-safe connection settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {} if SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {"sslmode": "require"},
    }

    # ── Mail ──────────────────────────────────────────────────────────────────
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME", "noreply@careerswipe.app")

    # ── Uploads ───────────────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join("static", "uploads")
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")
    LOGO_FOLDER   = os.path.join(UPLOAD_FOLDER, "logos")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload
