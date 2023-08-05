import os
from tdl.runner.runner_action import RunnerActions


CHALLENGES_FOLDER = 'challenges'
LAST_FETCHED_ROUND_PATH = '{}/XR.txt'.format(CHALLENGES_FOLDER)


class RoundManagement:

    @staticmethod
    def save_description(listener, raw_description, audit_stream, working_directory):
        if "\n" not in raw_description:
            return

        newline_index = raw_description.find("\n")
        round_id = raw_description[:newline_index]
        last_fetched_round = RoundManagement.get_last_fetched_round(working_directory)

        if not round_id == last_fetched_round:
            listener.on_new_round(round_id, RunnerActions.get_new_round_description.short_name)

        RoundManagement.display_and_save_description(round_id, raw_description, audit_stream, working_directory)

    @staticmethod
    def display_and_save_description(label, description, audit_stream, working_directory):
        challenges_path = os.path.join(working_directory, CHALLENGES_FOLDER)

        if not os.path.exists(challenges_path):
            os.makedirs(challenges_path)

        description_file_name = '{}.txt'.format(label)
        description_file_path = os.path.join(challenges_path, description_file_name)

        with open(description_file_path, "w+") as output:
            output.write(description)

        audit_stream.log("Challenge description saved to file: {}/{}.".format(CHALLENGES_FOLDER, description_file_name))

        with open(os.path.join(challenges_path, "XR.txt"), "w+") as output:
            output.write(label)

    @staticmethod
    def get_last_fetched_round(working_directory):
        try:
            with open(os.path.join(working_directory, LAST_FETCHED_ROUND_PATH), 'r') as round_file:
                return round_file.read().replace('\n', '')
        except:
            return "noRound"
