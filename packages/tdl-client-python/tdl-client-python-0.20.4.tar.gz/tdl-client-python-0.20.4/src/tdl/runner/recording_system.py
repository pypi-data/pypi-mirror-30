import unirest
from tdl.runner.runner_action import RunnerActions


RECORDING_SYSTEM_ENDPOINT = "http://localhost:41375"


class RecordingSystem:

    def __init__(self, recording_required):
        self._recording_required = recording_required

    def is_recording_system_ok(self):
        return RecordingSystem.is_running() if self._recording_required else True

    @staticmethod
    def is_running():
        try:
            response = unirest.get("{}/status".format(RECORDING_SYSTEM_ENDPOINT))

            if response.code == 200 and response.body.startswith("OK"):
                return True
        except Exception as e:
            print("Could not reach recording system: {}".format(str(e)))

        return False

    def notify_event(self, last_fetched_round, action_name):
        print('Notify round "{}", event "{}"'.format(last_fetched_round, action_name))

        if not self.is_recording_system_ok():
            return

        try:
            response = unirest.post("{}/notify".format(RECORDING_SYSTEM_ENDPOINT),
                                    params="{}/{}".format(last_fetched_round, action_name))

            if response.code != 200:
                print("Recording system returned code: {}".format(response.code))
                return

            if not response.body.startswith("ACK"):
                print("Recording system returned body: {}".format(response.body))

        except Exception as e:
            print("Could not reach recording system: {}".format(str(e)))

    def on_new_round(self, round_id, short_name):
        self.notify_event(round_id, short_name)

    def deploy_notify_event(self, last_fetched_round):
        self.notify_event(last_fetched_round, RunnerActions.deploy_to_production.short_name)
