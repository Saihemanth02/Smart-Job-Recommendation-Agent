import os
import csv
import random
from pathlib import Path

# Setup paths
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)

# Seed lists
FIRST_NAMES = [
    "Aarav", "Arjun", "Aditya", "Sai", "Krishna", "Rohan", "Vivek", "Rahul", "Neha", "Priya", 
    "Sneha", "Ananya", "Harish", "Sandeep", "Divya", "Manoj", "Rajesh", "Suresh", "Lakshmi", "Kiran",
    "Pranav", "Ishaan", "Riya", "Kavya", "Varun", "Abhishek", "Deepak", "Swati", "Shruti", "Vijay"
]
LAST_NAMES = [
    "Sharma", "Verma", "Rao", "Reddy", "Patel", "Iyer", "Joshi", "Nair", "Gupta", "Kumar", 
    "Choudhury", "Das", "Sen", "Prasad", "Bhat", "Murthy", "Srinivas", "Acharya", "Mehta", "Bose"
]
COLLEGES = [
    "Gayatri Vidya Parishad College of Engineering (GVP), Visakhapatnam",
    "JNTU Hyderabad (JNTUH)",
    "JNTU Kakinada (JNTUK)",
    "JNTU Anantapur (JNTUA)",
    "Vellore Institute of Technology (VIT), Vellore",
    "SRM Institute of Science and Technology, Chennai",
    "IIIT Hyderabad",
    "NIT Warangal",
    "IIT Madras",
    "Andhra University, Visakhapatnam",
    "Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad",
    "GMR Institute of Technology, Rajam"
]
DEGREE_LEVELS = ["B.Tech", "MCA", "M.Tech", "B.Sc", "M.Sc"]

ROLE_DETAILS = {
    "Frontend Developer": {
        "category": "Software Development",
        "skills": ["React", "JavaScript", "HTML", "CSS", "Git", "Tailwind CSS", "Vue.js", "Angular", "TypeScript", "Bootstrap"],
        "projects": [
            "E-commerce dashboard built with React and Tailwind CSS",
            "Real-time chat application using WebSockets and JavaScript",
            "Portfolio website optimized for responsive layouts and SEO"
        ],
        "base_salary": 4.5
    },
    "Java Developer": {
        "category": "Software Development",
        "skills": ["Java", "Spring Boot", "Hibernate", "SQL", "Git", "REST APIs", "Maven", "JUnit", "Docker", "PostgreSQL"],
        "projects": [
            "Online banking application backend using Spring Boot and SQL",
            "Inventory management API with secure JWT authentication",
            "Microservices-based retail gateway integrated with Maven"
        ],
        "base_salary": 4.2
    },
    "DevOps Engineer": {
        "category": "Software Development",
        "skills": ["Docker", "Kubernetes", "AWS", "Jenkins", "Linux", "Git", "Terraform", "Ansible", "Shell Scripting", "Python"],
        "projects": [
            "CI/CD pipeline automation using Jenkins, Docker, and Kubernetes",
            "Infrastructure provisioning on AWS using Terraform files",
            "Server configuration automation with Ansible playbooks"
        ],
        "base_salary": 5.2
    },
    "ML Engineer": {
        "category": "Data & Analytics",
        "skills": ["Python", "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NumPy", "SQL", "Git", "Docker", "Machine Learning"],
        "projects": [
            "Image classification model using CNNs and PyTorch",
            "Customer churn prediction algorithm using Random Forest on Scikit-Learn",
            "Real-time object detection system optimized with TensorFlow Lite"
        ],
        "base_salary": 6.5
    },
    "Data Scientist": {
        "category": "Data & Analytics",
        "skills": ["Python", "SQL", "Machine Learning", "Tableau", "Statistics", "Pandas", "NumPy", "Deep Learning", "Git", "PowerBI"],
        "projects": [
            "A/B testing analysis platform for dynamic pricing strategies",
            "Sales forecasting model using Time Series Analysis and Pandas",
            "Interactive executive dashboard using Tableau and custom SQL scripts"
        ],
        "base_salary": 6.0
    },
    "Business Analyst": {
        "category": "Data & Analytics",
        "skills": ["SQL", "Excel", "Tableau", "PowerBI", "Agile", "Scrum", "Jira", "Communication", "Python", "Requirements Gathering"],
        "projects": [
            "Market research study mapping product demand in Tier-2 Indian cities",
            "Business requirements document (BRD) for automated retail workflow",
            "Visualizing KPI trends using PowerBI and Excel pivot tables"
        ],
        "base_salary": 4.0
    },
    "UX Designer": {
        "category": "Design",
        "skills": ["Figma", "Adobe XD", "Wireframing", "Prototyping", "HTML", "CSS", "User Research", "Interaction Design", "Illustrator", "Photoshop"],
        "projects": [
            "Mobile banking app redesign focus group and high-fidelity prototype",
            "Wireframing and user testing flows for a local delivery platform",
            "Interactive landing page designs optimized with Figma design tokens"
        ],
        "base_salary": 4.5
    },
    "Marketing Executive": {
        "category": "Marketing",
        "skills": ["SEO", "SEM", "Social Media Marketing", "Content Writing", "Google Analytics", "Excel", "Email Marketing", "Communication", "Copywriting", "Photoshop"],
        "projects": [
            "Organic traffic growth strategy yielding 40% user increase via SEO",
            "Paid search campaign management using Google Ads and SEM tools",
            "Social media branding plan for an early-stage Indian startup"
        ],
        "base_salary": 3.8
    },
    "Mechanical Design Engineer": {
        "category": "Core/Mechanical",
        "skills": ["AutoCAD", "SolidWorks", "CATIA", "Fusion 360", "ANSYS", "GD&T", "Thermodynamics", "FEA", "Materials Science", "Excel"],
        "projects": [
            "Structural analysis of automotive chassis parts using ANSYS FEA",
            "3D mechanical CAD drafting of planetary gear assemblies",
            "Thermal performance analysis of custom radiator tubes"
        ],
        "base_salary": 4.0
    },
    "Systems Analyst": {
        "category": "Business/Ops",
        "skills": ["SQL", "UML", "Systems Design", "Agile", "Business Analysis", "Git", "Java", "Python", "Excel", "Jira"],
        "projects": [
            "Systems architecture diagramming using UML class/sequence panels",
            "Migrating manual database records to structured cloud database systems",
            "Feasibility studies for enterprise software deployment plans"
        ],
        "base_salary": 4.5
    }
}

