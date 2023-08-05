from tdl.runner.challenge_server_client import ChallengeServerClient,ClientErrorException,OtherCommunicationException,ServerErrorException
from tdl.runner.recording_system import RecordingSystem
from tdl.runner.round_management import RoundManagement


class ChallengeSession:

    @staticmethod
    def for_runner(runner):
        return ChallengeSession(runner)

    def __init__(self, runner):
        self._runner = runner
        self._config = None
        self._audit_stream = None
        self._user_input_callback = None
        self._recording_system = None
        self._challenge_server_client = None

    def with_config(self, config):
        self._config = config
        self._audit_stream = config.get_audit_stream()
        return self

    def with_action_provider(self, callback):
        self._user_input_callback = callback
        return self

    def start(self):
        self._recording_system = RecordingSystem(self._config.get_recording_system_should_be_on())

        if not self._recording_system.is_recording_system_ok():
            self._audit_stream.log('Please run `record_screen_and_upload` before continuing.')
            return

        self._audit_stream.log('Connecting to {}'.format(self._config.get_hostname()))
        self.run_app()

    def run_app(self):
        self._challenge_server_client = ChallengeServerClient(
            self._config.get_hostname(),
            self._config.get_port(),
            self._config.get_journey_id(),
            self._config.get_use_colours())

        try:
            should_continue = self.check_status_of_challenge()
            if should_continue:
                user_input = self._user_input_callback()
                self._audit_stream.log('Selected action is: {}'.format(user_input))
                round_description = self.execute_user_action(user_input)
                RoundManagement.save_description(
                    self._recording_system,
                    round_description,
                    self._audit_stream,
                    self._config.get_working_directory())

        except ClientErrorException as e:
            self._audit_stream.log(e)
        except ServerErrorException:
            self._audit_stream.log('Server experienced an error. Try again in a few minutes.')
        except OtherCommunicationException:
            self._audit_stream.log('Client threw an unexpected error. Try again.')

    def check_status_of_challenge(self):
        journey_progress = self._challenge_server_client.get_journey_progress()
        self._audit_stream.log(journey_progress)

        available_actions = self._challenge_server_client.get_available_actions()
        self._audit_stream.log(available_actions)

        return 'No actions available.' not in available_actions

    def execute_user_action(self, user_input):
        if user_input == 'deploy':
            self._runner.run()
            last_fetched_round = RoundManagement.get_last_fetched_round(self._config.get_working_directory())
            self._recording_system.deploy_notify_event(last_fetched_round)

        return self.execute_action(user_input)

    def execute_action(self, user_input):
        action_feedback = self._challenge_server_client.send_action(user_input)
        self._audit_stream.log(action_feedback)
        return self._challenge_server_client.get_round_description()
