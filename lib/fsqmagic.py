import string
import urlparse
import pprint
import random
from foursquare import Foursquare

pp = pprint.PrettyPrinter(indent=2)

class FsqMagic:
  def __init__(self, oauth, explore={}, photos=[]):
    self.f = Foursquare(access_token = oauth)
    self.explore = explore
    self.photos = photos

  def magic(self, latlong, dist=1000, limit=50, verbose=False):
    print "Explore\n"
    # explore venues
    explore = self.f.venues.explore(params={"ll":latlong,"friendVisits":"visited","radius":dist, "limit":limit, "section":"food"})["groups"][0]["items"]

    if verbose == True:
      print "Explore results:\n"
      pp.pprint(explore)

    # filter shitty results out
    print "Filter\n"
    filtered_explore = {}
    for i in explore:
      if i["reasons"]["count"] > 0:
        # sort by places
        filtered_explore[i["venue"]["name"]] = i

    if verbose == True:
      print "\nFiltered explore results:\n"
      pp.pprint(filtered_explore)

    self.explore = filtered_explore

    # make photo list
    print "Making photo list\n"
    for key in self.explore.keys():
      vid = self.explore[key]["venue"]["id"]
      venue_photos = self.f.venues.photos(vid, params={"group":"venue"})["photos"]["items"]
      for i in venue_photos:
        photo = {}
        photo["venue_id"] = vid;
        photo["url"] = i["prefix"] + "500x500" + i["suffix"]
        photo["photo_id"] = i["id"]
        self.photos.append(photo)
    random.shuffle(self.photos)

    if verbose == True:
      print "\nPhoto list:\n"
      pp.pprint(self.photos)

    return self.explore

  def get_photos(self, offset=0, limit=10):
    return self.photos[offset:offset+limit]
