class PublishAndStopAction:

    @staticmethod
    def get_audit_text():
        return ''

    @staticmethod
    def after_response(remote_broker, headers, response):
        remote_broker.respond_to(headers, response)

    @staticmethod
    def prepare_for_next_request(remote_broker):
        remote_broker.stop()
