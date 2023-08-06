import re

def status():
    print('SQL Sanitizer is working fine')


def is_sanitized(data):
    if isinstance(data, list):
        is_array_sanitized(data)

    if isinstance(data, dict):
        is_map_sanitized(data)

    if isinstance(data, str):
        is_string_sanitized(data)


def is_array_sanitized(data):
    _ = [is_sanitized(d) for d in data]


def is_map_sanitized(data):
    _ = [is_sanitized(value) for key, value in data.items()]


def is_string_sanitized(data):
    sanitized_string = re.sub('[\'";]', '', data)
    if len(data) != len(sanitized_string):
        raise Exception('Input contains un sanitized characters')