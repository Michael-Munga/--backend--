from flask import make_response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity 
from models import db, Department, Employee

# Utility: Get the current logged-in user

def current_user():
    return Employee.query.get(get_jwt_identity())

class DepartmentListResource(Resource):
    @jwt_required()
    def get(self):
        user = current_user()

        # Policy: Only HR and Managers can view the list of all departments.
        if user.user_type_name not in ["HR", "Manager"]:
            return make_response({"message": "Forbidden: You do not have access to view departments."}, 403)

        departments = Department.query.all()
        return make_response([{"id": d.id, "name": d.name, "description": d.description, "manager_name": d.manager_name} for d in departments], 200)

    @jwt_required()
    def post(self):
        user = current_user()

        # Only HR can add new departments
        if user.user_type_name != "HR":
            return make_response({"error": "Forbidden: Only HR can add departments."}, 403)

        data = request.get_json()

        # Validate required fields
        if not data or "name" not in data:
            return make_response({"error": "Department name is required."}, 400)

        department_name = data["name"].strip()
        description = data.get("description", "").strip()

        # Check for duplicate department name
        if Department.query.filter_by(name=department_name).first():
            return make_response({"error": f"Department with name '{department_name}' already exists."}, 409) # 409 Conflict

        new_department = Department(name=department_name, description=description)

        try:
            db.session.add(new_department)
            db.session.commit()
            # Return the newly created department's serialized data
            return make_response(new_department.to_dict(), 201) # 201 Created
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)


class DepartmentDetailResource(Resource):
    @jwt_required()
    def get(self, id):
        user = current_user() # Get the logged-in user

        department = Department.query.get(id)
        if not department:
            return make_response({"error": "Department not found"}, 404)

        # Policy: Only HR and Managers can view department details.
        if user.user_type_name in ["HR", "Manager"]:
            return make_response(department.to_dict(), 200)
        # Employees can view their own department details
        elif user.user_type_name == "Employee" and user.department_id == department.id:
            return make_response(department.to_dict(), 200)
        # Otherwise, forbidden
        else:
            return make_response({"message": "Forbidden: You do not have access to view department details."}, 403)

