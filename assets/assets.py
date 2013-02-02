import os.path
from subprocess import Popen, PIPE
from flask import Blueprint, Response, abort

from functools import partial

from settings import STATIC_PATH

assets_blueprint = Blueprint('assets', __name__)

# Helper
def compile_asset(compiler, compiler_args, data):
    compilation = Popen(
        [compiler] + compiler_args,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE
    )
    compilation.stdin.write(data)
    compilation.stdin.flush()
    compilation.stdin.close()
    compilation.wait()

    asset = compilation.stdout.read()
    error = compilation.stderr.read()

    if len(asset) > 0:
        return True, asset
    else:
        return False, error

def route_asset(dir_path, extension, compiler, name):
    asset_path = os.path.join(dir_path, '%s.%s' % (name, extension))

    if not os.path.exists(asset_path):
        return abort(404)

    with open(asset_path) as fd:
        success, body = compiler(fd.read())

    if success:
        return Response(body, status=200, content_type='text/css')
    else:
        return Response('<pre>%s</pre>' % body, status=500, content_type='text/html')

@assets_blueprint.route('/stylesheets/<name>.css')
def stylesheets(name):
    dir_path = os.path.join(STATIC_PATH, 'stylesheets')
    sass   = partial(compile_asset, 'sass', ['--trace', '--scss', '--stdin', '-I', dir_path, '--compass'])
    return route_asset(
        dir_path,
        'scss',
        sass,
        name,
    )

@assets_blueprint.route('/javascripts/<name>.js')
def javascripts(name):
    coffee = partial(compile_asset, 'coffee', ['-c', '-s'])
    return route_asset(
        os.path.join(STATIC_PATH, 'javascripts'),
        'coffee',
        coffee,
        name,
    )
