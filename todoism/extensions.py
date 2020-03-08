from flask import request, current_app
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel, _
from flasgger import Swagger

db = SQLAlchemy()
csrf = CSRFProtect()
login_manage = LoginManager()
babel = Babel()
swagger = Swagger()

login_manage.login_view = 'auth.login'
login_manage.login_message = _('Please login to access this page.')


@login_manage.user_loader
def load_user(user_id):
    from todoism.models import User
    return User.query.get(int(user_id))


@babel.localeselector
def get_locale():
    if current_user.is_authenticated and current_user.locale is not None:
        return current_user.locale

    locale = request.cookies.get('locale')
    if locale is not None:
        return locale
    return request.accept_languages.best_match(current_app.config['TODOISM_LOCALES'])