from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models import JobTitle

class JobTitleListResource(Resource):
    @jwt_required()
    def get(self):
        return [jt.to_dict() for jt in JobTitle.query.all()], 200


class JobTitleDetailResource(Resource):
    @jwt_required()
    def get(self, id):
        return JobTitle.query.get_or_404(id).to_dict(), 200
