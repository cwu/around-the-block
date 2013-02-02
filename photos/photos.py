from flask import request, Blueprint, g, make_response

import json
from lib.fbmagic import magic
import redis

photos_blueprint = Blueprint('photos', __name__)

r = redis.StrictRedis()

@photos_blueprint.route('/photos')
def photos():
  latitude = request.args['latitude']
  longitude = request.args['longitude']
  distance = request.args.get('range', 1000)

  oauth_token = g.user.fb_access_token

  cache_key = "%s-%s-%s" % (g.user.id, latitude, longitude)
  item = r.get(cache_key)
  if not item:
    item = json.dumps(magic(oauth_token, '%s,%s' % (latitude, longitude), dist=distance))
    r.set(cache_key, item)

  return make_response(item)
