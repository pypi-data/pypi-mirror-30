from functools import wraps
import sys

import requests
import click

from cis_client import exception

CONTEXT_SETTINGS = dict(auto_envvar_prefix='CIS_CLIENT')


def add_auth_options(func):
    @click.option('--brand-id', type=click.STRING, help='Brand Id')
    @click.option('--account-id', type=click.STRING, help='Account Id')
    @click.option('--group-id', type=click.STRING, help='Group Id')
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def add_host_options(func):
    @click.option('--aaa-host', required=True, type=click.STRING, help='AAA hostname.')
    @click.option('--north-host', required=True, type=click.STRING, help='CIS North hostname.')
    @click.option('--south-host', type=click.STRING, help='CIS South hostname.')
    @click.option('--insecure', type=click.BOOL, default=False,
                  help='Allow insecure server connections when using SSL')
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def add_credentials_options(func):
    @click.option('--username', required=True, type=click.STRING, help='AAA username.')
    @click.option('--password', required=True, type=click.STRING, help='AAA password.')
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except requests.HTTPError as e:
            print "Error: {}, reason: {}".format(str(e), e.response.text)
            sys.exit(1)
        except (exception.OptionException, exception.UploadConflictException) as e:
            print "Error:", e.message
            sys.exit(1)
        except Exception as e:
            raise
    return wrapper


def get_source_file_list_from_kwargs(**kwargs):
    split_values = lambda comma_separated_values: map(str.strip, map(str, comma_separated_values.split(',')))
    if kwargs.get('source_file_list') is not None and kwargs.get('source_file') is not None:
        raise exception.OptionException("Please specify only one option --source-file-list or --source-file")
    paths = []
    if kwargs.get('source_file_list') is not None:
        with open(kwargs['source_file_list']) as f:
            file_content = f.read()
        paths = map(str.strip, file_content.strip().split('\n'))
    if kwargs.get('source_file') is not None:
        paths = split_values(kwargs['source_file'])

    return paths
