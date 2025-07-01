import re
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from models import Employee

EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

class AuthResource(Resource):
    # POST /auth/login
    def post(self, action):
        if action != "login":
            return {"error": "Invalid action"}, 400

        data = request.get_json() or {}
        email    = data.get("email", "").strip().lower()
        password = data.get("password", "")

        # --- Minimal validation -----------------
        if not email or not password:
            return {"error": "Email and password required"}, 400
        if not EMAIL_RE.match(email):
            return {"error": "Bad email format"}, 400

        # --- Authenticate ------------------------
        user = Employee.query.filter_by(email=email).first()
        if not user or not user.verify_password(password):
            return {"error": "Invalid credentials"}, 401

        token = create_access_token(identity=user.id)
        return {
            "user": user.to_dict(),
            "access_token": token
        }, 200
