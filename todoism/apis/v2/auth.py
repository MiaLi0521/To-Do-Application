from functools import wraps

from flask import g, current_app, request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from flask_restx import Resource, fields

from todoism.models import User
from todoism.apis.v2 import api, ns


def generate_token(user):
    expiration = 3600
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    token = s.dumps({'id': user.id}).decode('ascii')
    return token, expiration


def validate_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return False
    user = User.query.get(data['id'])
    if user is None:
        return False
    g.current_user = user
    return True


def get_token():
    """Flask/Werkzeug do not recognize any authentication types other than Basic or Digest,
    so here we parse the header by hand."""
    if 'Authorization' in request.headers:
        try:
            token_type, token = request.headers['Authorization'].split(None, 1)
        except ValueError:
            # The Authorization header is either empty or has no token
            token_type = token = None
    else:
        token_type = token = None

    return token_type, token


parser = api.parser()
parser.add_argument("username", required=True, help="Name cannot be blank!", type=str, location="form")
parser.add_argument("password", required=True, help="Password cannot be blank!", type=str, location="form")


@ns.route('/oauth/token')
class AuthTokenAPI(Resource):

    @api.doc(parser=parser)
    def post(self):
        """Bearer授权接口,响应头我是设不来，怎么也不生效"""
        args = parser.parse_args()
        grant_type = 'password'
        username = args.get('username')
        password = args.get('password')

        if grant_type is None or grant_type.lower() != 'password':
            api.abort(400, message='The grant type must be password.', code='400')

        user = User.query.filter_by(username=username).first()
        if user is None or not user.validate_password(password):
            api.abort(400, message='Either the username or password was invalid.')

        token, expiration = generate_token(user)

        return {
            'access_token': generate_token(user),
            'token_type': 'Bearer',
            'expires_in': expiration
        }

