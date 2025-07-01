import os
from datetime import timedelta
from dotenv import load_dotenv

from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from models import db
# ==== Import and Register Resources
from resources.auth import AuthResource
from resources.employee import EmployeeListResource, EmployeeDetailResource,TotalEmployeesResource
from resources.review import ReviewListResource, ReviewDetailResource
from resources.department import DepartmentListResource, DepartmentDetailResource
from resources.user_type import UserTypeListResource, UserTypeDetailResource
from resources.job_title import JobTitleListResource, JobTitleDetailResource



# ==== Load environment variables 
load_dotenv()

# Initialize Flask App 
app = Flask(__name__)

# ==== Configurations ====
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI") 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

#Debug print to check if .env was loaded correctly
print("JWT SECRET:", app.config["JWT_SECRET_KEY"]) 

# ==== Extensions Initialization ====
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
db.init_app(app)
CORS(app)
api = Api(app)

# ==== JWT Unauthorized Handling 
@jwt.unauthorized_loader
def missing_token(error):
    return {
        "message": "Authorization required",
        "success": False,
        "errors": ["Authorization token is required"],
    }, 401
@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return {"message": "Invalid token", "reason": reason}, 422

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {"message": "Token expired"}, 401



api.add_resource(AuthResource, '/auth/<string:action>') 
api.add_resource(EmployeeListResource, "/employees")
api.add_resource(EmployeeDetailResource, "/employees/<int:id>")
api.add_resource(TotalEmployeesResource, '/total-employees')
api.add_resource(ReviewListResource, "/reviews")
api.add_resource(ReviewDetailResource, "/reviews/<int:id>")
api.add_resource(DepartmentListResource, "/departments")
api.add_resource(DepartmentDetailResource, "/departments/<int:id>")
api.add_resource(UserTypeListResource, "/user-types")
api.add_resource(UserTypeDetailResource, "/user-types/<int:id>")
api.add_resource(JobTitleListResource, "/job-titles")
api.add_resource(JobTitleDetailResource, "/job-titles/<int:id>")



# ==== Entry Point ====
if __name__ == "__main__":
    app.run(port=5555, debug=True)
