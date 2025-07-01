from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models import UserType

class UserTypeListResource(Resource):
    @jwt_required()
    def get(self):
        return [ut.to_dict() for ut in UserType.query.all()], 200


class UserTypeDetailResource(Resource):
    @jwt_required()
    def get(self, id):
        return UserType.query.get_or_404(id).to_dict(), 200
