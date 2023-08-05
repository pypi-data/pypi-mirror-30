import unirest


class ChallengeServerClient:

    def __init__(self, hostname, port, journey_id, use_colours):
        self._journey_id = journey_id
        self._accept_header = 'text/coloured' if use_colours else 'text/not-coloured'
        self._url = "http://{0}:{1}".format(hostname, port)

    def get_journey_progress(self):
        return self.get("journeyProgress")

    def get_available_actions(self):
        return self.get("availableActions")

    def get_round_description(self):
        return self.get("roundDescription")

    def send_action(self, action):
        encoded_path = self.encode(self._journey_id)
        url = "{}/action/{}/{}".format(self._url, action, encoded_path)
        response = unirest.post(url, headers={"Accept": self._accept_header, "Accept-Charset": "UTF-8"})
        self.ensure_status_ok(response)
        return response.body

    def get(self, name):
        journey_id_utf8 = self.encode(self._journey_id)
        url = "{}/{}/{}".format(self._url, name, journey_id_utf8)
        response = unirest.get(url, headers={"Accept": self._accept_header, "Accept-Charset": "UTF-8"})
        self.ensure_status_ok(response)
        return response.body

    def ensure_status_ok(self, response):
        if self.is_client_error(response.code):
            raise ClientErrorException(response.body)
        elif self.is_server_error(response.code):
            raise ServerErrorException(response.body)
        elif self.is_other_error_response(response.code):
            raise OtherCommunicationException(response.body)

    @staticmethod
    def is_client_error(response_status):
        return 400 <= response_status < 500

    @staticmethod
    def is_server_error(response_status):
        return 500 <= response_status < 600

    @staticmethod
    def is_other_error_response(response_status):
        return response_status < 200 or response_status > 300

    @staticmethod
    def encode(text):
        try:
            return unicode(text, 'utf-8')
        except TypeError:
            return text


class ClientErrorException(Exception):
    pass


class ServerErrorException(Exception):
    pass


class OtherCommunicationException(Exception):
    pass
