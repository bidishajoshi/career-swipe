import argparse
import csv
import json
import random
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from werkzeug.security import generate_password_hash


SEED = 20260602
DEFAULT_PASSWORD = "password123"
OUTPUT_DIR = Path("data")


FIRST_NAMES = [
    "Aarav", "Aisha", "Amelia", "Arjun", "Avery", "Chloe", "Daniel", "Dev", "Elena", "Ethan",
    "Fatima", "Grace", "Hannah", "Imran", "Isabella", "Jacob", "Jasmine", "Kai", "Leah", "Liam",
    "Maya", "Mia", "Nadia", "Noah", "Olivia", "Omar", "Priya", "Rohan", "Sofia", "Vikram",
    "Zara", "Nikhil", "Meera", "Lucas", "Emma", "Anika", "Ryan", "Sara", "Mateo", "Lina",
]

LAST_NAMES = [
    "Sharma", "Patel", "Nguyen", "Garcia", "Khan", "Singh", "Johnson", "Williams", "Brown", "Chen",
    "Kim", "Rodriguez", "Ahmed", "Miller", "Wilson", "Davis", "Thomas", "Martinez", "Lopez", "Ali",
    "Gurung", "Rai", "Tamang", "Adhikari", "Bhandari", "Maharjan", "Hernandez", "Anderson", "Clark", "Lewis",
]

LOCATIONS = [
    ("Kathmandu, Nepal", "+977", "Nepal"),
    ("Lalitpur, Nepal", "+977", "Nepal"),
    ("Pokhara, Nepal", "+977", "Nepal"),
    ("Bengaluru, India", "+91", "India"),
    ("Hyderabad, India", "+91", "India"),
    ("Delhi, India", "+91", "India"),
    ("Dubai, UAE", "+971", "United Arab Emirates"),
    ("Toronto, Canada", "+1", "Canada"),
    ("Vancouver, Canada", "+1", "Canada"),
    ("New York, NY", "+1", "United States"),
    ("Austin, TX", "+1", "United States"),
    ("London, UK", "+44", "United Kingdom"),
    ("Singapore", "+65", "Singapore"),
    ("Sydney, Australia", "+61", "Australia"),
]

UNIVERSITIES = {
    "Technology": ["Kathmandu University", "Tribhuvan University", "IIT Delhi", "University of Toronto", "National University of Singapore"],
    "Product": ["Delhi University", "University of British Columbia", "London School of Economics", "Kathmandu University"],
    "Design": ["Srishti Manipal Institute", "RMIT University", "University of the Arts London", "NID Ahmedabad"],
    "Marketing": ["Delhi University", "Kathmandu University School of Management", "University of Sydney", "York University"],
    "Finance": ["Tribhuvan University", "University of Toronto", "Singapore Management University", "LSE"],
    "Operations": ["Pokhara University", "IIT Bombay", "University of Texas at Austin", "University of British Columbia"],
    "HR": ["Kathmandu University School of Management", "Delhi University", "University of Leeds", "York University"],
}

DEGREES = [
    "BSc Computer Science", "BTech Information Technology", "Bachelor of Business Administration",
    "MBA", "MSc Data Science", "Bachelor of Design", "Bachelor of Commerce",
    "MSc Information Systems", "BSc Electrical Engineering", "BA Communications",
]

