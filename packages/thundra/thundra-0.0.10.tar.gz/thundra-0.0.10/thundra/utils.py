import os

from thundra import constants


def get_thundra_apikey():
    return os.environ['thundra_apiKey'] if 'thundra_apiKey' in os.environ else None


def is_thundra_trace_disabled():
    return os.environ['thundra_trace_disable'] if 'thundra_trace_disable' in os.environ else ''


def is_thundra_lambda_publish_cloudwatch_enabled():
    return os.environ['thundra_lambda_publish_cloudwatch_enable'] if 'thundra_lambda_publish_cloudwatch_enable' in os.environ else 'false'


def is_thundra_lambda_audit_request_skipped():
    return os.environ['thundra_lambda_audit_request_skip'] if 'thundra_lambda_audit_request_skip' in os.environ else ''


def is_thundra_lambda_audit_response_skipped():
    return os.environ['thundra_lambda_audit_response_skip'] if 'thundra_lambda_audit_response_skip' in os.environ else ''


def get_thundra_application_profile():
    return os.environ['thundra_applicationProfile'] if 'thundra_applicationProfile' in os.environ else ''


def get_aws_lambda_log_stream():
    return os.environ['AWS_LAMBDA_LOG_STREAM_NAME'] if 'AWS_LAMBDA_LOG_STREAM_NAME' in os.environ else None


def get_aws_lambda_function_version():
    return os.environ['AWS_LAMBDA_FUNCTION_VERSION'] if 'AWS_LAMBDA_FUNCTION_VERSION' in os.environ else ""


def get_aws_region():
    return os.environ['AWS_REGION'] if 'AWS_REGION' in os.environ else ""


def format_date(date_to_be_formatted):
    date = date_to_be_formatted.strftime(constants.DATE_FORMAT)
    # make ms 3 digits
    ms = date[20:-6]
    formatted_date = date.replace(ms, ms[:-3])
    return formatted_date