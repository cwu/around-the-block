$(window).on 'load', (evt) ->
  if window.location.hash == '#_=_'
    window.location.hash = ''
    history.pushState('', document.title, window.location.pathname)
    evt.preventDefault()

hasLocation = () -> !!($('meta[name=latitude]').attr('content') and $('meta[name=latitude]').attr('content'))

window.getLocation = () ->
  return {
    latitude : $('meta[name=latitude]').attr('content')
    longitude : $('meta[name=longitude]').attr('content')
  }

window.fetchLocation = (cb) ->
  if hasLocation()
    cb(coords : getLocation())
  else
    navigator.geolocation.getCurrentPosition(cb) if navigator?.geolocation?

$ ->
  if not hasLocation()
    window.fetchLocation (position) ->
      $.ajax
        url  : '/location'
        type : 'POST'
        data :
          latitude  : position.coords.latitude
          longitude : position.coords.longitude
        success : () ->
          $('meta[name=latitude]').attr('content', position.coords.latitude)
          $('meta[name=longitude]').attr('content', position.coords.longitude)
