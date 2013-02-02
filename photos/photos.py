from flask import request, Blueprint, redirect, session, g, make_response

import json
from lib.fbmagic import magic
import redis

photos_blueprint = Blueprint('photos', __name__)

r = redis.StrictRedis()

@photos_blueprint.route('/photos')
def photos():
  latitude = request.args['latitude']
  longitude = request.args['longitude']

  oauth_token = g.user.fb_access_token

  cache_key = "%s-%s-%s" % (g.user.id, latitude, longitude)
  item = r.get(cache_key)
  if not item:
    try:
      item = json.dumps(magic(oauth_token, '%s,%s' % (latitude, longitude)))
      r.set(cache_key, item)
    except Exception:
      session.pop('user_id')
      return redirect('/')

  return make_response(item)
