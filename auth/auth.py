from flask import request, Blueprint, url_for, redirect, session

import foursquare
import db
import settings
import urllib
import urlparse
import requests
import models as m

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/fb_login')
def fb_login():
  args = {
    'client_id'    : settings.FB_APP_ID,
    'redirect_uri' : url_for('.fb_login', _external=True),
    'scope'        : "user_status,user_photos,friends_status,friends_photos",
  }

  if 'code' in request.args:
    args['client_secret'] = settings.FB_SECRET
    args['code'] = request.args['code']

    url = 'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(args)
    content = requests.get(url).content
    response = urlparse.parse_qs(content)

    fb_access_token = response['access_token'][-1]

    url = 'https://graph.facebook.com/me?access_token=%s' % fb_access_token
    user_profile = requests.get(url, params={'access_token' : fb_access_token}).json()

    user = m.User.query.filter(m.User.fb_uid==int(user_profile['id'])).first()
    if user:
      # update auth token
      user.name = user_profile['name']
      user.fb_access_token = fb_access_token
    else:
      # create user
      user = m.User(name=user_profile['name'], fb_uid=int(user_profile['id']), fb_access_token=fb_access_token)

    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id

    return redirect('/')
  else:
    url = "http://www.facebook.com/dialog/oauth?%s" % urllib.urlencode(args)
    return redirect(url)

@auth_blueprint.route('/fs_login')
def fs_login():
  args = {
    'client_id'    : settings.FS_APP_ID,
    'redirect_uri' : url_for('.fs_login', _external=True),
  }
  client = foursquare.Foursquare(
    client_id=settings.FS_APP_ID,
    client_secret=settings.FS_SECRET,
    redirect_uri=url_for('.fs_login', _external=True),
  )

  if 'code' in request.args:
    args['client_secret'] = settings.FS_SECRET
    args['code'] = request.args['code']
    args['grant_type'] = 'authorization_code'

    url = 'https://foursquare.com/oauth2/access_token?' + urllib.urlencode(args)
    response = requests.get(url).json()

    fs_access_token = response['access_token']
    client.set_access_token(fs_access_token)

    fs_uid = client.users()['user']['id']

    user = m.User.query.filter(m.User.fs_uid==int(fs_uid)).first()
    if user:
      # update auth token
      user.fs_access_token = fs_access_token
    else:
      # create user
      user = m.User(fs_uid=int(fs_uid), fs_access_token=fs_access_token)

    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id

    return redirect('/')
  else:
    args['response_type'] = 'code'
    url = "https://foursquare.com/oauth2/authenticate?" + urllib.urlencode(args)
    return redirect(url)
