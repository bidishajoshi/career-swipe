import re
import os
import subprocess
import uuid
import pdfplumber
from docx import Document

# Core skills list for matching (Expanded)
SKILLS_LIST = [
    "python", "java", "sql", "html", "css", "javascript", "react", "flask", "django", "node", "aws",
    "c++", "c#", "php", "ruby", "swift", "kotlin", "go", "rust", "typescript", "angular", "vue",
    "mongodb", "postgresql", "mysql", "docker", "kubernetes", "git", "linux", "machine learning",
    "data science", "nlp", "cloud computing", "azure", "gcp", "tableau", "power bi", "excel",
    "communication", "leadership", "project management", "agile", "scrum", "devops", "testing"
]

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file using pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def extract_text_from_docx(docx_path):
    """Extracts text from a .docx file using python-docx."""
    try:
        doc = Document(docx_path)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Word extraction error: {e}")
        return ""

def convert_to_pdf(input_path, output_folder):
    """Converts .doc or .docx to .pdf using LibreOffice headless."""
    try:
        subprocess.run([
            'soffice', 
            '--headless', 
            '--convert-to', 'pdf', 
            '--outdir', output_folder, 
            input_path
        ], check=True, capture_output=True)
        
        base_name = os.path.basename(input_path).rsplit('.', 1)[0]
        pdf_path = os.path.join(output_folder, f"{base_name}.pdf")
        return pdf_path if os.path.exists(pdf_path) else None
    except Exception as e:
        print(f"Conversion error: {e}")
        return None

