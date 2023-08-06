from gevent import monkey
monkey.patch_all()

import os
import time
import logging
log = logging.getLogger(__name__)

import socketio

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler


sio = socketio.Server(logger=True, async_mode='gevent')

import click
from flask import Flask, jsonify, request

import pkg_resources



static_path = pkg_resources.resource_filename('yadagehttpctrl', 'static')
app = Flask('yadagectrl',static_folder=static_path)

sio = socketio.Server(logger=True, async_mode='gevent')
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)


def init_app(app, statetype, stateopts, backendstring, backendopts = None):
    from yadage.wflowstate import load_model_fromstring
    from yadage.utils import setupbackend_fromstring
    from yadage.controllers import PersistentController
    model      = load_model_fromstring(statetype,stateopts)
    backend    = setupbackend_fromstring(backendstring, backendopts)
    app.config['yadage_controller'] = PersistentController(model,backend)
    app.config['yadage_controller'].sync_backend()
    from yadageblueprint import blueprint

    app.register_blueprint(blueprint)

def watch_state(state):
    lastmod = None
    while True:
        try:
            path = state.split(':')[-1]
            old = lastmod
            lastmod = os.path.getmtime(path)
            if lastmod > old:
                log.info('lastmod %s', lastmod)
                log.info('send!')
                sio.emit('sync', room='yadage', namespace='/yadage')
        except:
            log.exception('keeping background thread alive')
        time.sleep(1.0)

@sio.on('join', namespace='/yadage')
def join_room(sid,data):
    sio.enter_room(sid, 'yadage', namespace='/yadage')

@click.command()
@click.argument('statetype')
@click.argument('backend')
@click.option('-l', '--modelopt', multiple=True, default=None, help = 'options for the workflow state models')
@click.option('--ip', default = '0.0.0.0', help = 'host ip on which to server')
@click.option('--port', default = 8000, help = 'port on which to server')
def serve(statetype, backend, modelopt, ip ,port):
    from yadage.utils import options_from_eqdelimstring
    logging.basicConfig(level = logging.INFO)
    stateopts  = options_from_eqdelimstring(modelopt)
    backendopts = {}
    init_app(app, statetype, stateopts, backend, backendopts)

    sio.start_background_task(lambda: watch_state(statetype))
    pywsgi.WSGIServer(('0.0.0.0', port), app,
                      handler_class = WebSocketHandler,
                      ).serve_forever()
