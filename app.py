from flask import Flask, render_template

import settings
from assets.assets import assets_blueprint
from auth.auth import auth_blueprint

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

@app.route('/')
def hello():
  from lib.auth import get_user
  return render_template('index.html', user=get_user())

@app.route('/main')
def main():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)
