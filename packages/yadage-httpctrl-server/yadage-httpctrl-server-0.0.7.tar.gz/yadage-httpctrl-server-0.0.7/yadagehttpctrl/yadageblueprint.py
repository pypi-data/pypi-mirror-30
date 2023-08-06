from flask import Blueprint, jsonify, request
from flask import current_app as app
from gevent.lock import BoundedSemaphore

lock = sem = BoundedSemaphore(1)

blueprint = Blueprint('yadage', __name__)

@blueprint.route('/')
def ui():
    return app.send_static_file('ui.html')

@blueprint.route('/ctrl/read/<method>')
def readmethod(method):
    with sem:
        return jsonify(getattr(app.config['yadage_controller'], method)())

@blueprint.route('/ctrl/write/<method>', methods=['POST'])
def writemethod(method):
    with sem:
        getattr(app.config['yadage_controller'], method)(**request.json)
        return jsonify({'status': 'ok'})

@blueprint.route('/state')
def state():
    with sem:
        return jsonify(app.config['yadage_controller'].adageobj.json())

@blueprint.route('/state/rule/<ruleid>')
def rule(ruleid):
    with sem:
        return jsonify(app.config['yadage_controller'].adageobj.view().getRule(identifier = ruleid).json())

@blueprint.route('/state/node/<nodeid>')
def node(nodid):
    with sem:
        return jsonify(app.config['yadage_controller'].adageobj.view().getNode(identifier = nodeid).json())