CERTIFICATIONS_POOL = [
    "AWS Certified Solutions Architect", "Scrum Alliance Certified ScrumMaster", "Oracle Certified Associate Java SE",
    "Google Professional Data Engineer", "TensorFlow Developer Certificate", "Tableau Desktop Specialist",
    "Google Analytics Individual Qualification", "Certified SolidWorks Associate (CSWA)", "Microsoft Certified: Azure Fundamentals"
]

CITIES_BY_TIER = {
    1: ["Bangalore", "Hyderabad", "Mumbai", "Pune", "Chennai", "Delhi NCR"],
    2: ["Visakhapatnam", "Coimbatore", "Kochi", "Jaipur", "Lucknow", "Ahmedabad"],
    3: ["Vijayawada", "Nellore", "Kakinada", "Warangal", "Udaipur", "Nashik"]
}

def generate_resume_text(name, degree, college, role, skills, projects, certifications, exp_years):
    skills_str = ", ".join(skills)
    projects_str = ". ".join(projects)
    certs_str = ", ".join(certifications)
    exp_str = f"Fresher with academic experience." if exp_years == 0 else f"Professional with {exp_years} years of experience as {role}."
    
    resume_body = (
        f"Resume of {name}\n"
        f"Education: {degree} from {college}.\n"
        f"Target Role: {role}\n"
        f"Experience: {exp_str} Worked on designing, implementing, and optimizing solutions.\n"
        f"Projects: {projects_str}.\n"
        f"Certifications: {certs_str}.\n"
        f"Key Skills: {skills_str}.\n"
    )
    return resume_body

def generate_resumes_dataset(n_rows=800):
    rows = []
    for _ in range(n_rows):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        phone = f"+91-{random.randint(70000, 99999)}-{random.randint(10000, 99999)}"
        
        college = random.choice(COLLEGES)
        degree = random.choice(DEGREE_LEVELS)
        exp_years = random.choices([0, 1, 2, 3], weights=[0.5, 0.25, 0.15, 0.10])[0]
        
        role = random.choice(list(ROLE_DETAILS.keys()))
        details = ROLE_DETAILS[role]
        category = details["category"]
        
        # Sample subset of skills to introduce variability
        candidate_skills = random.sample(details["skills"], random.randint(5, len(details["skills"])))
        # Occasional cross-domain skills (e.g. communication or Git)
        if random.random() > 0.4:
            candidate_skills.append("Communication")
        if random.random() > 0.4:
            candidate_skills.append("Git")
            
        candidate_projects = random.sample(details["projects"], random.randint(1, len(details["projects"])))
        num_certs = random.choices([0, 1, 2], weights=[0.4, 0.4, 0.2])[0]
        candidate_certs = random.sample(CERTIFICATIONS_POOL, num_certs) if num_certs > 0 else []
        
        resume_text = generate_resume_text(
            name, degree, college, role, candidate_skills, candidate_projects, candidate_certs, exp_years
        )
        
        rows.append({
            "name": name,
            "email": email,
            "phone": phone,
            "education_level": degree,
            "college": college,
            "experience_years": exp_years,
            "num_skills": len(candidate_skills),
            "num_certifications": num_certs,
            "skills": ", ".join(candidate_skills),
            "resume_text": resume_text,
            "job_category": category,
            "job_role": role
        })
        
    # Write to CSV
    csv_path = DATA_DIR / "resumes_seed.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {n_rows} resumes inside {csv_path}")

