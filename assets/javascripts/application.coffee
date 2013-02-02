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
    <a href="/detail/{{id}}"><img src="{{url}}" /></a>
  </div>
  """
)
window.renderMain = (position) ->
  $.ajax
    url : "/photos?latitude=#{ position.coords.latitude }&longitude=#{ position.coords.longitude }"
    success : (response) ->
      json = JSON.parse response
      window.json = json
      _.each json.photos, (photo) ->
        $('#container').append(mainPhotosTemplate(url : photo.url, id: photo.id))

window.renderMapView = (position) ->
  $.ajax
    url : "/photos?latitude=#{ position.coords.latitude }&longitude=#{ position.coords.longitude }"
    success : (response) ->
      map = L.map('map')
      L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
        maxZoom: 18
      }).addTo(map)
      map.locate({setView: true, maxZoom: 14})
      L.marker([position.coords.latitude, position.coords.longitude], {color: '#FF0000'}).addTo(map).bindPopup('You are here').openPopup()

      json = JSON.parse response
      window.json = json
      _.each json.places, (place) ->
        latLong = [place.location.latitude, place.location.longitude]
        randomPhoto = place.photos[_.random(0, place.photos.length-1)]
        L.marker(latLong).addTo(map).bindPopup("<a href=\"/detail/#{ randomPhoto.id}\"><img src=\"#{randomPhoto.url}\"/></a>").openPopup()
      _.each json.photos, (photo) ->
        $('#scroll-container').append(mainPhotosTemplate(url : photo.url, id: photo.id))

photoDetailsTemplate = Handlebars.compile(
  """
  <img class="profile-picture" src="https://graph.facebook.com/{{ id }}/picture?type=large" />
  <span>{{ name }} - {{ date }}</span>
  {{#if date }}
    <span>{{ name }} - {{ date }}</span>
  {{ else }}
    <span>{{ name }}</span>
  {{/if}}
  </div>
  """
)
photoProfileTemplate = Handlebars.compile(
  """
  <img class="profile-picture" src="https://graph.facebook.com/{{ id }}/picture?type=large" />
  """
)
photoTemplate = Handlebars.compile(
  """
  <img src="{{ url }}" />
  """
)
locationTemplate = Handlebars.compile(
  """
  {{ street }} {{ city }}, {{ province }} - {{ zip }}
  """
)
window.renderDetailView = (position) ->
  $.ajax
    url : "/photos?latitude=#{ position.coords.latitude }&longitude=#{ position.coords.longitude }"
    success : (response) ->
      urlParts = document.URL.split('/')
      photoID = urlParts[urlParts.length-1]

      json = JSON.parse response
      window.json = json

      photo = json.photos[photoID]
      latLong = [photo.location.latitude, photo.location.longitude]

      map = L.map('map-detail').setView(latLong, 13)
      L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
        maxZoom: 18
      }).addTo(map)

      L.marker(latLong).addTo(map).bindPopup('Photo was taken here')
      $('#main-image').append(photoTemplate(url : photo.url))
      d = new Date(photo.date)
      $('#photo-details').append(photoDetailsTemplate(
        id: photo.from.id,
        name : photo.from.name,
        date: if isNaN(d.getTime()) then '' else d.toDateString()
      ))
      $('#location-details').append(locationTemplate(
        street   : photo.location.street
        city     : photo.location.city
        province : photo.location.state
        zip      : photo.location.zip
      ))
      _.each photo.tags, (tag) ->
        $('#friend-details').append(photoProfileTemplate(id: tag.id))
