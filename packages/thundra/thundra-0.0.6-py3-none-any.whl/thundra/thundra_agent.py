from functools import wraps
import os

from thundra.plugins.trace.trace_plugin import TracePlugin
from thundra.reporter import Reporter


class Thundra:
    def __init__(self, api_key=None, disable_trace=False):

        self.plugins = []
        print(os.environ)
        self.api_key = os.environ['thundra_apiKey'] if 'thundra_apiKey' in os.environ else api_key
        if self.api_key is None:
            raise Exception('Please set thundra_apiKey from environment variables in order to use Thundra')
        self.data = {}

        disable_trace_by_env = os.environ['thundra_trace_disable'] if 'thundra_trace_disable' in os.environ else ""
        if self.should_enable_plugin(disable_trace_by_env, disable_trace):
            self.plugins.append(TracePlugin())

        self.reported = False
        self.reporter = Reporter(self.api_key)

    def __call__(self, original_func):
        @wraps(original_func)
        def wrapper(event, context):
            self.data['reporter'] = self.reporter
            self.data['event'] = event
            self.data['context'] = context
            self.execute_hook('before:invocation', self.data)
            try:
                response = original_func(event, context)
                self.data['response'] = response
            except Exception as e:
                self.data['error'] = e
                raise e
            self.execute_hook('after:invocation', self.data)
            return response

        return wrapper

    call = __call__

    def should_enable_plugin(self, disable_by_env, disable_by_param=False):
        if disable_by_env == 'true':
            return False
        elif disable_by_env == 'false':
            return True
        else:
            return not disable_by_param

    def execute_hook(self, name, data):
        return [plugin.hooks[name](data) for plugin in self.plugins if hasattr(plugin, 'hooks') and name in plugin.hooks]

