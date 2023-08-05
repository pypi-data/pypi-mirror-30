from tdl.audit.stdout_audit_stream import StdoutAuditStream


class ImplementationRunnerConfig:

    def __init__(self):
        self._port = 61613
        self._request_timeout_millis = 500
        self._audit_stream = StdoutAuditStream
        self._hostname = None
        self._unique_id = None

    def set_hostname(self, hostname):
        self._hostname = hostname
        return self

    def set_port(self, port):
        self._port = port
        return self

    def set_unique_id(self, unique_id):
        self._unique_id = unique_id
        return self

    def set_time_to_wait_for_request(self, time_to_wait_for_request):
        self._request_timeout_millis = time_to_wait_for_request
        return self

    def set_audit_stream(self, audit_stream):
        self._audit_stream = audit_stream
        return self

    def get_hostname(self):
        return self._hostname

    def get_port(self):
        return self._port

    def get_unique_id(self):
        return self._unique_id

    def get_time_to_wait_for_request(self):
        return self._request_timeout_millis

    def get_audit_stream(self):
        return self._audit_stream
