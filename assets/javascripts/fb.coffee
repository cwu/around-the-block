window.fbAsyncInit = () ->
  FB.init
    appId  : $('meta[name=fb-app-id]').attr('content')
    status : true
    cookie : true
    xfbml  : true

  $('a.facebook-login').on 'click', () ->
    #kFB.login (response) ->
    #k  if response.authResponse
    #k    console.log response
    #k  else
    #k    console.log 'boo'

    #kreturn false
