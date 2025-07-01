from app import app
from models import db, Department, UserType, JobTitle, Employee, PerformanceReview
from datetime import datetime


with app.app_context():
    print("Seeding manually...")

    # Clear existing data to ensure a clean slate
    PerformanceReview.query.delete()
    Employee.query.delete()
    Department.query.delete()
    UserType.query.delete()
    JobTitle.query.delete()
    db.session.commit()

    # User types
    manager_type = UserType(name="Manager", description="Oversees department")
    employee_type = UserType(name="Employee", description="General staff")
    hr_type = UserType(name="HR", description="Manages human resources")
    db.session.add_all([manager_type, employee_type, hr_type])
    db.session.commit()

    # Job titles - Expanded for more variety within departments
    titles_data = {
        "Engineering Manager": "Engineering Manager",
        "Software Engineer": "Software Engineer",
        "QA Engineer": "QA Engineer",
        "DevOps Engineer": "DevOps Engineer",
        "Product Manager": "Product Manager",

        "Marketing Manager": "Marketing Manager",
        "Marketing Specialist": "Marketing Specialist",
        "Content Creator": "Content Creator",
        "SEO Analyst": "SEO Analyst",
        "Social Media Coordinator": "Social Media Coordinator",

        "HR Officer": "HR Officer", # Manager for HR department
        "HR Assistant": "HR Assistant",
        "Recruitment Specialist": "Recruitment Specialist",
        "Payroll Administrator": "Payroll Administrator",

        "Finance Manager": "Finance Manager",
        "Accountant": "Accountant",
        "Financial Analyst": "Financial Analyst",
        "Auditor": "Auditor",

        "Support Manager": "Support Manager",
        "Support Agent": "Support Agent",
        "Customer Success Rep": "Customer Success Rep",
        "Technical Support": "Technical Support",
    }
    # Create JobTitle objects and store them in a dictionary for easy lookup by their key
    titles = {}
    for key, title_name in titles_data.items():
        job_title_obj = JobTitle(title=title_name)
        db.session.add(job_title_obj)
        titles[key] = job_title_obj
    db.session.commit()


    # Departments
    departments = {
        "Engineering": Department(name="Engineering", description="Builds software"),
        "Marketing": Department(name="Marketing", description="Promotes products"),
        "HR": Department(name="HR", description="Manages people"),
        "Finance": Department(name="Finance", description="Handles money"),
        "Support": Department(name="Support", description="Helps customers"),
    }
    db.session.add_all(departments.values())
    db.session.commit()

    # Unique phone number generator
    # Starting with a base number and incrementing for each new employee
    phone_counter = 700000000

    # Define the structure of departments, managers, and employees with their specific job title keys
    structure = {
        "Engineering": {
            "manager": {"first": "Alice", "last": "Ngugi", "email": "alice.ngugi@company.com", "job_title_key": "Engineering Manager"},
            "employees": [
                {"first": "Brian", "last": "Mutua", "email": "brian.mutua@company.com", "job_title_keys": ["Software Engineer", "QA Engineer", "DevOps Engineer"]},
                {"first": "Carol", "last": "Wambui", "email": "carol.wambui@company.com", "job_title_keys": ["QA Engineer", "Software Engineer", "Product Manager"]},
                {"first": "David", "last": "Otieno", "email": "david.otieno@company.com", "job_title_keys": ["DevOps Engineer", "Software Engineer", "QA Engineer"]},
            ],
        },
        "Marketing": {
            "manager": {"first": "Grace", "last": "Kariuki", "email": "grace.kariuki@company.com", "job_title_key": "Marketing Manager"},
            "employees": [
                {"first": "Helen", "last": "Njeri", "email": "helen.njeri@company.com", "job_title_keys": ["Marketing Specialist", "Content Creator", "SEO Analyst"]},
                {"first": "Ian", "last": "Kimani", "email": "ian.kimani@company.com", "job_title_keys": ["Content Creator", "Social Media Coordinator", "Marketing Specialist"]},
                {"first": "Joy", "last": "Mwangi", "email": "joy.mwangi@company.com", "job_title_keys": ["SEO Analyst", "Marketing Specialist", "Content Creator"]},
            ],
        },
        "HR": {
            "manager": {"first": "Faith", "last": "Mugo", "email": "faith.mugo@company.com", "job_title_key": "HR Officer"},
            "employees": [
                {"first": "Kevin", "last": "Odhiambo", "email": "kevin.odhiambo@company.com", "job_title_keys": ["HR Assistant", "Recruitment Specialist", "Payroll Administrator"]},
                {"first": "Linda", "last": "Omondi", "email": "linda.omondi@company.com", "job_title_keys": ["Recruitment Specialist", "HR Assistant", "Recruitment Specialist"]},
                {"first": "Martin", "last": "Chege", "email": "martin.chege@company.com", "job_title_keys": ["Payroll Administrator", "HR Assistant", "Recruitment Specialist"]},
            ],
        },
        "Finance": {
            "manager": {"first": "Peter", "last": "Koech", "email": "peter.koech@company.com", "job_title_key": "Finance Manager"},
            "employees": [
                {"first": "Nancy", "last": "Muthoni", "email": "nancy.muthoni@company.com", "job_title_keys": ["Accountant", "Financial Analyst", "Auditor"]},
                {"first": "Oscar", "last": "Ochieng", "email": "oscar.ochieng@company.com", "job_title_keys": ["Financial Analyst", "Accountant", "Financial Analyst"]},
                {"first": "Paula", "last": "Nyambura", "email": "paula.nyambura@company.com", "job_title_keys": ["Auditor", "Accountant", "Financial Analyst"]},
            ],
        },
        "Support": {
            "manager": {"first": "Quincy", "last": "Njiru", "email": "quincy.njiru@company.com", "job_title_key": "Support Manager"},
            "employees": [
                {"first": "Rachel", "last": "Wafula", "email": "rachel.wafula@company.com", "job_title_keys": ["Support Agent", "Customer Success Rep", "Technical Support"]},
                {"first": "Steve", "last": "Musyoka", "email": "steve.musyoka@company.com", "job_title_keys": ["Customer Success Rep", "Support Agent", "Customer Success Rep"]},
                {"first": "Tina", "last": "Kiplagat", "email": "tina.kiplagat@company.com", "job_title_keys": ["Technical Support", "Support Agent", "Customer Success Rep"]},
            ],
        },
    }

    for dept_name, team in structure.items():
        dept = departments[dept_name]

        # Manager creation
        m_data = team["manager"]
        current_manager_job_title = titles[m_data["job_title_key"]] # Get the specific job title for the manager
        user_role_for_manager = hr_type if dept_name == "HR" else manager_type # Assign HR user type to HR manager

        manager = Employee(
            first_name=m_data["first"],
            last_name=m_data["last"],
            email=m_data["email"],
            phone=f"07{phone_counter:08d}", # Assign unique phone number
            department=dept,
            user_type=user_role_for_manager,
            job_title=current_manager_job_title,
        )
        manager.set_password("password123")
        db.session.add(manager)
        db.session.commit()
        phone_counter += 1 # Increment phone counter for the next employee

        # Employee creation + Reviews
        job_title_index = 0 # Used to cycle through the job titles for employees within a department
        for emp_data in team["employees"]:
            # Get specific job title for employee, cycling through the list of job_title_keys
            emp_job_title_key = emp_data["job_title_keys"][job_title_index % len(emp_data["job_title_keys"])]
            emp_job_title = titles[emp_job_title_key]

            emp = Employee(
                first_name=emp_data["first"],
                last_name=emp_data["last"],
                email=emp_data["email"],
                phone=f"07{phone_counter:08d}", # Assign unique phone number
                department=dept,
                user_type=employee_type, # All non-managers are 'Employee' user type by default
                job_title=emp_job_title,
            )
            emp.set_password("password123")
            db.session.add(emp)
            db.session.commit()
            phone_counter += 1 # Increment phone counter for the next employee
            job_title_index += 1 # Move to the next job title for cycling

            # Add 3 performance reviews for each employee
            for y in [2022, 2023, 2024]:
                review = PerformanceReview(
                    employee=emp,
                    reviewer=f"{m_data['first']} {m_data['last']}", # Reviewer is the manager of their department
                    notes=f"Performance review for {y}. Doing well overall.",
                    rating=4 if y != 2023 else 5, # Example: higher rating in 2023
                    review_date=datetime(y, 5, 20),
                )
                db.session.add(review)

    db.session.commit()
    print("✅ Manual seed complete.")

