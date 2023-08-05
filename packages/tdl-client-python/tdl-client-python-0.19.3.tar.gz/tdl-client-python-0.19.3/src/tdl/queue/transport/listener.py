from stomp import ConnectionListener
from tdl.queue.abstractions.request import Request


class Listener(ConnectionListener):
    def __init__(self, remote_broker, handling_strategy, start_timer, stop_timer, audit):
        self._remote_broker = remote_broker
        self._handling_strategy = handling_strategy
        self._start_timer = start_timer
        self._stop_timer = stop_timer
        self._audit = audit

    def on_message(self, headers, message_json):
        self._stop_timer()
        self._handling_strategy.process_next_request_from(
            self._remote_broker,
            headers,
            Request.deserialize(message_json, self._audit))
        self._start_timer()
