import click
from flask import Flask, jsonify, request

import pkg_resources



static_path = pkg_resources.resource_filename('yadagehttpctrl', 'static')
app = Flask('yadagectrl',static_folder=static_path)
app.debug = True

def init_app(app, statetype, stateopts, backendstring):
    from yadage.wflowstate import load_model_fromstring
    from yadage.utils import setupbackend_fromstring
    from yadage.controllers import PersistentController
    model      = load_model_fromstring(statetype,stateopts)
    backend    = setupbackend_fromstring(backendstring)
    app.config['yadage_controller'] = PersistentController(model,backend)

    from yadageblueprint import blueprint

    app.register_blueprint(blueprint)

@click.command()
@click.argument('statetype')
@click.argument('backend')
@click.option('-l', '--modelopt', multiple=True, default=None, help = 'options for the workflow state models')
@click.option('--ip', default = '0.0.0.0', help = 'host ip on which to server')
@click.option('--port', default = 8000, help = 'port on which to server')
def serve(statetype, backend, modelopt, ip ,port):
    from yadage.utils import options_from_eqdelimstring


    stateopts  = options_from_eqdelimstring(modelopt)
    init_app(app, statetype, stateopts, backend)

    app.run(host=ip, port=port)

if __name__ == '__main__':
    serve()
