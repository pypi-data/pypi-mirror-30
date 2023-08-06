from datetime import datetime, timezone
import uuid

import thundra.utils as utils


class TracePlugin:
    #TODO: make 1.0.0
    data_format_version = '0.0.1'
    IS_COLD_START = True

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.start_time = 0
        self.end_time = 0
        aws_lambda_log_stream = utils.get_aws_lambda_log_stream()
        self.log_stream = aws_lambda_log_stream.split("]")[1] if aws_lambda_log_stream is not None else ''
        self.application_version = utils.get_aws_lambda_function_version()
        self.application_profile = utils.get_thundra_application_profile()
        self.aws_region = utils.get_aws_region()
        self.trace_data = {}

    def before_invocation(self, data):
        context = data['context']
        event = data['event']

        context_id = str(uuid.uuid4())
        self.start_time = datetime.now(timezone.utc)
        formatted_date = utils.format_date(self.start_time)
        self.trace_data = {
            'id': str(uuid.uuid4()),
            'applicationName': context.function_name,
            'applicationId': self.log_stream,
            'applicationVersion': self.application_version,
            'applicationProfile': self.application_profile,
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
                'request': event if data['request_skipped'] is not True else None,
                'response': {},
                'coldStart': 'true' if TracePlugin.IS_COLD_START else 'false',
                'functionRegion': self.aws_region,
                'functionMemoryLimitInMB': context.memory_limit_in_mb
            }

        }
        TracePlugin.IS_COLD_START = False

    def after_invocation(self, data):
        if 'error' in data:
            error = data['error']
            error_type = type(error)
            exception = {
                'errorType': error_type.__name__,
                'errorMessage': str(error),
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
        formatted_date = utils.format_date(self.end_time)
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