ROLE_PROFILES = {
    "Software Engineer": {
        "field": "Technology",
        "skills": ["Python", "JavaScript", "React", "Node.js", "SQL", "REST APIs", "Git", "Docker", "AWS", "TypeScript", "PostgreSQL", "Unit Testing", "CI/CD", "Microservices"],
        "positions": ["Software Engineer", "Backend Developer", "Full Stack Developer", "Frontend Engineer"],
        "salary": (45000, 140000),
    },
    "Data Analyst": {
        "field": "Technology",
        "skills": ["SQL", "Python", "Power BI", "Tableau", "Excel", "Data Cleaning", "A/B Testing", "Looker", "Statistics", "ETL", "dbt", "BigQuery"],
        "positions": ["Data Analyst", "Business Intelligence Analyst", "Reporting Analyst"],
        "salary": (38000, 105000),
    },
    "Product Manager": {
        "field": "Product",
        "skills": ["Product Strategy", "Roadmapping", "User Research", "Jira", "Analytics", "A/B Testing", "Stakeholder Management", "Agile", "Figma", "Go-to-Market"],
        "positions": ["Associate Product Manager", "Product Manager", "Product Owner"],
        "salary": (55000, 150000),
    },
    "UX Designer": {
        "field": "Design",
        "skills": ["Figma", "Wireframing", "Prototyping", "Design Systems", "User Research", "Usability Testing", "Accessibility", "Journey Mapping", "Adobe Creative Suite"],
        "positions": ["UX Designer", "Product Designer", "UI Designer"],
        "salary": (40000, 120000),
    },
    "Digital Marketing Specialist": {
        "field": "Marketing",
        "skills": ["SEO", "Google Ads", "Meta Ads", "Content Strategy", "Google Analytics", "Email Marketing", "CRM", "Copywriting", "Marketing Automation"],
        "positions": ["Digital Marketing Specialist", "Growth Marketer", "Performance Marketing Analyst"],
        "salary": (30000, 95000),
    },
    "Finance Analyst": {
        "field": "Finance",
        "skills": ["Financial Modeling", "Excel", "Budgeting", "Forecasting", "Variance Analysis", "Power BI", "Accounting", "QuickBooks", "Risk Analysis"],
        "positions": ["Finance Analyst", "FP&A Analyst", "Accountant"],
        "salary": (35000, 105000),
    },
    "Operations Coordinator": {
        "field": "Operations",
        "skills": ["Logistics", "Vendor Management", "Excel", "Inventory Planning", "Process Improvement", "ERP", "Supply Chain", "Data Entry", "SOPs"],
        "positions": ["Operations Coordinator", "Supply Chain Analyst", "Logistics Coordinator"],
        "salary": (28000, 85000),
    },
    "HR Generalist": {
        "field": "HR",
        "skills": ["Recruiting", "Onboarding", "Employee Relations", "HRIS", "Payroll Coordination", "Interviewing", "Compliance", "Performance Reviews"],
        "positions": ["HR Generalist", "Talent Acquisition Specialist", "People Operations Associate"],
        "salary": (32000, 90000),
    },
}

COMPANIES = [
    ("CloudRiver Labs", "Technology", "SaaS platform for workflow automation and analytics.", "cloudriverlabs.com"),
    ("Himalaya Digital Bank", "Financial Technology", "Digital banking products for consumers and small businesses.", "himalayadigitalbank.com"),
    ("NexaHealth Systems", "Healthcare Technology", "Clinical operations and patient engagement software.", "nexahealthsystems.com"),
    ("Evergreen Logistics", "Logistics", "Regional freight, warehousing, and last-mile delivery operations.", "evergreenlogistics.com"),
    ("BrightPath Learning", "Education Technology", "Online learning tools for professional certification programs.", "brightpathlearning.com"),
    ("UrbanNest Properties", "Real Estate", "Property management and leasing technology for urban rentals.", "urbannestproperties.com"),
    ("OrbitPay", "Payments", "Cross-border payment infrastructure for growing businesses.", "orbitpay.io"),
    ("Peak Retail Group", "Retail", "Omnichannel retail group with stores and online marketplaces.", "peakretailgroup.com"),
    ("TerraGrid Energy", "Renewable Energy", "Solar and battery projects for commercial facilities.", "terragridenergy.com"),
    ("BluePeak Studio", "Design and Media", "Brand, content, and product design studio.", "bluepeakstudio.com"),
    ("MapleBridge Consulting", "Consulting", "Operations and technology consulting for mid-market companies.", "maplebridgeconsulting.com"),
    ("SwiftServe Hospitality", "Hospitality", "Cloud tools and managed services for hotels and restaurants.", "swiftservehospitality.com"),
]

