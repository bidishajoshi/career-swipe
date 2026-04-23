import re
import os
import subprocess
import uuid
import pdfplumber
from docx import Document

# A comprehensive list of skills to search for across various industries
SKILLS_DB = [
    # --- TECH & IT ---
    "Python", "Java", "JavaScript", "C++", "C#", "PHP", "Ruby", "Swift", "Kotlin", "Go", "Rust",
    "HTML", "CSS", "SQL", "NoSQL", "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask",
    "Spring", "Hibernate", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "DevOps", "CI/CD",
    "Machine Learning", "Data Analysis", "AI", "NLP", "Deep Learning", "TensorFlow", "PyTorch",
    "Excel", "Tableau", "Power BI", "Agile", "Scrum", "UI/UX", "Figma", "Git", "GitHub", "Linux",
    "Cybersecurity", "Blockchain", "TypeScript", "GraphQL", "PostgreSQL", "MongoDB", "Flutter",

    # --- BUSINESS & MANAGEMENT ---
    "Project Management", "Business Analysis", "Operations Management", "Strategic Planning",
    "Team Leadership", "Risk Management", "Business Development", "Stakeholder Management",
    "Budgeting", "Contract Negotiation", "Agile Methodologies", "Change Management",

    # --- FINANCE & ACCOUNTING ---
    "Accounting", "Financial Analysis", "Financial Reporting", "Auditing", "Taxation",
    "QuickBooks", "SAP", "Banking", "Investment Management", "Payroll", "Economic Research",

    # --- SALES & MARKETING ---
    "Sales", "Marketing", "Digital Marketing", "SEO", "SEM", "Content Writing", "Copywriting",
    "Social Media Marketing", "Email Marketing", "Market Research", "Public Relations",
    "CRM", "Salesforce", "Branding", "Direct Sales", "Account Management",

    # --- HEALTHCARE & MEDICAL ---
    "Nursing", "Patient Care", "Medical Terminology", "Clinical Research", "Pharmacology",
    "Diagnostics", "Healthcare Administration", "First Aid", "CPR", "Mental Health",
    "Emergency Medicine", "Pediatrics", "Surgery",

    # --- EDUCATION & TEACHING ---
    "Teaching", "Curriculum Development", "Classroom Management", "Lesson Planning",
    "Special Education", "Tutoring", "Early Childhood Education", "Academic Research",

    # --- HOSPITALITY & TOURISM ---
    "Customer Service", "Hospitality Management", "Event Planning", "Guest Relations",
    "Travel Coordination", "Catering", "Front Office", "Tourism Management",

    # --- ADMINISTRATIVE & OFFICE ---
    "Administrative Support", "Office Management", "Data Entry", "Scheduling",
    "Document Management", "Microsoft Office", "Outlook", "Communication Skills",

    # --- LEGAL & COMPLIANCE ---
    "Legal Research", "Legal Drafting", "Litigation Support", "Compliance", "Contract Law",
    "Intellectual Property", "Paralegal Studies",

    # --- LOGISTICS & SUPPLY CHAIN ---
    "Logistics", "Supply Chain Management", "Inventory Management", "Warehouse Operations",
    "Procurement", "Distribution", "Shipping & Receiving",

    # --- SOFT SKILLS ---
    "Problem Solving", "Critical Thinking", "Time Management", "Adaptability",
    "Leadership", "Teamwork", "Conflict Resolution", "Interpersonal Skills"
]

def convert_to_pdf(input_path, output_folder):
    """Converts .doc or .docx to .pdf using LibreOffice headless."""
    try:
        # LibreOffice command: soffice --headless --convert-to pdf --outdir output_folder input_path
        subprocess.run([
            'soffice', 
            '--headless', 
            '--convert-to', 'pdf', 
            '--outdir', output_folder, 
            input_path
        ], check=True, capture_output=True)
        
        # The output file will have the same basename but .pdf extension
        base_name = os.path.basename(input_path).rsplit('.', 1)[0]
        pdf_path = os.path.join(output_folder, f"{base_name}.pdf")
        
        if os.path.exists(pdf_path):
            return pdf_path
        return None
    except Exception as e:
        print(f"Conversion error: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return text

def extract_email(text):
    """Extracts email using regex."""
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_regex, text)
    return match.group(0) if match else ""

def extract_name(text):
    """Robust heuristic to extract name, skipping common headers."""
    # Common headers to ignore
    ignore_list = [
        "curriculum vitae", "resume", "cv", "name:", "bio", 
        "summary", "profile", "contact", "experience"
    ]
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines[:10]: # Look in first 10 non-empty lines
        clean_line = line.lower()
        # Skip lines that are just headers or common noise
        if any(header in clean_line for header in ignore_list):
            continue
        # Skip lines that look like contact info
        if "@" in line or any(char.isdigit() for char in line) and "+" in line:
            continue
        
        # Assume first substantial line (2-4 words) that isn't a header is the name
        words = line.split()
        if 2 <= len(words) <= 4:
            return line
            
    return ""

def extract_skills(text):
    """Extracts skills based on keyword matching."""
    found_skills = []
    text_lower = text.lower()
    for skill in SKILLS_DB:
        # Use word boundaries to avoid matching sub-words (e.g., 'C' in 'Cloud')
        if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
            found_skills.append(skill)
    return ", ".join(found_skills)

def extract_text_from_word(word_path):
    """Extracts text from a .docx file using python-docx."""
    try:
        doc = Document(word_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Word extraction error: {e}")
        return ""

def process_resume(filepath, upload_folder):
    """Main function to handle resume processing."""
    ext = filepath.rsplit('.', 1)[-1].lower()
    temp_pdf_path = None
    text = ""

    if ext in ['doc', 'docx']:
        # Extract text directly from docx if possible (better results)
        if ext == 'docx':
            text = extract_text_from_word(filepath)
        
        # Still convert to PDF as requested for storage
        temp_pdf_path = convert_to_pdf(filepath, upload_folder)
        
        # If text extraction from docx failed or it's .doc, try PDF extraction
        if not text and temp_pdf_path:
            text = extract_text_from_pdf(temp_pdf_path)
    elif ext == 'pdf':
        temp_pdf_path = filepath
        text = extract_text_from_pdf(temp_pdf_path)
    
    if not text:
        return None

    name = extract_name(text)
    email = extract_email(text)
    skills = extract_skills(text)

    # Split name into first and last
    name_parts = name.split()
    first_name = name_parts[0] if len(name_parts) > 0 else ""
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    print(f"DEBUG: Scanned Resume. Name: {name}, Email: {email}, Skills Count: {len(skills.split(',')) if skills else 0}", flush=True)

    result = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "skills": skills,
        "resume_path": temp_pdf_path
    }

    return result
