from flask import Blueprint
from flask_restx import Api

api_v2 = Blueprint('api_v2', __name__)
api = Api(api_v2, version='2.0', title="TODOISM API", description="My TODOISM API")
ns = api.namespace("", description="Item and Auth Operations")

from todoism.apis.v2 import auth, resources
