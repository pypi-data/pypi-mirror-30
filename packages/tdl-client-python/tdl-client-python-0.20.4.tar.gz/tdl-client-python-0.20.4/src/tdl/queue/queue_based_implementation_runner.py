import datetime
import time
from tdl.queue.processing_rules import ProcessingRules
from tdl.queue.actions.publish_action import PublishAction
from tdl.queue.transport.remote_broker import RemoteBroker


class QueueBasedImplementationRunner:

    def __init__(self, config, deploy_processing_rules):
        self._config = config
        self._deploy_processing_rules = deploy_processing_rules
        self._audit = QueueBasedImplementationRunnerAudit(config.get_audit_stream())
        self.total_processing_time_millis = None

    def run(self):
        start_time = datetime.datetime.now()

        try:
            self._audit.log_line('Starting client')

            remote_broker = RemoteBroker(
                self._config.get_hostname(),
                self._config.get_port(),
                self._config.get_unique_id(),
                self._config.get_time_to_wait_for_request())

            self._audit.log_line('Waiting for requests')

            remote_broker.subscribe(ApplyProcessingRules(self._deploy_processing_rules, self._audit), self._audit)

            # DEBT - this is just to block.
            while remote_broker.is_connected():
                time.sleep(0.1)

            self._audit.log_line('Stopping client')
        except Exception as e:
            self._audit.log_exception('There was a problem processing messages', e)

        end_time = datetime.datetime.now()

        self.total_processing_time_millis = (end_time - start_time).total_seconds() * 1000.00

    def get_request_timeout_millis(self):
        return self._config.get_time_to_wait_for_request()


class QueueBasedImplementationRunnerAudit:

    def __init__(self, audit_stream):
        self._audit_stream = audit_stream
        self._lines = []

        self.start_line()

    def start_line(self):
        self._lines[:] = []

    def log(self, auditable):
        text = auditable.get_audit_text()
        self._lines.append(text)

    def end_line(self):
        text = ', '.join(self._lines)
        self._audit_stream.log(text)

    def log_exception(self, message, e):
        self.start_line()
        self._lines.append('{0}: {1}'.format(message, str(e)))
        self.end_line()

    def log_line(self, text):
        self.start_line()
        self._lines.append(text)
        self.end_line()


class QueueBasedImplementationRunnerBuilder:

    def __init__(self):
        self._deploy_processing_rules = ProcessingRules()
        self._config = None

        self._deploy_processing_rules.\
            on('display_description').\
            call(lambda *_: 'OK').\
            then(PublishAction)

    def set_config(self, config):
        self._config = config
        return self

    def with_solution_for(self, method_name, user_implementation, action = PublishAction):
        self._deploy_processing_rules.\
            on(method_name).\
            call(user_implementation).\
            then(action)
        return self

    def create(self):
        return QueueBasedImplementationRunner(self._config, self._deploy_processing_rules)


class ApplyProcessingRules:

    def __init__(self, processing_rules, audit):
        self._processing_rules = processing_rules
        self._audit = audit

    def process_next_request_from(self, remote_broker, headers, request):
        self._audit.start_line()
        self._audit.log(request)

        response = self._processing_rules.get_response_for(request)
        self._audit.log(response)

        client_action = response.client_action
        self._audit.log(client_action)

        self._audit.end_line()

        client_action.after_response(remote_broker, headers, response)

        return client_action.prepare_for_next_request(remote_broker)
