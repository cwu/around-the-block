from flask import Flask, render_template

from assets.sass import sass_blueprint

app = Flask(__name__)
app.register_blueprint(sass_blueprint)

@app.route('/')
def hello():
    return render_template('hello.html')


if __name__ == '__main__':
    app.run(debug=True)
