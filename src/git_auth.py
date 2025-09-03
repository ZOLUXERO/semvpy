import os
import re
from urllib.parse import quote, urlparse
from logger import logger


class AuthenticationError(Exception):
    pass


def detect_auth_method():
    # TODO: validate azure devops configuration
    # and usage, it may differ from the others
    tokens = [
        ('GH_TOKEN', 'github'),
        ('GITHUB_TOKEN', 'github'),
        ('GL_TOKEN', 'gitlab'),
        ('GITLAB_TOKEN', 'gitlab'),
        ('BB_TOKEN', 'bitbucket'),
        ('BITBUCKET_TOKEN', 'bitbucket'),
        ('AZURE_DEVOPS_EXT_PAT', 'azure_devops'),
        ('GIT_CREDENTIALS', 'generic'),
    ]

    for env_key, service in tokens:
        token = os.environ.get(env_key)
        if token:
            return service, token

    return None, None


def format_auth_url(remote: str, service: str, token: str) -> str:
    url = remote.split('://')
    if (service == 'github'
            or service == 'gitlab'
            or service == 'bitbucket'
            or service == 'azure_devops'):
        return f'{url[0]}://{token}@{url[1]}'

    if service == 'generic':
        user_info = token.split(":", 1)
        u_enc = quote(user_info[0])
        p_enc = quote(user_info[1])
        return f'{url[0]}://{u_enc}:{p_enc}@{url[1]}'


def validate_ssh_keys() -> bool:
    ssh_keys = [os.path.expanduser(
        '~/.ssh/id_rsa'), os.path.expanduser('~/.ssh/id_ed25519')]
    for key in ssh_keys:
        if os.path.exists(key):
            return True

    return False


def remote_contains_credentials(remote: str) -> bool:
    # alternative ?????
    # pattern = r"(?<=https:\/\/).+:.+(?=@)"
    # credentials = re.search(pattern, remote)
    parsed = urlparse(remote)
    return bool(parsed.username and parsed.password)


def authenticate_url(remote: str) -> str:
    if remote.startswith('git@'):
        logger.debug('Url has format ssh')
        return remote

    if remote_contains_credentials(remote):
        logger.info('URL contains credentials')
        return remote

    service, token = detect_auth_method()
    if service and token:
        remote_url = format_auth_url(remote, service, token)
        logger.debug('Url has normal format')
        return remote_url

    logger.warning('Remote url could not be authenticated and formated')
    raise AuthenticationError("Auth failed for remote repository")
