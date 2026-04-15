import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from extensions import db, migrate, mail
from models import Seeker, Company, JobListing, JobSwipe
from utils.tfidf import parse_resume, match_resume_to_job

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

from werkzeug.exceptions import HTTPException

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    import traceback
    traceback.print_exc()
    return "Internal Server Error - check terminal", 500

os.makedirs(app.config["RESUME_FOLDER"], exist_ok=True)
os.makedirs(app.config["LOGO_FOLDER"], exist_ok=True)

ALLOWED_RESUME = {"pdf", "doc", "docx"}
ALLOWED_LOGO   = {"png", "jpg", "jpeg"}

def allowed_file(filename, allowed):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed

# ── Email Helpers ────────────────────────────────────────────────────────────
def send_application_emails(seeker_email, seeker_name, company_email, company_name, job_title, resume_path):
    # To Company
    msg1 = Message(f"New applicant for {job_title}", recipients=[company_email])
    msg1.html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto">
      <h2 style="color:#00c896">CareerSwipe</h2>
      <p><b>{seeker_name}</b> has applied for <b>{job_title}</b>.</p>
      <p>Resume is attached.</p>
    </div>"""
    if resume_path and os.path.exists(resume_path):
        with app.open_resource(resume_path) as fp:
            msg1.attach(os.path.basename(resume_path), "application/octet-stream", fp.read())
    mail.send(msg1)

    # To Seeker
    msg2 = Message(f"Application sent to {company_name}", recipients=[seeker_email])
    msg2.html = f"<h2>CareerSwipe</h2><p>Your application for <b>{job_title}</b> was sent!</p>"
    mail.send(msg2)

# ════════════════════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ════════════════════════════════════════════════════════════════════════════
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register/seeker", methods=["GET", "POST"])
def register_seeker():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        
        if Seeker.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("register_seeker"))

        resume_file = request.files.get("resume")
        resume_path = ""
        if resume_file and allowed_file(resume_file.filename, ALLOWED_RESUME):
            fname = secure_filename(f"{uuid.uuid4()}_{resume_file.filename}")
            resume_path = os.path.join(app.config["RESUME_FOLDER"], fname)
            resume_file.save(resume_path)

        new_seeker = Seeker(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            email=email,
            password_hash=generate_password_hash(request.form["password"]),
            phone=request.form.get("phone", ""),
            education=request.form.get("education", ""),
            experience=request.form.get("experience", ""),
            skills=request.form.get("skills", ""),
            resume_path=resume_path,
            is_verified=True
        )
        db.session.add(new_seeker)
        db.session.commit()
        
        flash("Account created! You can log in now.", "success")
        return redirect(url_for("login_seeker"))
    return render_template("register_seeker.html")

@app.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        email = request.form["email"].strip().lower()

        if Company.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("register_company"))

        logo_file = request.files.get("logo")
        logo_path = ""
        if logo_file and allowed_file(logo_file.filename, ALLOWED_LOGO):
            fname = secure_filename(f"{uuid.uuid4()}_{logo_file.filename}")
            logo_path = os.path.join(app.config["LOGO_FOLDER"], fname)
            logo_file.save(logo_path)

        new_company = Company(
            company_name=request.form["company_name"],
            email=email,
            password_hash=generate_password_hash(request.form["password"]),
            description=request.form.get("description", ""),
            industry=request.form.get("industry", ""),
            website=request.form.get("website", ""),
            logo_path=logo_path,
            is_verified=True
        )
        db.session.add(new_company)
        db.session.commit()
        
        flash("Company registered!", "success")
        return redirect(url_for("login_company"))
    return render_template("register_company.html")

@app.route("/login/seeker", methods=["GET", "POST"])
def login_seeker():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = Seeker.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, request.form["password"]):
            session["seeker_id"] = user.id
            session["seeker_name"] = user.first_name
            return redirect(url_for("seeker_dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login_seeker.html")

@app.route("/login/company", methods=["GET", "POST"])
def login_company():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        co = Company.query.filter_by(email=email).first()
        
        if co and check_password_hash(co.password_hash, request.form["password"]):
            session["company_id"] = co.id
            session["company_name"] = co.company_name
            return redirect(url_for("company_dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login_company.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ════════════════════════════════════════════════════════════════════════════
#  SEEKER FEATURES
# ════════════════════════════════════════════════════════════════════════════
@app.route("/dashboard/seeker")
def seeker_dashboard():
    if "seeker_id" not in session:
        return redirect(url_for("login_seeker"))
        
    seeker = Seeker.query.get(session["seeker_id"])
    if not seeker:
        session.clear()
        return redirect(url_for("login_seeker"))

    swiped_job_ids = [swipe.job_id for swipe in seeker.swipes]
    
    query = JobListing.query
    if swiped_job_ids:
        query = query.filter(~JobListing.id.in_(swiped_job_ids))
    available_jobs = query.order_by(JobListing.created_at.desc()).limit(20).all()

    resume_text = parse_resume(seeker.resume_path) if seeker.resume_path and os.path.exists(seeker.resume_path) else ""
    
    # Format jobs to match the dictionaries the template expects
    jobs = []
    for job in available_jobs:
        job_data = {
            "id": job.id,
            "title": job.title,
            "company_name": job.company.company_name,
            "logo_path": job.company.logo_path,
            "location": job.location,
            "job_type": job.job_type,
            "salary": job.salary,
            "description": job.description,
            "required_skills": job.required_skills,
            "match_score": match_resume_to_job(resume_text, f"{job.description} {job.required_skills}") if resume_text else 0
        }
        jobs.append(job_data)

    jobs.sort(key=lambda x: x["match_score"], reverse=True)

    # Fetch applied jobs
    swipes = JobSwipe.query.filter_by(seeker_id=session["seeker_id"], direction='right').order_by(JobSwipe.created_at.desc()).all()
    applications = []
    for s in swipes:
        applications.append({
            "title": s.job_listing.title,
            "company_name": s.job_listing.company.company_name,
            "applied_at": s.created_at,
            "status": s.status
        })

    return render_template("seeker_dashboard.html", seeker=seeker, jobs=jobs, applications=applications)

@app.route("/swipe", methods=["POST"])
def swipe():
    if "seeker_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    job_id = data.get("job_id")
    direction = data.get("direction")

    if JobSwipe.query.filter_by(seeker_id=session["seeker_id"], job_id=job_id).first():
        return jsonify({"status": "already_swiped"})

    new_swipe = JobSwipe(
        seeker_id=session["seeker_id"],
        job_id=job_id,
        direction=direction,
        status='pending'
    )
    db.session.add(new_swipe)
    db.session.commit()

    if direction == "right":
        seeker = Seeker.query.get(session["seeker_id"])
        job = JobListing.query.get(job_id)
        if job and job.company:
            try:
                send_application_emails(
                    seeker.email, f"{seeker.first_name} {seeker.last_name}", 
                    job.company.email, job.company.company_name, 
                    job.title, seeker.resume_path
                )
            except: pass

    return jsonify({"status": "ok", "direction": direction})

@app.route("/profile/seeker", methods=["GET", "POST"])
def edit_seeker_profile():
    if "seeker_id" not in session:
        return redirect(url_for("login_seeker"))

    seeker = Seeker.query.get(session["seeker_id"])

    if request.method == "POST":
        resume_file = request.files.get("resume")
        resume_path = request.form.get("existing_resume", "")
        if resume_file and allowed_file(resume_file.filename, ALLOWED_RESUME):
            fname = secure_filename(f"{uuid.uuid4()}_{resume_file.filename}")
            resume_path = os.path.join(app.config["RESUME_FOLDER"], fname)
            resume_file.save(resume_path)

        seeker.first_name = request.form["first_name"]
        seeker.last_name = request.form["last_name"]
        seeker.phone = request.form.get("phone", "")
        seeker.education = request.form.get("education", "")
        seeker.experience = request.form.get("experience", "")
        seeker.skills = request.form.get("skills", "")
        seeker.resume_path = resume_path
        
        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("seeker_dashboard"))

    return render_template("edit_seeker_profile.html", seeker=seeker)

# ════════════════════════════════════════════════════════════════════════════
#  COMPANY FEATURES
# ════════════════════════════════════════════════════════════════════════════
@app.route("/dashboard/company")
def company_dashboard():
    if "company_id" not in session:
        return redirect(url_for("login_company"))
        
    company = Company.query.get(session["company_id"])
    if not company:
        session.clear()
        return redirect(url_for("login_company"))

    jobs = JobListing.query.filter_by(company_id=session["company_id"]).order_by(JobListing.created_at.desc()).all()
    
    # Applicants to this company's jobs
    swipes = JobSwipe.query.join(JobListing).filter(
        JobListing.company_id == session["company_id"],
        JobSwipe.direction == 'right'
    ).order_by(JobSwipe.created_at.desc()).all()
    
    applicants = []
    for sw in swipes:
        applicants.append({
            "seeker_id": sw.seeker.id,
            "first_name": sw.seeker.first_name,
            "last_name": sw.seeker.last_name,
            "email": sw.seeker.email,
            "skills": sw.seeker.skills,
            "resume_path": sw.seeker.resume_path,
            "job_title": sw.job_listing.title,
            "applied_at": sw.created_at,
            "status": sw.status,
            "swipe_id": sw.id
        })

    return render_template("company_dashboard.html", company=company, jobs=jobs, applicants=applicants)

@app.route("/jobs/post", methods=["GET", "POST"])
def post_job():
    if "company_id" not in session:
        return redirect(url_for("login_company"))
        
    if request.method == "POST":
        new_job = JobListing(
            company_id=session["company_id"],
            title=request.form["title"],
            description=request.form["description"],
            required_skills=request.form.get("required_skills", ""),
            location=request.form.get("location", ""),
            job_type=request.form.get("job_type", "Full-time"),
            salary=request.form.get("salary", "")
        )
        db.session.add(new_job)
        db.session.commit()
        
        flash("Job posted successfully!", "success")
        return redirect(url_for("company_dashboard"))
        
    return render_template("post_job.html")

@app.route("/applicant/<int:swipe_id>/<action>")
def update_applicant(swipe_id, action):
    if "company_id" not in session:
        return redirect(url_for("login_company"))
        
    swipe = JobSwipe.query.get_or_404(swipe_id)
    
    # Ensure this swipe belongs to a job from the logged-in company
    if swipe.job_listing.company_id != session["company_id"]:
        flash("Unauthorized action.", "error")
        return redirect(url_for("company_dashboard"))
        
    swipe.status = action + "ed"
    db.session.commit()
    
    seeker = swipe.seeker
    job = swipe.job_listing
    msg = Message(f"Application Update: {job.title}", recipients=[seeker.email])
    msg.html = f"<p>Hi {seeker.first_name}, your application for {job.title} was {action}ed.</p>"
    try: mail.send(msg)
    except: pass
    
    flash(f"Applicant {action}ed.", "success")
    return redirect(url_for("company_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
