$(window).on 'load', (evt) ->
  if window.location.hash == '#_=_'
    window.location.hash = ''
    history.pushState('', document.title, window.location.pathname)
    evt.preventDefault()

window.hasLocation = () -> !!($('meta[name=latitude]').attr('content') and $('meta[name=latitude]').attr('content'))

window.getLocation = () ->
  return {
    latitude : $('meta[name=latitude]').attr('content')
    longitude : $('meta[name=longitude]').attr('content')
  }

window.fetchLocation = (cb) ->
  if hasLocation()
    cb(coords : getLocation())
  else if navigator?.geolocation?
    navigator.geolocation.getCurrentPosition (position) ->
      $.ajax
        url  : '/location'
        type : 'POST'
        data :
          latitude  : position.coords.latitude
          longitude : position.coords.longitude
        success : () ->
          $('meta[name=latitude]').attr('content', position.coords.latitude)
          $('meta[name=longitude]').attr('content', position.coords.longitude)
      cb(position)

mainPhotosTemplate = Handlebars.compile(
  """
  <div class="photo">
    <img src="{{url}}" />
  </div>
  """
)
window.renderMain = (position) ->
  $.ajax
    url : "/photos?latitude=#{ position.coords.latitude }&longitude=#{ position.coords.longitude }"
    success : (response) ->
      json = JSON.parse response
      window.json = json
      photoUrls = _.flatten(_.map json, (place, placeName) ->
        _.map place.data, (item) ->
          if item.photo_url
            return [item.photo_url[0].source]
          else
            return []
      )
      _.each photoUrls, (photoUrl) ->
        $('#container').append(mainPhotosTemplate(url : photoUrl))

window.renderMapView = (position) ->
  $.ajax
    url : "/photos?latitude=#{ position.coords.latitude }&longitude=#{ position.coords.longitude }"
    success : (response) ->
      map = L.map('map')
      L.tileLayer('http://{s}.tile.cloudmade.com/d57249c45c2c486c9653c5f2600cafbc/997/256/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
        maxZoom: 18
      }).addTo(map)
      map.locate({setView: true, maxZoom: 16})
      L.marker([position.coords.latitude, position.coords.longitude], {color: '#FF0000'}).addTo(map).bindPopup('You are here').openPopup()

      json = JSON.parse response
      window.json = json
      photoUrls = _.flatten(_.map json, (place, placeName) ->
        _.map place.data, (item) ->
          if item.photo_url
            return [item.photo_url[0].source]
          else
            return []
      )
      locations = _.map json, (place, placeName) ->
        if place.data[0].photo_url
          return [place.location.latitude, place.location.longitude, place.data[0].photo_url[0].source]
        else
          return [place.location.latitude, place.location.longitude, null]
      _.each locations, (location) ->
        if location[2] != null
          L.marker([location[0], location[1]]).addTo(map).bindPopup('<img src="' + location[2] + '" />').openPopup()
        else
          L.marker([location[0], location[1]]).addTo(map).bindPopup('No photo here').openPopup()
      _.each photoUrls, (photoUrl) ->
        $('#scroll-container').append(mainPhotosTemplate(url : photoUrl))
