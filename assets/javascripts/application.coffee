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
