from flask import request, Blueprint, url_for, redirect, session

import db
import settings
import urllib
import urlparse
import requests
import models as m

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/fb_login')
def fb_login():
  fb_args = {
    'client_id' : settings.FB_APP_ID,
    'redirect_uri' : url_for('.fb_login', _external=True)
  }

  if 'code' in request.args:
    fb_args['client_secret'] = settings.FB_SECRET
    fb_args['code'] = request.args['code']

    url = 'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(fb_args)
    content = requests.get(url).content
    response = urlparse.parse_qs(content)

    fb_access_token = response['access_token'][-1]

    url = 'https://graph.facebook.com/me?access_token=%s' % fb_access_token
    user_profile = requests.get(url, params={'access_token' : fb_access_token}).json()

    user = m.User.query.filter(m.User.fb_uid==int(user_profile['id'])).first()
    if not user:
      user = m.User(name=user_profile['name'], fb_uid=int(user_profile['id']), fb_access_token=fb_access_token)
      db.session.add(user)
      db.session.commit()

    session['user_id'] = user.id

    return redirect('/')
  else:
    url = "http://www.facebook.com/dialog/oauth?%s" % urllib.urlencode(fb_args)
    return redirect(url)
