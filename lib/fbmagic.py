from facebook import GraphAPI
import string
import urlparse
import pprint

pp = pprint.PrettyPrinter(indent=2)

def magic(oauth, latlong, dist=1000, limit=5, verbose=True):
  g = GraphAPI(oauth)

  # search a bunch of stuff, until no more results
  # https://graph.facebook.com/search?type=location&center=[lat],[long]&distance=[dist]&access_token=[oauth]
  search = []
  params = {"type":"location", "center":latlong, "distance":dist, "access_token":oauth}
  while limit > 0:
    res = g.request("search", params)
    if len(res.keys()) == 0 or not res.get("paging"):
      break
    search += res["data"]
    params = dict(urlparse.parse_qsl(res["paging"]["next"].split("?")[1]))
    limit -= 1

  if verbose == True:
    pp.pprint(search)

  # filter
  places = g.fql("SELECT name, location, type, page_id FROM page where page_id in (%s)" % string.join([i["place"]["id"] for i in search], ", "))
  desired_place_types = ["RESTAURANT/CAFE", "BAR", "CLUB", "FOOD/BEVERAGES", "LOCAL BUSINESS"]
  limit = 1;
  filtered_places = {}
  for i in places:
    if i["type"].upper() in desired_place_types:
      name = i["name"]
      filtered_places[name] = i
      filtered_places[name]["data"] = []
      page = g.get_object(str(i["page_id"]) + "/picture", width="600")
      if page.get("url"):
        filtered_places[name]["photo_url"] = page["url"]
      del i["name"]

  if verbose == True:
    pp.pprint(filtered_places)

  # sort by places
  for i in search:
    if i["place"]["name"] in filtered_places:
      filtered_places[i["place"]["name"]]["data"].append(i)
      del i["place"]

      # get fb picture urls if can
      if i["type"] == "photo":
        photo = g.get_object(i["id"])
        if photo.get("images"):
          i["photo_url"] = photo["images"]

  if verbose == True:
    pp.pprint(filtered_places)

  return filtered_places
