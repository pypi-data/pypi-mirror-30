from functools import wraps

from myslx import config
from flask import g, url_for
from werkzeug.utils import redirect


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(
                f"https://{config.PORTAL_DOMAIN}/auth/oauth/authorize?client_id={config.OAUTH_CLIENT_ID}&response_type=code&redirect_uri={url_for('myslx.callback', _external=True)}"
            )

        return f(*args, **kwargs)

    return decorated_function
