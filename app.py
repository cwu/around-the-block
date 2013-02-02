from flask import Flask, render_template

from assets.assets import assets_blueprint

app = Flask(__name__)
app.register_blueprint(assets_blueprint)

@app.route('/')
def hello():
    return render_template('base.html')


if __name__ == '__main__':
    app.run(debug=True)
