from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
import re

# ===========================
# DB Setup with Convention
# ===========================
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

# ===========================
# Department
# ===========================
class Department(db.Model, SerializerMixin):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(225))

    employees = db.relationship('Employee', back_populates='department', cascade='all, delete-orphan')


    @property
    def manager_name(self):
        manager = next((emp for emp in self.employees if emp.user_type_name == "Manager"), None)
        if manager:
            return f"{manager.first_name} {manager.last_name}"
        return "N/A"

    serialize_only = (
        "id",
        "name",
        "description",
        "manager_name" 
    )

    serialize_rules = ("-employees.department",)

# ===========================
# User Type (Manager, Employee, HR, etc.)
# ===========================
class UserType(db.Model, SerializerMixin):
    __tablename__ = 'user_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(225))

    employees = db.relationship('Employee', back_populates='user_type')

    serialize_rules = ("-employees.user_type",)

# ===========================
# Job Title (Backend Engineer, HR Assistant, etc.)
# ===========================
class JobTitle(db.Model, SerializerMixin):
    __tablename__ = 'job_titles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)

    employees = db.relationship('Employee', back_populates='job_title')

    serialize_rules = ("-employees.job_title",)

# ===========================
# Employee
# ===========================
class Employee(db.Model, SerializerMixin):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(100), unique = True)
    hire_date = db.Column(db.DateTime, default=datetime.now)

    password_hash = db.Column(db.String(128), nullable=False)

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    user_type_id = db.Column(db.Integer, db.ForeignKey('user_types.id'))
    job_title_id = db.Column(db.Integer, db.ForeignKey('job_titles.id'))

    department = db.relationship('Department', back_populates='employees')
    user_type = db.relationship('UserType', back_populates='employees')
    job_title = db.relationship('JobTitle', back_populates='employees')

    attendances = db.relationship('Attendance', back_populates='employee', cascade='all, delete-orphan')
    reviews = db.relationship('PerformanceReview', back_populates='employee', cascade='all, delete-orphan')

    department_name = association_proxy('department', 'name')
    user_type_name = association_proxy('user_type', 'name')
    job_title_name = association_proxy('job_title', 'title')

    serialize_only = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "user_type_name",
        "job_title_name",
         "department_name" 
    )

    serialize_rules = (
        "-password_hash",
        "-department.employees",
        "-user_type.employees",
        "-job_title.employees",
        "-attendances.employee",
        "-reviews.employee"
    )

    def set_password(self, raw_password):
        from flask_bcrypt import generate_password_hash
        self.password_hash = generate_password_hash(raw_password).decode('utf-8')

    def verify_password(self, raw_password):
        from flask_bcrypt import check_password_hash
        return check_password_hash(self.password_hash, raw_password)

    @validates("email")
    def validate_email(self, key, value):
        normalized = value.strip().lower()
        regex = r"[A-Za-z][A-Za-z0-9_.]*@[A-Za-z0-9]+\.[a-z]{2,}"
        if not re.match(regex, normalized):
            raise ValueError("Invalid email format")
        return normalized

# ===========================
# Attendance
# ===========================
class Attendance(db.Model, SerializerMixin):
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.Time)
    check_out_time = db.Column(db.Time)

    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    employee = db.relationship('Employee', back_populates='attendances')

    serialize_rules = ("-employee.attendances",)

# ===========================
# Performance Review
# ===========================
class PerformanceReview(db.Model, SerializerMixin):
    __tablename__ = 'performance_reviews'

    id = db.Column(db.Integer, primary_key=True)
    review_date = db.Column(db.DateTime, default=datetime.now)
    reviewer = db.Column(db.String(50))  # Manager's name
    notes = db.Column(db.Text)
    rating = db.Column(db.Integer)

    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    employee = db.relationship('Employee', back_populates='reviews')

    @property
    def employee_name(self):
        return f"{self.employee.first_name} {self.employee.last_name}"

    @property
    def employee_job_title(self):
        return self.employee.job_title.title if self.employee.job_title else None

    @property
    def employee_department(self):
        return self.employee.department.name if self.employee.department else None

    serialize_only = (
        "id",
        "review_date",
        "reviewer",
        "notes",
        "rating",
        "employee_id",
        "employee_name",
        "employee_job_title",
        "employee_department",
    )

    serialize_rules = ("-employee.reviews",)
