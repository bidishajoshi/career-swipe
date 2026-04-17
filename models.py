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

    # ✅ NEW JOB-PORTAL / INDEED STYLE FIELDS
    gender = db.Column(db.String(20))
    dob = db.Column(db.String(20))

    experience_type = db.Column(db.String(50))      # fresher / experienced
    career_field = db.Column(db.String(100))        # IT / Marketing / Finance etc
    job_status = db.Column(db.String(50))           # searching / employed / open to offers
    job_location_type = db.Column(db.String(50))    # remote / onsite / hybrid
    shift_preference = db.Column(db.String(50))     # day / night / flexible

    verification_token = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    swipes = db.relationship(
        'JobSwipe',
        backref='seeker',
        lazy=True,
        cascade='all, delete-orphan'
    )


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

    jobs = db.relationship(
        'JobListing',
        backref='company',
        lazy=True,
        cascade='all, delete-orphan'
    )


class JobListing(db.Model):
    __tablename__ = 'job_listings'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id', ondelete='CASCADE'),
        nullable=False
    )
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text)
    location = db.Column(db.String(255))
    job_type = db.Column(db.String(50), default='Full-time')
    job_location_type = db.Column(db.String(50), default='Onsite') # Onsite, Remote, Hybrid
    salary = db.Column(db.String(100))
    max_salary = db.Column(db.Integer)
    experience_level = db.Column(db.String(50), default='Entry Level') # Entry, Mid, Senior, Expert
    min_experience = db.Column(db.Integer, default=0)
    tags = db.Column(db.Text) # comma separated keywords
    is_boosted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    swipes = db.relationship(
        'JobSwipe',
        backref='job_listing',
        lazy=True,
        cascade='all, delete-orphan'
    )


class JobSwipe(db.Model):
    __tablename__ = 'job_swipes'
    
    id = db.Column(db.Integer, primary_key=True)
    seeker_id = db.Column(
        db.Integer,
        db.ForeignKey('seekers.id', ondelete='CASCADE'),
        nullable=False
    )
    job_id = db.Column(
        db.Integer,
        db.ForeignKey('job_listings.id', ondelete='CASCADE'),
        nullable=False
    )
    direction = db.Column(db.String(10), nullable=False)  # left / right
    status = db.Column(db.String(20), default='pending')   # pending / shortlisted / rejected / interview
    
    # AI Scores
    ats_score = db.Column(db.Float, default=0.0)
    match_score = db.Column(db.Float, default=0.0)
    ai_rank_score = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    user_type = db.Column(db.String(20), nullable=False, index=True) # 'seeker' or 'company'
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='system') # application / accepted / rejected / interview / system
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)