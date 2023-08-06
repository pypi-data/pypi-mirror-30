import os
import sys


def get_token():
    """Get Ion Channel token from envvars."""
    try:
        return os.environ['IONCHANNEL_SECRET_KEY']
    except KeyError:
        sys.exit('Ion Channel Token not set')


def get_api_endpoint():
    """Get Ion Channel endpoint from envvars."""
    if os.environ.get('IONCHANNEL_ENDPOINT_URL') is not None:
        return os.environ['IONCHANNEL_ENDPOINT_URL']
    else:
        return 'https://api.ionchannel.io'
