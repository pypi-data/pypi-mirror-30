from tdl.queue.actions.stop_action import StopAction


class FatalErrorResponse:

    def __init__(self, message):
        self._message = message
        self.client_action = StopAction

    def get_audit_text(self):
        return 'error = "{0}"'.format(self._message)