JOB_TITLES = [
    "Software Engineer", "Frontend Engineer", "Backend Developer", "Data Analyst", "BI Analyst",
    "Product Manager", "Product Designer", "UX Designer", "Digital Marketing Specialist",
    "Finance Analyst", "Operations Coordinator", "HR Generalist", "Talent Acquisition Specialist",
    "Supply Chain Analyst", "QA Engineer", "DevOps Engineer", "Customer Success Manager",
]


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def phone_for(country_code, rng):
    if country_code == "+977":
        return f"+977-98{rng.randint(10000000, 99999999)}"
    return f"{country_code}-{rng.randint(200, 999)}-{rng.randint(200, 999)}-{rng.randint(1000, 9999)}"


def salary_range(min_salary, max_salary, experience_years, rng):
    floor = min_salary + experience_years * rng.randint(1800, 4200)
    ceiling = min(max_salary, floor + rng.randint(12000, 32000))
    return f"${floor:,.0f} - ${ceiling:,.0f}"


def make_seekers(rng):
    seekers = []
    used_emails = set()
    role_names = list(ROLE_PROFILES.keys())
    for idx in range(1, 101):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        location, country_code, country = rng.choice(LOCATIONS)
        target_role = rng.choice(role_names)
        profile = ROLE_PROFILES[target_role]
        years = rng.choices(range(0, 16), weights=[7, 8, 10, 11, 12, 12, 10, 8, 7, 5, 4, 3, 2, 1, 1, 1])[0]
        grad_year = datetime.now().year - max(years, 0) - rng.randint(0, 3)
        current_position = "Recent Graduate" if years == 0 else rng.choice(profile["positions"])
        skill_count = rng.randint(5, min(15, len(profile["skills"])))
        skills = rng.sample(profile["skills"], skill_count)
        degree = rng.choice(DEGREES)
        university = rng.choice(UNIVERSITIES[profile["field"]])
        salary = salary_range(*profile["salary"], years, rng)
        email_base = f"{first}.{last}.{idx:03d}@example.careerswipe.test".lower()
        while email_base in used_emails:
            email_base = f"{first}.{last}.{idx}{rng.randint(10,99)}@example.careerswipe.test".lower()
        used_emails.add(email_base)
        linkedin_slug = slugify(f"{first}-{last}-{target_role}-{idx}")
        has_portfolio = profile["field"] in {"Technology", "Design", "Product", "Marketing"} and rng.random() > 0.25
        portfolio = f"https://{slugify(first + last)}.portfolio.careerswipe.test" if has_portfolio else ""
        summary = (
            f"{current_position} with {years} year{'s' if years != 1 else ''} of experience in "
            f"{profile['field'].lower()}, strongest in {', '.join(skills[:3])}. "
            f"Known for practical execution, clear communication, and shipping measurable improvements."
        )
        seekers.append({
            "full_name": f"{first} {last}",
            "first_name": first,
            "last_name": last,
            "email": email_base,
            "phone_number": phone_for(country_code, rng),
            "location": location,
            "country": country,
            "education": degree,
            "university": university,
            "graduation_year": grad_year,
            "skills": skills,
            "years_of_experience": years,
            "career_field": profile["field"],
            "current_position": current_position,
            "expected_salary": salary,
            "resume_summary": summary,
            "linkedin_url": f"https://www.linkedin.com/in/{linkedin_slug}",
            "portfolio_url": portfolio,
            "preferred_work_mode": rng.choice(["Remote", "Hybrid", "Onsite"]),
            "availability": rng.choice(["Immediate", "2 weeks", "30 days", "60 days"]),
            "work_authorization": rng.choice(["Citizen", "Permanent Resident", "Work Permit", "Requires Sponsorship"]),
        })
    return seekers


