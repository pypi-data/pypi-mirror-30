from datetime import datetime, timezone
import uuid
import os

from thundra import constants


class TracePlugin:

    data_format_version = '0.0.1'

    def __init__(self):
        self.data = {}
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.start_time = 0
        self.end_time = 0
        self.trace_data = {}

    def before_invocation(self, data):
        context = data['context']
        event = data['event']

        context_id = str(uuid.uuid4())
        self.start_time = datetime.now(timezone.utc)
        date = self.start_time.strftime(constants.DATE_FORMAT)
        #make ms 3 digits
        ms = date[20:-6]
        formatted_date = date.replace(ms, ms[:-3])
        self.trace_data = {
            'id': str(uuid.uuid4()),
            'applicationName': context.function_name,
            'applicationId': os.environ['AWS_LAMBDA_LOG_STREAM_NAME'].split("]")[1],
            'applicationVersion': os.environ['AWS_LAMBDA_FUNCTION_VERSION'],
            'applicationProfile': os.environ['thundra_applicationProfile'] if 'thundra_applicationProfile' in os.environ else "",
            'applicationType': 'python',
            'duration': None,
            'startTime': formatted_date,
            'endTime': None,
            'errors': [],
            'thrownError': None,
            'contextType': 'ExecutionContext',
            'contextName': context.function_name,
            'contextId': context_id,
            'auditInfo': {
                'contextName': context.function_name,
                'id': context_id,
                'openTime': formatted_date,
                'closeTime': None,
                'errors': [],
                'thrownError': None
            },
            'properties': {
                'request': event,
                'response': {},
                'coldStart': 'true' if constants.IS_COLD_START else 'false',
                'functionRegion': os.environ['AWS_REGION'],
                'functionMemoryLimitInMB': context.memory_limit_in_mb
            }

        }
        constants.IS_COLD_START = False

    def after_invocation(self, data):
        if 'error' in data:
            error = data['error']
            error_type = type(error)
            exception = {
                'error': error_type.__name__,
                'args': error.args,
                'cause': error.__cause__
            }
            self.trace_data['errors'].append(error_type.__name__)
            self.trace_data['thrownError'] = error_type.__name__
            self.trace_data['auditInfo']['errors'].append(exception)
            self.trace_data['auditInfo']['thrownError'] = exception

        if 'response' in data:
            self.trace_data['properties']['response'] = data['response']
        self.end_time = datetime.now(timezone.utc)
        duration = self.end_time - self.start_time
        duration_in_ms = duration.total_seconds() * 1000
        self.trace_data['duration'] = int(duration_in_ms)
        date = self.end_time.strftime(constants.DATE_FORMAT)
        # make ms 3 digits
        ms = date[20:-6]
        formatted_date = date.replace(ms, ms[:-3])
        self.trace_data['endTime'] = formatted_date
        self.trace_data['auditInfo']['closeTime'] = formatted_date

        reporter = data['reporter']
        report_data = {
            'apiKey': reporter.api_key,
            'type': 'AuditData',
            'dataFormatVersion': TracePlugin.data_format_version,
            'data': self.trace_data
        }
        reporter.add_report(report_data)
        reporter.send_report()



