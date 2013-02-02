from flask import Flask, render_template, url_for, redirect, g, session

import settings
from assets.assets import assets_blueprint
from auth.auth import auth_blueprint

import models as m

import db

app = Flask(__name__)
app.secret_key = 'SECRET'
app.config.from_object(settings)

app.register_blueprint(assets_blueprint)
app.register_blueprint(auth_blueprint)

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
def hello():
  if g.user:
    return redirect(url_for('.main'))
  return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/map')
def map():
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
