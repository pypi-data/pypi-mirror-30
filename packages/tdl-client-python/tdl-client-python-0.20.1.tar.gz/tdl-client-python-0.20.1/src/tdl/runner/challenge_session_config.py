from tdl.audit.stdout_audit_stream import StdoutAuditStream


class ChallengeSessionConfig:

    def __init__(self, journey_id):
        self._hostname = None
        self._port = 8222
        self._use_colours = True
        self._recording_system_should_be_on = True
        self._journey_id = journey_id
        self._audit_stream = StdoutAuditStream
        self._working_directory = './'

    @staticmethod
    def for_journey(journey_id):
        return ChallengeSessionConfig(journey_id)

    def with_server_hostname(self, hostname):
        self._hostname = hostname
        return self

    def with_port(self, port):
        self._port = port
        return self

    def with_colours(self, use_colours):
        self._use_colours = use_colours
        return self

    def with_recording_system_should_be_on(self, recording_system_should_be_on):
        self._recording_system_should_be_on = recording_system_should_be_on
        return self

    def with_audit_stream(self, audit_stream):
        self._audit_stream = audit_stream
        return self

    def with_working_directory(self, working_directory):
        self._working_directory = working_directory
        return self

    def get_recording_system_should_be_on(self):
        return self._recording_system_should_be_on

    def get_hostname(self):
        return self._hostname

    def get_port(self):
        return self._port

    def get_journey_id(self):
        return self._journey_id

    def get_use_colours(self):
        return self._use_colours

    def get_audit_stream(self):
        return self._audit_stream

    def get_working_directory(self):
        return self._working_directory
