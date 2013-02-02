from flask import request, Blueprint, g, make_response

import json
from lib.fbmagic import magic
import redis
import settings
import random

photos_blueprint = Blueprint('photos', __name__)

r = redis.StrictRedis(port=settings.REDIS_PORT)

def fb_to_common(fb_data):
  common_data = {
      'photos' : {},
      'places' : {},
  }
  for venue_name, properties in fb_data.iteritems():
    for event in properties['data']:
      if 'photo_url' not in event:
        continue

      mid = len(event['photo_url']) / 2

      photo = {
        'url'        : event['photo_url'][mid]['source'],
        'id'         : event['id'],
        'location'   : properties['location'],
        'from'       : event['from'],
        'tags'       : event.get('tags', {'data':[]})['data'],
        'date'       : event['created_time'],
        'place_id'   : properties['page_id'],
        'place_name' : venue_name,
      }
      common_data['photos'][event['id']] = photo

      if properties['page_id'] not in common_data['places']:
        common_data['places'][properties['page_id']] = {
          'location'  : properties['location'],
          'photo_url' : properties['photo_url'],
          'photos'    : [],
        }
      common_data['places'][properties['page_id']]['photos'].append(photo)
  return common_data

@photos_blueprint.route('/photos')
def photos():
  latitude = float(request.args['latitude'])
  longitude = float(request.args['longitude'])
  distance = request.args.get('range', 2000)

  oauth_token = g.user.fb_access_token

  cache_key = "fb-results-%s-%d-%d" % (g.user.id, int(latitude*1000), int(longitude*1000))
  item = r.get(cache_key)
  if not item:
    item = json.dumps(fb_to_common(magic(oauth_token, '%s,%s' % (latitude, longitude), dist=distance)))
    r.set(cache_key, item)

  return make_response(item)


@photos_blueprint.route('/ar_photos')
def ar_photos():
  latitude = float(request.args['latitude'])
  longitude = float(request.args['longitude'])
  distance = request.args.get('range', 2000)

  return make_response(r.get(random.choice(r.keys('fb-*'))))

