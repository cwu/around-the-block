from flask import Flask, render_template, url_for, redirect, g, session, request, make_response

import settings
from assets.assets import assets_blueprint
from auth.auth import auth_blueprint
from photos.photos import photos_blueprint
from datetime import datetime, timedelta
import time

import models as m

import db

app = Flask(__name__)
app.secret_key = 'SECRET'
app.config.from_object(settings)

app.register_blueprint(assets_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(photos_blueprint)

# required by flask for handling sessions properly
@app.teardown_request
def shutdown_session(exception=None):
  db.session.remove()

db.init()

@app.before_request
def load_user():
  if 'user_id' in session:
    g.user = m.User.query.filter_by(id=session["user_id"]).first()
  else:
    g.user = None

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/main')
def main():
  if not g.user:
    return redirect(url_for('.index'))
  return render_template('main.html')

@app.route('/map')
def map():
  return render_template('map.html')

@app.route('/location', methods=['POST'])
def location():
  five_min_from_now = int(time.mktime((datetime.now() + timedelta(minutes=5)).timetuple()))
  response = make_response('OK')
  response.set_cookie('lat', request.form['latitude'], expires=five_min_from_now)
  response.set_cookie('long', request.form['longitude'], expires=five_min_from_now)
  return response


#TODO: route depends on photo
@app.route('/detail')
def detail():
    return render_template('detail.html')

if __name__ == '__main__':
    app.run(debug=True)
