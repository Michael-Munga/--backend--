from flask import make_response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Employee, UserType, JobTitle, Department, db

# Utility: Get the current logged-in user
def current_user():
    return Employee.query.get(get_jwt_identity())

# ========== EMPLOYEE LIST ==========
class EmployeeListResource(Resource):
    @jwt_required()
    def get(self):
        user = current_user()
        employees = []

        if user.user_type_name == "HR":
            employees = Employee.query.all()
            print(f"HR user '{user.email}' is fetching ALL employees.") # For debugging
        elif user.user_type_name == "Manager":
            employees = Employee.query.filter_by(department_id=user.department_id).all()
            print(f"Manager user '{user.email}' is fetching employees for department '{user.department.name}'.") # For debugging
        else:
            return make_response({"error": "Forbidden: You do not have permission to view employee lists."}, 403)

        return make_response([e.to_dict() for e in employees], 200)

    @jwt_required()
    def post(self):
        user = current_user()
        data = request.get_json()

        # Validate required fields
        required_fields = ["first_name", "last_name", "email", "password", "user_type_name", "job_title_name"]
        if user.user_type_name == "HR":
            required_fields.append("department_id")

        missing = [field for field in required_fields if field not in data]
        if missing:
            return make_response({"error": f"Missing fields: {', '.join(missing)}"}, 400)

        # Check for duplicate email
        if Employee.query.filter_by(email=data["email"].strip().lower()).first():
            return make_response({"error": "Email already exists"}, 400)

        # Get user type
        user_type = UserType.query.filter_by(name=data["user_type_name"]).first()
        if not user_type:
            return make_response({"error": "Invalid user type"}, 400)

        # --- FIX: Check if job title exists, if not, create it ---
        job_title_name = data["job_title_name"].strip()
        job_title = JobTitle.query.filter_by(title=job_title_name).first()
        if not job_title:
            try:
                new_job_title = JobTitle(title=job_title_name)
                db.session.add(new_job_title)
                db.session.commit() # Commit new job title to get its ID
                job_title = new_job_title # Use the newly created job title
                print(f"Created new job title: {job_title_name}") # For debugging
            except Exception as e:
                db.session.rollback()
                return make_response({"error": f"Failed to create new job title: {str(e)}"}, 500)
        

        # Determine department_id based on user role
        department_id = None
        if user.user_type_name == "HR":
            department_id = data.get("department_id")
            if not department_id:
                return make_response({"error": "Department ID is required for HR to add an employee."}, 400)
            if not Department.query.get(department_id):
                return make_response({"error": "Invalid Department ID"}, 400)
        elif user.user_type_name == "Manager":
            department_id = user.department_id
        else:
            return make_response({"error": "Forbidden: Only HR or Managers can add employees."}, 403)

        new_employee = Employee(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"].strip().lower(),
            phone=data.get("phone"),
            department_id=department_id,
            user_type_id=user_type.id,
            job_title_id=job_title.id 
        )
        new_employee.set_password(data["password"])

        try:
            db.session.add(new_employee)
            db.session.commit()
            return make_response(new_employee.to_dict(), 201)
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)


# ========== EMPLOYEE DETAIL ==========
class EmployeeDetailResource(Resource):
    @jwt_required()
    def get(self, id):
        user = current_user()
        target_employee = Employee.query.get(id)
        if not target_employee:
            return make_response({"error": "Employee not found"}, 404)

        if user.user_type_name == "HR":
            return make_response(target_employee.to_dict(), 200)
        elif user.user_type_name == "Manager" and user.department_id == target_employee.department_id:
            return make_response(target_employee.to_dict(), 200)
        elif user.id == id:
            return make_response(target_employee.to_dict(), 200)
        else:
            return make_response({"error": "Forbidden: You do not have permission to view this employee's details."}, 403)


class TotalEmployeesResource(Resource):
    @jwt_required()
    def get(self):
        user = current_user()
        if user.user_type_name != "HR":
            return make_response({"message": "Forbidden: Only HR can view the total employee count."}, 403)
        total_employees = Employee.query.count()
        return make_response({"total_employees": total_employees}, 200)
