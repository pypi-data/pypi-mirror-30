import json
from stomp import Connection
from threading import Timer
from collections import OrderedDict
from tdl.queue.transport.listener import Listener


class RemoteBroker:
    def __init__(self, hostname, port, unique_id, request_timeout_millis):
        hosts = [(hostname, port)]
        connect_timeout = 10
        self.conn = Connection(host_and_ports=hosts, timeout=connect_timeout)
        self.conn.start()
        self.conn.connect(wait=True)
        self.unique_id = unique_id
        self.request_timeout_millis = request_timeout_millis
        self._timer = None

    def acknowledge(self, headers):
        self.conn.ack(headers['message-id'], headers['subscription'])

    def publish(self, response):
        self.conn.send(
                body=json.dumps(response, separators=(',', ':')),
                destination='{}.resp'.format(self.unique_id)
        )

    def subscribe(self, handling_strategy, audit):
        listener = Listener(self, handling_strategy, self.start_timer, self.stop_timer, audit)
        self.conn.set_listener('listener', listener)
        self.conn.subscribe(
                destination='{}.req'.format(self.unique_id),
                id=1,
                ack='client-individual'
        )
        self.start_timer()

    def respond_to(self, headers, response):
        self.acknowledge(headers)
        self.publish(OrderedDict([
            ('result', response.result),
            ('error', None),
            ('id', response.id)
        ]))

    def stop(self):
        self.conn.unsubscribe(1)
        self.conn.remove_listener('listener')

    def close(self):
        self.conn.disconnect()

    def is_connected(self):
        return self.conn.is_connected()

    def stop_timer(self):
        if self._timer is not None:
            self._timer.cancel()

    def start_timer(self):
        self._timer = Timer(self.request_timeout_millis / 1000.00, self.close)
        self._timer.start()
