import os
import sys


def get_envvars():
    """Get Ion Channel token from envvars."""
    if os.environ.get('IONCHANNEL_SECRET_KEY') is not None:
        return os.environ['IONCHANNEL_SECRET_KEY']
    else:
        print('Ion Channel Token not set')
        sys.exit(1)


def get_api_endpoint():
    """Get Ion Channel endpoint from envvars."""
    if os.environ.get('IONCHANNEL_ENDPOINT_URL') is not None:
        return os.environ['IONCHANNEL_ENDPOINT_URL']
    else:
        return 'https://api.ionchannel.io'
