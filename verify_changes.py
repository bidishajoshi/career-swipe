#!/usr/bin/env python
"""Verification script to check all implemented changes"""

import os

print("=" * 70)
print("VERIFICATION REPORT: Career Swipe Improvements & Fixes")
print("=" * 70)

# 1. Check CSRF Tokens in Templates
print("\n1. CSRF TOKEN VERIFICATION")
print("-" * 70)

templates_to_check = [
    'templates/login_seeker.html',
    'templates/login_company.html',
    'templates/register_seeker.html',
    'templates/register_company.html',
    'templates/post_job.html',
    'templates/upload_resume.html',
    'templates/edit_seeker_profile.html',
    'templates/edit_company_profile.html',
    'templates/eligibility_form.html',
    'templates/edit_job.html',
]

csrf_found = 0
for template in templates_to_check:
    if os.path.exists(template):
        with open(template, 'r') as f:
            content = f.read()
            has_csrf = 'csrf_token()' in content or 'csrf_token' in content
            status = "✓" if has_csrf else "✗"
            print(f"{status} {template}")
            if has_csrf:
                csrf_found += 1

print(f"\nTotal templates with CSRF tokens: {csrf_found}/{len(templates_to_check)}")

# 2. Check Database Model Fields
print("\n2. DATABASE MODEL FIELDS")
print("-" * 70)

with open('models.py', 'r') as f:
    content = f.read()
    
    fields_to_check = {
        'interview_stage': 'Interview stage tracking',
        'offer_extended_date': 'Offer extended date',
        'offer_accepted_date': 'Offer accepted date',
        'hired_date': 'Hire date tracking',
    }
    
    for field, desc in fields_to_check.items():
        found = field in content
        status = "✓" if found else "✗"
        print(f"{status} {field}: {desc}")

# 3. Check Jobs Routes
print("\n3. JOBS ROUTES")
print("-" * 70)

with open('apps/routes/jobs.py', 'r') as f:
    content = f.read()
    
    routes_to_check = {
        'edit_job': 'Job edit route',
        'delete_job': 'Job delete route',
        'view_job': 'Job view route',
    }
    
    for route, desc in routes_to_check.items():
        found = f"def {route}" in content
        status = "✓" if found else "✗"
        print(f"{status} {route}: {desc}")

# 4. Check Dashboard Tabs
print("\n4. COMPANY DASHBOARD TABS")
print("-" * 70)

with open('templates/company_dashboard.html', 'r') as f:
    content = f.read()
    
    tabs_to_check = {
        'id="posted-jobs"': 'Posted Jobs tab',
        'id="applications"': 'Applications tab',
        'id="shortlisted"': 'Shortlisted tab',
        'id="interviews"': 'Interviews tab',
        'id="hired"': 'Hired tab',
    }
    
    for tab_id, desc in tabs_to_check.items():
        found = tab_id in content
        status = "✓" if found else "✗"
        print(f"{status} {desc}")

# 5. Check Edit/Delete Buttons
print("\n5. JOB MANAGEMENT BUTTONS")
print("-" * 70)

buttons_to_check = {
    'confirmDeleteJob': 'Delete button JavaScript',
    'edit_job': 'Edit button link',
}

for button, desc in buttons_to_check.items():
    found = button in content
    status = "✓" if found else "✗"
    print(f"{status} {desc}")

# 6. Check Application Status Actions
print("\n6. APPLICATION STATUS ACTIONS")
print("-" * 70)

with open('apps/routes/company.py', 'r') as f:
    content = f.read()
    
    actions_to_check = {
        'shortlist': 'Shortlist action',
        'interview': 'Interview action',
        'accept': 'Accept/Hire action',
        'reject': 'Reject action',
    }
    
    for action, desc in actions_to_check.items():
        found = f"'{action}'" in content
        status = "✓" if found else "✗"
        print(f"{status} {desc}")

# 7. Check Eligibility Questions Simplified
print("\n7. ELIGIBILITY QUESTIONS (SIMPLIFIED)")
print("-" * 70)

with open('apps/services/eligibility_service.py', 'r') as f:
    content = f.read()
    
    # Count question definitions
    legal_check = "Are you legally eligible to work in your country?" in content
    availability = "Are you available for the required job type" in content
    experience = "Years of relevant work experience?" in content
    
    print(f"{'✓' if legal_check else '✗'} Legal eligibility question")
    print(f"{'✓' if availability else '✗'} Availability question")
    print(f"{'✓' if experience else '✗'} Work experience question")
    
    # Check removed questions
    age_removed = "What is your age?" not in content
    relocation_removed = "Are you willing to relocate" not in content
    
    print(f"\n{'✓' if age_removed else '✗'} Age question removed")
    print(f"{'✓' if relocation_removed else '✗'} Relocation question removed")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