def make_companies(rng):
    companies = []
    for idx, (name, industry, description, domain) in enumerate(COMPANIES, start=1):
        city, country_code, country = rng.choice(LOCATIONS)
        companies.append({
            "company_name": name,
            "email": f"careers@{domain}",
            "phone": phone_for(country_code, rng),
            "hr_name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
            "company_address": f"{rng.randint(10, 990)} {rng.choice(['Innovation Road', 'Market Street', 'King Street', 'Tech Park', 'Main Avenue'])}, {city}",
            "headquarters": city,
            "country": country,
            "description": description,
            "industry": industry,
            "company_type": rng.choice(["Private", "Public", "Startup", "Non-profit"]),
            "company_size": rng.choice(["11-50", "51-200", "201-500", "501-1000", "1001-5000"]),
            "founded_year": rng.randint(2004, 2022),
            "website": f"https://{domain}",
            "hiring_frequency": rng.choice(["Monthly", "Quarterly", "Seasonal", "Continuous"]),
            "remote_hiring": rng.choice([True, True, False]),
            "international_hiring": rng.choice([True, False]),
            "preferred_locations": rng.sample([loc[0] for loc in LOCATIONS], rng.randint(2, 5)),
            "hiring_categories": rng.sample(list({v["field"] for v in ROLE_PROFILES.values()}), rng.randint(2, 4)),
            "linkedin_url": f"https://www.linkedin.com/company/{slugify(name)}",
        })
    return companies


def make_jobs(rng, companies):
    jobs = []
    for idx in range(1, 61):
        company = rng.choice(companies)
        base_title = rng.choice(JOB_TITLES)
        profile = ROLE_PROFILES.get(base_title, ROLE_PROFILES[rng.choice(list(ROLE_PROFILES.keys()))])
        min_exp = rng.randint(0, 8)
        required = rng.sample(profile["skills"], rng.randint(4, min(9, len(profile["skills"]))))
        location = rng.choice(company["preferred_locations"])
        job_type = rng.choice(["Full-time", "Full-time", "Contract", "Part-time", "Internship"])
        mode = rng.choice(["Remote", "Hybrid", "Onsite"])
        level = "Entry Level" if min_exp < 2 else "Mid" if min_exp < 5 else "Senior"
        jobs.append({
            "company_name": company["company_name"],
            "title": base_title,
            "description": (
                f"{company['company_name']} is hiring a {base_title} to support production systems, "
                f"cross-functional delivery, and measurable business outcomes. The role suits someone "
                f"comfortable with ownership, documentation, stakeholder updates, and continuous improvement."
            ),
            "required_skills": required,
            "location": location,
            "job_type": job_type,
            "job_location_type": mode,
            "experience_level": level,
            "min_experience": min_exp,
            "experience_required": f"{min_exp}-{min_exp + 2} years",
            "salary": salary_range(*profile["salary"], min_exp, rng),
            "tags": [slugify(base_title), slugify(company["industry"]), slugify(mode), slugify(level)],
            "is_boosted": idx % 7 == 0,
        })
    return jobs


def build_dataset():
    rng = random.Random(SEED)
    companies = make_companies(rng)
    jobs = make_jobs(rng, companies)
    seekers = make_seekers(rng)
    return {
        "metadata": {
            "name": "CareerSwipe realistic demo dataset",
            "seed": SEED,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "counts": {"job_seekers": len(seekers), "companies": len(companies), "jobs": len(jobs)},
            "default_password_for_seeded_accounts": DEFAULT_PASSWORD,
        },
        "job_seekers": seekers,
        "companies": companies,
        "jobs": jobs,
    }


def write_outputs(dataset, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "careerswipe_demo_dataset.json"
    json_path.write_text(json.dumps(dataset, indent=2), encoding="utf-8")

    for key, rows in [
        ("job_seekers", dataset["job_seekers"]),
        ("companies", dataset["companies"]),
        ("jobs", dataset["jobs"]),
    ]:
        csv_path = output_dir / f"{key}.csv"
        fieldnames = list(rows[0].keys())
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: json.dumps(v) if isinstance(v, list) else v for k, v in row.items()})


