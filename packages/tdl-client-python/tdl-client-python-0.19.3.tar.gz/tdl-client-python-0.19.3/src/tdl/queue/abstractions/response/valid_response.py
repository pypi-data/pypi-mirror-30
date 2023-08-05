from tdl.util import Util


class ValidResponse:

    def __init__(self, id_, result, client_action):
        self.id = id_
        self.result = result
        self.client_action = client_action

    def get_audit_text(self):
        return 'resp = {0}'.format(Util.compress_text(self.result))
