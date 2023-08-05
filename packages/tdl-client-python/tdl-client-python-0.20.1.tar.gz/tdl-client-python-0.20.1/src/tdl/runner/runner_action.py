class RunnerAction:
    def __init__(self, short_name, name, client_action):
        self.short_name = short_name
        self.name = name
        self.client_action = client_action


class RunnerActions:

    get_new_round_description = RunnerAction("new", "get_new_round_description", "stop")
    deploy_to_production = RunnerAction("deploy", "deploy_to_production", "publish")

    all = [
        get_new_round_description,
        deploy_to_production,
    ]
