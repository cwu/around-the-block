from flask import request, Blueprint, g, make_response

import json
from lib.fbmagic import magic
import redis
import settings

photos_blueprint = Blueprint('photos', __name__)

r = redis.StrictRedis(port=settings.REDIS_PORT)

@photos_blueprint.route('/photos')
def photos():
  latitude = float(request.args['latitude'])
  longitude = float(request.args['longitude'])
  distance = request.args.get('range', 2000)

  oauth_token = g.user.fb_access_token

  cache_key = "fb-results-%s-%d-%d" % (g.user.id, int(latitude*10000), int(longitude*10000))
  item = r.get(cache_key)
  if not item:
    item = json.dumps(magic(oauth_token, '%s,%s' % (latitude, longitude), dist=distance))
    r.set(cache_key, item)

  return make_response(item)
