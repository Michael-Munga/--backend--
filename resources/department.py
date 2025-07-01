from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models import Department

class DepartmentListResource(Resource):
    @jwt_required()
    def get(self):
        return [d.to_dict() for d in Department.query.all()], 200


class DepartmentDetailResource(Resource):
    @jwt_required()
    def get(self, id):
        return Department.query.get_or_404(id).to_dict(), 200