def process_resume(filepath, upload_folder):
    """Main function to handle resume processing."""
    if not os.path.exists(filepath):
        return None

    ext = filepath.rsplit('.', 1)[-1].lower()
    text = ""
    pdf_path = None

    # Step 1: Extract Text
    if ext == 'docx':
        text = extract_text_from_docx(filepath)
        pdf_path = convert_to_pdf(filepath, upload_folder)
    elif ext == 'doc':
        pdf_path = convert_to_pdf(filepath, upload_folder)
        if pdf_path:
            text = extract_text_from_pdf(pdf_path)
    elif ext == 'pdf':
        text = extract_text_from_pdf(filepath)
        pdf_path = filepath

    print("RAW TEXT:", text[:500] + "..." if text else "EMPTY")
    print("TEXT LENGTH:", len(text))

    # Handle Empty Extraction (Scanned PDF)
    if not text.strip():
        print("EXTRACTION FAILED: Scanned or empty file.")
        return {
            "first_name": "Unknown",
            "last_name": "Candidate",
            "email": "",
            "skills": "",
            "resume_path": pdf_path or filepath
        }

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    
    # Step 2: Extract Name (Improved)
    ignore_keywords = ["curriculum", "vitae", "resume", "page", "profile", "contact", "summary", "experience", "education", "skills", "objective"]
    full_name = "Unknown Candidate"
    
    for line in lines[:20]: # Look in first 20 non-empty lines
        clean_line = line.strip()
        
        # Skip if line is too long or too short
        word_count = len(clean_line.split())
        if word_count > 5 or word_count < 1:
            continue
            
        # Skip if it contains ignore keywords or numbers (like phone/address)
        if any(kw in clean_line.lower() for kw in ignore_keywords) or any(char.isdigit() for char in clean_line):
            continue
            
        # Check if it looks like a name (Capitalized words)
        words = clean_line.split()
        if all(w[0].isupper() or (len(w) > 1 and w[1] == '.') for w in words if any(c.isalpha() for c in w)):
            # Final check: shouldn't be all caps usually (some resumes do it, but let's be careful)
            if clean_line.isupper() and word_count == 1:
                continue
            
            # Strip common labels
            name_to_clean = clean_line
            for label in ["Name:", "Full Name:", "Candidate Name:"]:
                if name_to_clean.lower().startswith(label.lower()):
                    name_to_clean = name_to_clean[len(label):].strip()
            
            full_name = name_to_clean
            break
            
    print("NAME FOUND:", full_name)

    # Step 3: Extract Email
    email_match = re.search(r'[\w.-]+@[\w.-]+', text)
    email = email_match.group(0) if email_match else ""
    print("EMAIL:", email)

    # Step 4: Extract Phone
    phone_regex = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,13}'
    phone_match = re.search(phone_regex, text)
    phone = phone_match.group(0) if phone_match else ""
    print("PHONE:", phone)

    # Step 5: Extract Address (Heuristic)
    address = ""
    addr_keywords = [
        'Street', 'St.', 'Lane', 'Ln', 'Road', 'Rd', 'Avenue', 'Ave', 'Drive', 'Dr', 'Boulevard', 'Blvd', 'Postal', 'Zip',
        'Kathmandu', 'Nepal', 'Lalitpur', 'Bhaktapur', 'Pokhara', 'City', 'District'
    ]
    for line in lines[:25]: # Look a bit deeper
        if any(kw in line for kw in addr_keywords) or re.search(r'\d{5,6}', line):
            address = line
            break
    print("ADDRESS:", address)

    # Step 6: Extract Gender (Heuristic)
    gender = "Other"
    male_keywords = ["mr.", "he/him", "male"]
    female_keywords = ["ms.", "mrs.", "she/her", "female"]
    text_lower = text.lower()
    if any(kw in text_lower for kw in female_keywords):
        gender = "Female"
    elif any(kw in text_lower for kw in male_keywords):
        gender = "Male"
    print("GENDER:", gender)

    # Step 7: Extract Date of Birth
    dob = ""
    dob_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{1,2},?\s\d{4})', text, re.IGNORECASE)
    if dob_match:
        dob = dob_match.group(0)
    print("DOB:", dob)

    # Step 8: Section-based Extraction (Education & Experience)
    sections = {
        "education": ["education", "academic", "qualifications", "schooling"],
        "experience": ["experience", "work history", "employment", "professional background", "projects"],
        "skills": ["skills", "technical skills", "competencies", "expertise"]
    }
    
    extracted_sections = {"education": [], "experience": [], "skills_section": []}
    current_section = None
    
    for line in lines:
        line_lower = line.lower()
        is_header = False
        for sec, keywords in sections.items():
            if any(kw == line_lower.strip(':') for kw in keywords) or (len(line_lower) < 20 and any(kw in line_lower for kw in keywords)):
                current_section = sec
                is_header = True
                break
        
        if not is_header and current_section:
            if current_section == "skills":
                extracted_sections["skills_section"].append(line)
            else:
                extracted_sections[current_section].append(line)

    education = "\n".join(extracted_sections["education"][:5]) # Take first 5 lines of education
    experience = "\n".join(extracted_sections["experience"][:10]) # Take first 10 lines of experience
    
    # Step 9: Extract Skills (List-based + Section-based)
    found_skills = [s.capitalize() for s in SKILLS_LIST if s in text.lower()]
    # Also add skills found in the skills section if they aren't in our list
    if extracted_sections["skills_section"]:
        section_skills = ", ".join(extracted_sections["skills_section"])
        # Simple split by comma or newline for section skills
        additional_skills = [s.strip() for s in re.split(r'[,|\n]', section_skills) if s.strip()]
        for s in additional_skills[:10]:
            if s.capitalize() not in found_skills and len(s) < 30:
                found_skills.append(s.capitalize())
                
    skills_str = ", ".join(found_skills)
    print("SKILLS:", skills_str)

    # Step 10: Experience Type (Heuristic)
    experience_type = "Full-time"
    if "intern" in text_lower:
        experience_type = "Internship"
    elif "freelance" in text_lower:
        experience_type = "Freelance"
    elif not experience.strip():
        experience_type = "No Experience"
    print("EXP TYPE:", experience_type)

    # Step 11: Career Field (Heuristic)
    career_field = "Other"
    field_keywords = {
        "IT / Software": ["python", "java", "software", "developer", "engineer", "it", "coding", "programming"],
        "Marketing / Sales": ["marketing", "sales", "brand", "advertising", "seo"],
        "Finance / Accounting": ["finance", "accounting", "bank", "audit", "tax"],
        "Healthcare / Medical": ["nurse", "doctor", "medical", "health", "hospital"],
        "Education / Teaching": ["teacher", "professor", "tutor", "education", "school"],
        "Design / Creative": ["design", "graphic", "creative", "ui", "ux", "artist"]
    }
    for field, kws in field_keywords.items():
        if any(kw in text_lower for kw in kws):
            career_field = field
            break
    print("CAREER FIELD:", career_field)

    # Step 12: Job Location Type
    job_location_type = "Local"
    if "remote" in text_lower:
        job_location_type = "Remote"
    elif "anywhere" in text_lower or "relocate" in text_lower:
        job_location_type = "Anywhere"
    print("LOCATION PREF:", job_location_type)

    # Split name for DB fields
    name_parts = full_name.split()
    first_name = name_parts[0] if len(name_parts) > 0 else "Unknown"
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "Candidate"

    return {
        "name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "address": address,
        "gender": gender,
        "dob": dob,
        "education": education,
        "experience": experience,
        "experience_type": experience_type,
        "career_field": career_field,
        "job_location_type": job_location_type,
        "skills": skills_str,
        "resume_path": pdf_path or filepath
    }

