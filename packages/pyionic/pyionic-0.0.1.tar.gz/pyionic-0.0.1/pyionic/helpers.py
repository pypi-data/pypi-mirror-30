import os


def get_envvars():
    """Get Ion Channel token from envvars."""
    if os.environ.get('IONCHANNEL_TOKEN') is not None:
        return os.environ['IONCHANNEL_TOKEN']
    else:
        exit('Ion Channel Token not set')


def get_api_endpoint():
    """Get Ion Channel endpoint from envvars."""
    if os.environ.get('IONCHANNEL_ENDPOINT') is not None:
        return os.environ['IONCHANNEL_ENDPOINT']
    else:
        return 'https://api.ionchannel.io'
