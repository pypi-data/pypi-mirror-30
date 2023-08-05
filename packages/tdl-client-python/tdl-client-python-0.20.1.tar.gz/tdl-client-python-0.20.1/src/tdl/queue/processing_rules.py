from tdl.queue.abstractions.processing_rule import ProcessingRule
from tdl.queue.abstractions.response.fatal_error_response import FatalErrorResponse
from tdl.queue.abstractions.response.valid_response import ValidResponse


class ProcessingRules:

    def __init__(self):
        self._rules = {}

    def add(self, method_name, user_implementation, client_action):
        self._rules[method_name] = ProcessingRule(user_implementation, client_action)

    def on(self, method_name):
        return ProcessingRulesBuilder(self, method_name)

    def get_response_for(self, request):
        if request.method not in self._rules:
            return FatalErrorResponse("method '{0}' did not match any processing rule".format(request.method))

        processing_rule = self._rules[request.method]

        try:
            result = processing_rule.user_implementation(*request.params)
            return ValidResponse(request.id, result, processing_rule.client_action)
        except Exception as e:
            print(e.message)
            return FatalErrorResponse('user implementation raised exception')


class ProcessingRulesBuilder:

    def __init__(self, instance, method_name):
        self._instance = instance
        self._method_name = method_name
        self._user_implementation = None

    def call(self, user_implementation):
        self._user_implementation = user_implementation
        return self

    def then(self, client_action):
        self._instance.add(self._method_name, self._user_implementation, client_action)
