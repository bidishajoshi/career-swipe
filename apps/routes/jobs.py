"""
app/routes/jobs.py – Job listing routes.
Covers: post a job, view job details, edit job, delete job (company only).
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify,
)
from datetime import datetime

from ..extensions import db
from ..models import JobListing, JobSwipe

jobs_bp = Blueprint('jobs', __name__)


def _require_company():
    """Return the logged-in Company or None."""
    company_id = session.get('company_id')
    if not company_id:
        return None
    from ..models import Company
    company = db.session.get(Company, company_id)
    if not company:
        session.clear()
    return company


@jobs_bp.route('/jobs/post', methods=['GET', 'POST'])
def post_job():
    if 'company_id' not in session:
        return redirect(url_for('auth.login_company'))

    if request.method == 'POST':
        job = JobListing(
            company_id        = session['company_id'],
            title             = request.form['title'],
            description       = request.form['description'],
            required_skills   = request.form.get('required_skills', ''),
            location          = request.form.get('location', ''),
            job_type          = request.form.get('job_type', 'Full-time'),
            job_location_type = request.form.get('job_location_type', 'Onsite'),
            experience_level  = request.form.get('experience_level', 'Entry Level'),
            min_experience    = request.form.get('min_experience', 0, type=int),
            salary            = request.form.get('salary', ''),
            max_salary        = request.form.get('max_salary', 0, type=int),
            tags              = request.form.get('tags', ''),
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('company.company_dashboard'))

    return render_template('post_job.html')


# ── View Job Details ─────────────────────────────────────────────────────────
@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
def view_job(job_id):
    """View job details (accessible to anyone)"""
    job = JobListing.query.get(job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('seeker.seeker_dashboard'))
    
    return render_template('view_job.html', job=job)


# ── Edit Job ─────────────────────────────────────────────────────────────────
@jobs_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
def edit_job(job_id):
    """Edit job (company only)"""
    company = _require_company()
    if not company:
        return redirect(url_for('auth.login_company'))
    
    job = JobListing.query.get(job_id)
    if not job or job.company_id != company.id:
        flash('Job not found or unauthorized', 'error')
        return redirect(url_for('company.company_dashboard'))
    
    if request.method == 'POST':
        job.title             = request.form['title']
        job.description       = request.form['description']
        job.required_skills   = request.form.get('required_skills', '')
        job.location          = request.form.get('location', '')
        job.job_type          = request.form.get('job_type', 'Full-time')
        job.job_location_type = request.form.get('job_location_type', 'Onsite')
        job.experience_level  = request.form.get('experience_level', 'Entry Level')
        job.min_experience    = request.form.get('min_experience', 0, type=int)
        job.salary            = request.form.get('salary', '')
        job.max_salary        = request.form.get('max_salary', 0, type=int)
        job.tags              = request.form.get('tags', '')
        
        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('company.company_dashboard'))
    
    return render_template('edit_job.html', job=job)


# ── Delete Job ───────────────────────────────────────────────────────────────
@jobs_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    """Delete job (company only) - preserves application history"""
    company = _require_company()
    if not company:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    job = JobListing.query.get(job_id)
    if not job or job.company_id != company.id:
        return jsonify({'success': False, 'message': 'Job not found or unauthorized'}), 403
    
    try:
        # Note: Applications are preserved due to cascade behavior configured in models
        # Job is deleted but applications remain in database with historical data
        db.session.delete(job)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Job deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
