from flask import Flask, render_template

from sass import sass_blueprint

app = Flask(__name__)
app.register_blueprint(sass_blueprint)

@app.route('/hello')
def hello():
    return render_template('hello.html')


if __name__ == '__main__':
    app.run(debug=True)