def seed_database(dataset, replace=False):
    from app import app
    from extensions import db
    from models import Company, JobListing, JobSwipe, Seeker

    with app.app_context():
        if replace:
            JobSwipe.query.delete()
            JobListing.query.delete()
            Seeker.query.delete()
            Company.query.delete()
            db.session.commit()

        password_hash = generate_password_hash(DEFAULT_PASSWORD)
        company_models = {}
        for row in dataset["companies"]:
            existing = Company.query.filter_by(email=row["email"]).first()
            company = existing or Company(email=row["email"], password_hash=password_hash)
            company.company_name = row["company_name"]
            company.phone = row["phone"]
            company.hr_name = row["hr_name"]
            company.company_address = row["company_address"]
            company.headquarters = row["headquarters"]
            company.description = row["description"]
            company.industry = row["industry"]
            company.company_type = row["company_type"]
            company.company_size = row["company_size"]
            company.founded_year = row["founded_year"]
            company.website = row["website"]
            company.hiring_frequency = row["hiring_frequency"]
            company.remote_hiring = row["remote_hiring"]
            company.international_hiring = row["international_hiring"]
            company.preferred_locations = ", ".join(row["preferred_locations"])
            company.hiring_categories = ", ".join(row["hiring_categories"])
            company.linkedin_url = row["linkedin_url"]
            company.country = row["country"]
            company.is_verified = True
            company.age_verified = True
            company.legally_eligible = True
            company.is_published = True
            company.profile_completion = 100
            db.session.add(company)
            company_models[row["company_name"]] = company
        db.session.commit()

        for row in dataset["jobs"]:
            company = company_models[row["company_name"]]
            db.session.add(JobListing(
                company_id=company.id,
                title=row["title"],
                description=row["description"],
                required_skills=", ".join(row["required_skills"]),
                location=row["location"],
                job_type=row["job_type"],
                job_location_type=row["job_location_type"],
                experience_level=row["experience_level"],
                min_experience=row["min_experience"],
                experience_required=row["experience_required"],
                salary=row["salary"],
                tags=", ".join(row["tags"]),
                is_boosted=row["is_boosted"],
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 45)),
            ))

        for row in dataset["job_seekers"]:
            db.session.add(Seeker(
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                password_hash=password_hash,
                phone=row["phone_number"],
                address=row["location"],
                linkedin=row["linkedin_url"],
                portfolio=row["portfolio_url"] or None,
                education=row["education"],
                education_history=f"{row['education']}, {row['university']} ({row['graduation_year']})",
                experience=row["resume_summary"],
                skills=", ".join(row["skills"]),
                experience_type="fresher" if row["years_of_experience"] == 0 else "experienced",
                career_field=row["career_field"],
                job_status=random.choice(["searching", "open to offers", "employed"]),
                job_location_type=row["preferred_work_mode"],
                shift_preference=random.choice(["day", "flexible", "night"]),
                desired_roles=row["current_position"],
                salary_expectation=row["expected_salary"],
                availability=row["availability"],
                is_verified=True,
                age_verified=True,
                legally_eligible=True,
                country=row["country"],
                work_authorization=row["work_authorization"],
                source="demo_dataset",
                profile_completion=100,
                is_published=True,
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 120)),
            ))
        db.session.commit()


def main():
    parser = argparse.ArgumentParser(description="Generate a realistic CareerSwipe demo dataset.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Directory for JSON and CSV exports.")
    parser.add_argument("--seed-db", action="store_true", help="Seed the configured database with generated data.")
    parser.add_argument("--replace", action="store_true", help="Delete existing seekers, companies, jobs, and applications before seeding.")
    args = parser.parse_args()

    dataset = build_dataset()
    write_outputs(dataset, Path(args.output_dir))
    if args.seed_db:
        seed_database(dataset, replace=args.replace)
    print(
        f"Generated {len(dataset['job_seekers'])} seekers, "
        f"{len(dataset['companies'])} companies, and {len(dataset['jobs'])} jobs in {args.output_dir}."
    )


if __name__ == "__main__":
    main()
