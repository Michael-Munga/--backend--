from flask import request, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Employee, PerformanceReview
from datetime import datetime

# Helper function to get the current logged-in user
def current_user():
    return Employee.query.get(get_jwt_identity())

class ReviewListResource(Resource):
    @jwt_required()
    def get(self):
        user = current_user()

        reviews = []

        # HR can fetch all reviews
        if user.user_type_name == "HR":
            reviews = PerformanceReview.query.all()
            print(f"HR user '{user.email}' is fetching ALL reviews.") # For debugging

        # Managers fetch reviews for employees in their department
        elif user.user_type_name == "Manager":
            reviews = PerformanceReview.query.join(Employee).filter(
                Employee.department_id == user.department_id
            ).all()
            print(f"Manager user '{user.email}' is fetching reviews for department '{user.department.name}'.") # For debugging

        # Employees fetch only their own reviews
        else: # Covers 'Employee' user type and any other unhandled types
            reviews = PerformanceReview.query.filter_by(employee_id=user.id).all()
            print(f"Employee user '{user.email}' is fetching their own reviews.") # For debugging

        # Return all retrieved reviews as JSON
        return make_response([r.to_dict() for r in reviews], 200)

    @jwt_required()
    def post(self):
        user = current_user()

        # ONLY managers can add new reviews, and only for employees in their department
        data = request.get_json()
        employee_id_to_review = data.get("employee_id")

        employee_to_review = Employee.query.get(employee_id_to_review)

        # Check if user is a manager and the employee exists and is in their department
        if not (user.user_type_name == "Manager" and
                employee_to_review and
                employee_to_review.department_id == user.department_id):
            return make_response({"error": "Forbidden: Only managers can add reviews for employees in their department."}, 403)

        # Ensure employee_id is provided and valid
        if not employee_id_to_review:
            return make_response({"error": "Employee ID is required"}, 400)
        
        # If employee_to_review is None, it means the ID was invalid/not found
        if not employee_to_review:
             return make_response({"error": "Employee not found"}, 404)


        review = PerformanceReview(
            employee_id=employee_id_to_review,
            reviewer=f"{user.first_name} {user.last_name}",
            notes=data.get("notes"),
            rating=data.get("rating"),
            review_date=datetime.now() # Using datetime.now() for datetime column
        )

        db.session.add(review)
        db.session.commit()

        # Return the created review
        return make_response(review.to_dict(), 201)


class ReviewDetailResource(Resource):
    @jwt_required()
    def put(self, id):
        user = current_user()
        review = PerformanceReview.query.get_or_404(id)

        # Check if the user is the manager of the department the employee belongs to
        if not (user.user_type_name == "Manager" and
                review.employee.department_id == user.department_id):
            return make_response({"error": "Forbidden: Only the manager of this employee's department can edit this review."}, 403)

        data = request.get_json()

        # Update editable fields (notes and rating)
        for field in ["notes", "rating"]:
            if field in data:
                setattr(review, field, data[field])
            else: # If a field is explicitly sent as null, set it to None
                if field in data and data[field] is None:
                    setattr(review, field, None)

        db.session.commit()
        return make_response(review.to_dict(), 200)

    @jwt_required()
    def delete(self, id):
        user = current_user()
        review = PerformanceReview.query.get_or_404(id)

        # Check if the user is the manager of the department the employee belongs to
        if not (user.user_type_name == "Manager" and
                review.employee.department_id == user.department_id):
            return make_response({"error": "Forbidden: Only the manager of this employee's department can delete this review."}, 403)

        db.session.delete(review)
        db.session.commit()

        # Return 204 No Content
        return {}, 204