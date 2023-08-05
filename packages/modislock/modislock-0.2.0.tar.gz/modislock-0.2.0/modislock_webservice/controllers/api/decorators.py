from functools import wraps
from datetime import datetime
from flask import request
from werkzeug.security import check_password_hash

from ...models import AppApiAccess, AppApi


def app_required(func):
    """Wrapper that requires either app_id / password or app token for authentication
    
    :param func: func
    :return: none
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        app_id = request.headers.get('X-APP-ID')
        app_password = request.headers.get('X-APP-PASSWORD')
        app_token = request.headers.get('X-APP-TOKEN')

        if (app_id is None) and (app_token is None):
            return {'message': {'error': 'CREDENTIALS_REQUIRED'}}, 403

        if app_id:
            app = AppApi.query.filter_by(app_api_id=app_id).one_or_none()

            if app:
                if not check_password_hash(app.app_secret, app_password):
                    return {'message': {'error': 'INVALID_CREDENTIALS'}}, 403
            else:
                return {'message': {'error': 'ID_NOT_FOUND'}}, 403

        elif app_token:
            app = AppApiAccess.query.filter_by(token=app_token).one_or_none()

            if app:
                if app.expires < datetime.now():
                    return {'message': {'error': 'TOKEN_EXPIRED'}}, 403
            else:
                return {'message': {'error': 'TOKEN_NOT_FOUND'}}, 403

        return func(*args, **kwargs)
    return decorated_function
