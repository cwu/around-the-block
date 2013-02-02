from flask import request, Blueprint, g, make_response, abort

import db
import json
from lib.fbmagic import magic
from lib.fsqmagic import FsqMagic
import redis
import settings
import random
from facebook import GraphAPIError

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
        'type'       : 'fb',
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
          'type'      : 'fb',
          'location'  : properties['location'],
          'photo_url' : properties['photo_url'],
          'photos'    : [],
          'name'      : venue_name,
        }
      common_data['places'][properties['page_id']]['photos'].append(photo)
  return common_data

def fs_to_common(place_data, photo_data):
  common_data = {
    'photos' : {},
    'places' : {},
  }
  for venue_name, properties in place_data.iteritems():
    venue    = properties['venue']
    location = venue['location']

    location['street']    = location.pop('address')
    location['state']     = location.pop('state')
    location['latitude']  = location.pop('lat')
    location['longitude'] = location.pop('lng')
    venue['location']     = location

    common_data['places'][venue['id']] = {
        'type'     : 'fs',
        'location' : venue['location'],
        'photos'   : [],
        'name'     : venue_name,
    }

  for photo in photo_data:
     photo_data = {
       'type'       : 'fs',
       'id'         : photo['id'],
       'url'        : photo['url'],
       'location'   : common_data['places'][photo['venue_id']]['location'],
       'from'       : { 'id' : '', 'name' : '' },
       'tags'       : [],
       'date'       : photo['date'],
       'place_id'   : photo['venue_id'],
       'place_name' : common_data['places'][photo['venue_id']]['name']
     }
     common_data['photos'][photo['id']] = photo_data
     common_data['places'][photo['venue_id']]['photos'].append(photo_data)

  return common_data


@photos_blueprint.route('/photos')
def photos():
  latitude = float(request.args['latitude'])
  longitude = float(request.args['longitude'])
  distance = request.args.get('range', 2000)

  oauth_token = g.user.fb_access_token

  fb_cache_key = "fb-results-%s-%d-%d" % (g.user.id, int(latitude*1000), int(longitude*1000))
  fb_item = r.get(fb_cache_key)
  if not fb_item and oauth_token:
    try:
      fb_item = json.dumps(fb_to_common(magic(oauth_token, '%s,%s' % (latitude, longitude), dist=distance)))
      r.set(fb_cache_key, fb_item)
    except GraphAPIError:
      g.user.fb_access_token = None
      db.session.add(g.user)
      db.session.commit()
      abort()
  elif not oauth_token:
    fb_item = '{"photos":{},"places":{}}'

  fs_cache_key = "fs-results-%s-%d-%d" % (g.user.id, int(latitude*1000), int(longitude*1000))

  oauth_token = g.user.fs_access_token
  fs_magic = FsqMagic(oauth_token)
  fs_item = r.get(fs_cache_key)
  if not fs_item and oauth_token:
    fs_item = json.dumps(fs_to_common(
      fs_magic.magic('%s,%s' % (latitude, longitude), dist=distance),
      fs_magic.get_photos(limit=20)))
    r.set(fs_cache_key, fs_item)
  elif not oauth_token:
    fs_item = '{"photos":{},"places":{}}'

  # merge the two
  results = json.loads(fb_item)
  fs_dict = json.loads(fs_item)

  results['photos'].update(fs_dict['photos'])
  results['places'].update(fs_dict['places'])

  return make_response(json.dumps(results))


@photos_blueprint.route('/ar_photos')
def ar_photos():
  #latitude = float(request.args['latitude'])
  #longitude = float(request.args['longitude'])
  #distance = request.args.get('range', 2000)

  return make_response(r.get(random.choice(r.keys('fb-*'))))

