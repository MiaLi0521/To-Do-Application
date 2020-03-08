from flask import Blueprint
from flask_cors import CORS

api_v1 = Blueprint('api_v1', __name__)

# 为api蓝本中的路由添加跨域请求支持
CORS(api_v1)

from todoism.apis.v1 import resources