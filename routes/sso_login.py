#! /usr/bin/env python3

# routes that are only needed for local servers, as production servers usually have their
# own login pages we redirect to. Everything you add to this file will only get imported
# if config.LOCAL_SERVER is True.

import datetime
import uuid
import urllib.parse

from flask import request, redirect

from api_utils import handle_client_errors
from config import AUTH_COOKIE
from odie import app, csrf, sqla
from login import get_user, login_required
from db.fsmi import User, Cookie

login_page_text = """<html>
<body>
<h1>Login</h1>
<form action="/login?target_path=%s" method='post'>
  <input name='username' placeholder="Username"/>
  <input name='password' placeholder="Password" type='password'/>
  <button type='submit'>Login</button>
</form>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login_page():
    if request.method == 'GET':
        # NB: Due to severe PHP, you'll need to also provide a (potentially empty)
        # target_paras GET parameter for redirection to work properly when logging into
        # the real fsmi servers.
        return login_page_text % urllib.parse.quote_plus(request.args.get('target_path'))
    user = User.authenticate(request.form['username'], request.form['password'])
    if user:
        # see comment in fsmi.Cookie.refresh as to why we need this in python
        now = datetime.datetime.now()
        cookie = str(uuid.uuid4())
        sqla.session.add(Cookie(sid=cookie, user_id=user.id, last_action=now, lifetime=172800))
        sqla.session.commit()
        response = app.make_response(redirect(request.args.get('target_path')))
        response.set_cookie(AUTH_COOKIE, value=cookie)
        return response
    return 'Nope'


@app.route('/logout')
@csrf.exempt
@handle_client_errors
@login_required
def logout():
    Cookie.query.filter_by(user_id=get_user().id).delete()
    sqla.session.commit()
    response = app.make_response(redirect(request.args.get('target_path')))
    response.set_cookie(AUTH_COOKIE, value='', expires=0)
    return response

