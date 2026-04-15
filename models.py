from extensions import db
from datetime import datetime

class Seeker(db.Model):
    __tablename__ = 'seekers'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30))
    education = db.Column(db.String(255))
    experience = db.Column(db.Text)
    skills = db.Column(db.Text)
    resume_path = db.Column(db.String(500))
    verification_token = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    swipes = db.relationship('JobSwipe', backref='seeker', lazy=True, cascade='all, delete-orphan')

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    industry = db.Column(db.String(150))
    website = db.Column(db.String(300))
    logo_path = db.Column(db.String(500))
    verification_token = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    jobs = db.relationship('JobListing', backref='company', lazy=True, cascade='all, delete-orphan')

class JobListing(db.Model):
    __tablename__ = 'job_listings'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text)
    location = db.Column(db.String(255))
    job_type = db.Column(db.String(50), default='Full-time')
    salary = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    swipes = db.relationship('JobSwipe', backref='job_listing', lazy=True, cascade='all, delete-orphan')

class JobSwipe(db.Model):
    __tablename__ = 'job_swipes'
    
    id = db.Column(db.Integer, primary_key=True)
    seeker_id = db.Column(db.Integer, db.ForeignKey('seekers.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_listings.id', ondelete='CASCADE'), nullable=False)
    direction = db.Column(db.String(10), nullable=False) # 'left' or 'right'
    status = db.Column(db.String(20), default='pending') # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
