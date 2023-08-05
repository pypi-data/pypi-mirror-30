import requests
import json
import logging

log = logging.getLogger(__name__)

class YadageHTTPController():
    def __init__(self, server, deserialize = True, deserialization_opts = None):
        self.server = server
        self.deserialize = deserialize
        self.deserializer = False
        self.deserialization_opts = deserialization_opts

    @property
    def adageobj(self):
        if not self.deserialize:
            log.warning('python-level access to workflow object disabled; pass deserialize=True option to enable.')
            return None
        if not self.deserializer:
            from yadage.wflowstate import make_deserializer
            self.deserializer = make_deserializer(self.deserialization_opts)
        return self.deserializer(self.state())

    def state(self):
        state = requests.get(self.server + '/state').json()
        return state


    def applicable_rules(self):
        return requests.get(self.server + '/ctrl/read/applicable_rules').json()

    def submittable_nodes(self):
        return requests.get(self.server + '/ctrl/read/submittable_nodes').json()

    def undo_rules(self, ruleids):
        requests.post(
            self.server + '/ctrl/write/undo_rules',
            headers = {'Content-Type': 'application/json'},
            data = json.dumps({'ruleids': ruleids})
        )

    def apply_rules(self, ruleids):
        requests.post(
            self.server + '/ctrl/write/apply_rules',
            headers = {'Content-Type': 'application/json'},
            data = json.dumps({'ruleids': ruleids})
        )

    def submit_nodes(self, nodeids):
        requests.post(
            self.server + '/ctrl/write/submit_nodes',
            headers = {'Content-Type': 'application/json'},
            data = json.dumps({'nodeids': nodeids})
        )

    def reset_nodes(self, nodeids):
        requests.post(
            self.server + '/ctrl/write/reset_nodes',
            headers = {'Content-Type': 'application/json'},
            data = json.dumps({'nodeids': nodeids})
        )

    def finished(self):
        return requests.get(self.server + '/ctrl/read/finished').json()

    def validate(self):
        return requests.get(self.server + '/ctrl/read/validate').json()

    def successful(self):
        return requests.get(self.server + '/ctrl/read/successful').json()
