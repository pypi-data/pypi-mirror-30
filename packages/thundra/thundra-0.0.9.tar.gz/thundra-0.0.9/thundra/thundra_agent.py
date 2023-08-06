from functools import wraps
import time

from thundra.plugins.trace.trace_plugin import TracePlugin
from thundra.reporter import Reporter

import thundra.utils as utils


class Thundra:
    def __init__(self, api_key=None, disable_trace=False, thundra_lambda_audit_request_skip=False, thundra_lambda_audit_response_skip=False, disable_thundra_lambda_warmup=False):

        self.plugins = []
        api_key_from_environment_variable = utils.get_thundra_apikey()
        self.api_key = api_key_from_environment_variable if api_key_from_environment_variable is not None else api_key
        if self.api_key is None:
            raise Exception('Please set thundra_apiKey from environment variables in order to use Thundra')
        self.data = {}

        disable_trace_by_env = utils.is_thundra_trace_disabled()
        if self.should_enable(disable_trace_by_env, disable_trace):
            self.plugins.append(TracePlugin())

        audit_request_skip_by_env = utils.is_thundra_lambda_audit_request_skipped()
        if self.should_enable(audit_request_skip_by_env, thundra_lambda_audit_request_skip):
            self.data['request_skipped'] = True

        audit_response_skip_by_env = utils.is_thundra_lambda_audit_response_skipped()
        if self.should_enable(audit_response_skip_by_env, thundra_lambda_audit_response_skip):
            self.response_skipped = True

        disable_lambda_warmup_by_env = utils.is_thundra_lambda_warmup_disabled()
        if self.should_enable(disable_lambda_warmup_by_env, disable_thundra_lambda_warmup):
            self.disable_lambda_warmup = True

        self.reporter = Reporter(self.api_key)

    def __call__(self, original_func):
        @wraps(original_func)
        def wrapper(event, context):
            self.data['reporter'] = self.reporter
            self.data['event'] = event
            self.data['context'] = context
            self.execute_hook('before:invocation', self.data)
            try:
                if self.disable_lambda_warmup is not True and self.checkAndHandleWarmupRequest(event):
                    return None
                else:
                    response = original_func(event, context)
                if self.response_skipped is not True:
                    self.data['response'] = response
            except Exception as e:
                self.data['error'] = e
                self.execute_hook('after:invocation', self.data)
                self.reporter.send_report()
                raise e
            self.execute_hook('after:invocation', self.data)
            self.reporter.send_report()
            return response

        return wrapper

    call = __call__

    def should_enable(self, disable_by_env, disable_by_param=False):
        if disable_by_env == 'true':
            return False
        elif disable_by_env == 'false':
            return True
        else:
            return not disable_by_param

    def execute_hook(self, name, data):
        [plugin.hooks[name](data) for plugin in self.plugins if hasattr(plugin, 'hooks') and name in plugin.hooks]

    def checkAndHandleWarmupRequest(event):
        # Check whether it is empty request which is used as default warmup request
        if (not event):
            print("Received warmup request as empty message. " +
                  "Handling with 100 milliseconds delay ...")
            time.sleep(0.1)
            return True
        else:
            if (isinstance(event, str)):
                # Check whether it is warmup request
                if (event.startswith('#warmup')):
                    delayTime = 100
                    args = event[len('#warmup'):].strip().split()
                    # Warmup messages are in '#warmup wait=<waitTime>' format
                    # Iterate over all warmup arguments
                    for arg in args:
                        argParts = arg.split('=')
                        # Check whether argument is in key=value format
                        if (len(argParts) == 2):
                            argName = argParts[0]
                            argValue = argParts[1]
                            # Check whether argument is "wait" argument
                            # which specifies extra wait time before returning from request
                            if (argName == 'wait'):
                                waitTime = int(argValue)
                                delayTime += waitTime
                    print("Received warmup request as warmup message. " +
                          "Handling with " + str(delayTime) + " milliseconds delay ...")
                    time.sleep(delayTime / 1000)
                    return True
            return False


