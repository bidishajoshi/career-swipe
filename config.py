import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "careerswipe-secret-2026")
    
    # Render provides DATABASE_URL, local dev can fallback to SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///careerswipe.db")
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail config
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "your@gmail.com")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "your_app_password")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME", "your@gmail.com")
    
    UPLOAD_FOLDER = os.path.join("static", "uploads")
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")
    LOGO_FOLDER = os.path.join(UPLOAD_FOLDER, "logos")
