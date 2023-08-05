from flask import Blueprint, jsonify, request
from flask import current_app as app

blueprint = Blueprint('yadage', __name__)

@blueprint.route('/')
def ui():
    return app.send_static_file('ui.html')

@blueprint.route('/ctrl/read/<method>')
def readmethod(method):
    return jsonify(getattr(app.config['yadage_controller'], method)())

@blueprint.route('/ctrl/write/<method>', methods=['POST'])
def writemethod(method):
    getattr(app.config['yadage_controller'], method)(**request.json)
    return jsonify({'status': 'ok'})

@blueprint.route('/state')
def state():
    return jsonify(app.config['yadage_controller'].adageobj.json())

@blueprint.route('/state/rule/<ruleid>')
def rule(ruleid):
    return jsonify(app.config['yadage_controller'].adageobj.view().getRule(identifier = ruleid).json())

@blueprint.route('/state/node/<nodeid>')
def node(nodid):
    return jsonify(app.config['yadage_controller'].adageobj.view().getNode(identifier = nodeid).json())