def generate_salary_dataset(n_rows=1000):
    rows = []
    for _ in range(n_rows):
        role = random.choice(list(ROLE_DETAILS.keys()))
        details = ROLE_DETAILS[role]
        
        exp_years = random.choices([0, 1, 2, 3], weights=[0.5, 0.25, 0.15, 0.10])[0]
        location_tier = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
        num_skills = random.randint(4, 12)
        edu_level = random.choice(DEGREE_LEVELS)
        num_certs = random.choices([0, 1, 2], weights=[0.5, 0.4, 0.1])[0]
        
        # Calculate a realistic base salary
        base = details["base_salary"]
        
        # Add multipliers for experience, location tier, skills, certifications, and education
        exp_bonus = exp_years * 1.5  # +1.5L per year of experience
        loc_bonus = {1: 1.0, 2: 0.0, 3: -0.6}[location_tier]  # Tier 1 gets +1L, Tier 3 gets -0.6L
        skills_bonus = (num_skills - 6) * 0.15  # 0.15L per skill above/below 6
        certs_bonus = num_certs * 0.4  # 0.4L per certificate
        
        edu_map = {"B.Sc": 0.0, "B.Tech": 0.5, "MCA": 0.4, "M.Tech": 0.8, "M.Sc": 0.2}
        edu_bonus = edu_map.get(edu_level, 0.0)
        
        # Random market fluctuation (-10% to +15%)
        noise = random.uniform(-0.1, 0.15)
        
        salary_lpa = (base + exp_bonus + loc_bonus + skills_bonus + certs_bonus + edu_bonus) * (1 + noise)
        salary_lpa = max(2.8, round(salary_lpa, 2))  # Floor of 2.8 LPA for freshers
        
        rows.append({
            "job_role": role,
            "years_experience": exp_years,
            "location_tier": location_tier,
            "num_skills": num_skills,
            "education_level": edu_level,
            "num_certifications": num_certs,
            "salary": salary_lpa
        })
        
    csv_path = DATA_DIR / "salary_seed.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {n_rows} salary records inside {csv_path}")

def generate_skills_taxonomy():
    # Save a skills taxonomy file
    taxonomy_rows = []
    for role, details in ROLE_DETAILS.items():
        category = details["category"]
        for skill in details["skills"]:
            # Classify type
            if skill in ["React", "Vue.js", "Angular", "Docker", "Kubernetes", "Git", "Terraform", "Ansible", "Jenkins", "Tableau", "PowerBI", "Figma", "Adobe XD", "SolidWorks", "AutoCAD", "CATIA", "ANSYS", "Jira"]:
                skill_type = "tools"
            elif skill in ["Communication", "Leadership", "Teamwork", "Problem Solving", "Copywriting", "Content Writing"]:
                skill_type = "soft"
            elif skill in ["Agile", "Scrum", "Requirements Gathering", "GD&T", "FEA", "SEO", "SEM", "Systems Design"]:
                skill_type = "domain"
            else:
                skill_type = "technical"
            taxonomy_rows.append({"skill": skill, "category": skill_type})
            
    # Add a few extras
    extra_skills = [
        {"skill": "Communication", "category": "soft"},
        {"skill": "Leadership", "category": "soft"},
        {"skill": "Teamwork", "category": "soft"},
        {"skill": "Problem Solving", "category": "soft"},
        {"skill": "Python", "category": "technical"},
        {"skill": "SQL", "category": "technical"}
    ]
    for s in extra_skills:
        if s not in taxonomy_rows:
            taxonomy_rows.append(s)
            
    tax_path = Path(__file__).resolve().parent.parent / "ml" / "skills_taxonomy.csv"
    with open(tax_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["skill", "category"])
        writer.writeheader()
        writer.writerows(taxonomy_rows)
    print(f"Generated skills taxonomy at {tax_path}")

if __name__ == "__main__":
    generate_resumes_dataset()
    generate_salary_dataset()
    generate_skills_taxonomy()
