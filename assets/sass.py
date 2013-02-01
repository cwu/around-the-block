import os.path
from subprocess import Popen, PIPE
from flask import Blueprint, Response, abort

from settings import STATIC_PATH

sass_blueprint = Blueprint('sass', __name__)

# Helper
def scss(data, load_path):
    args = ['--trace', '--scss', '--stdin', '-I', load_path]
    sass = Popen(['sass'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    sass.stdin.write(data)
    sass.stdin.flush()
    sass.stdin.close()
    sass.wait()

    css = sass.stdout.read()
    error = sass.stderr.read()

    if len(css) > 0:
        return True, css
    else:
        return False, error

# Sample route
@sass_blueprint.route('/stylesheets/<name>.css')
def css(name):
    print "hit"
    print STATIC_PATH
    dir_path = os.path.join(STATIC_PATH, 'stylesheets')
    print dir_path
    scss_path = os.path.join(dir_path, '%s.scss' % name)

    if not os.path.exists(scss_path):
        return abort(404)

    with open(scss_path) as fd:
        success, body = scss(fd.read(), dir_path)

    if success:
        return Response(body, status=200, content_type='text/css')
    else:
        return Response('<pre>%s</pre>' % body, status=500, content_type='text/html')
