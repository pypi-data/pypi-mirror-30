""" Utility functions.
"""

from edw.logger.config import LOG_USER_ID
from edw.logger.config import LOG_USER_IP


def get_user_type(name):
    return 'Anonymous' if name == 'Anonymous User' else 'Authenticated'


def _get_ip(request):
    environ = getattr(request, 'environ', {})

    if "HTTP_X_FORWARDED_FOR" in environ:
        return environ.get('HTTP_X_FORWARDED_FOR')

    if 'REMOTE_ADDR' in environ:
        return environ.get('REMOTE_ADDR')

    return environ.get('HTTP_HOST', None)


def _get_user_id(request):
    if request is None:
        request = {}
    user = request.get('AUTHENTICATED_USER', None)
    return getattr(user, 'getUserName', lambda: 'unknown')()


# If user id or user ip logging is disabled,
# return the disabled message directly.
get_ip = _get_ip if LOG_USER_IP else lambda _: 'ip log disabled'
get_user_id = _get_user_id if LOG_USER_ID else lambda _: 'user log disabled'


def get_request_data(request):
    if request is not None:
        user_id = get_user_id(request)
        ip = get_ip(request)
        # Bypass LOG_USER_ID option in this case, we want to know if the
        # user is authenticated or not.
        user_type = get_user_type(_get_user_id(request))
        url = request.get('URL', 'NO_URL')

    else:
        user_id = ip = user_type = url = 'NO_REQUEST'

    action = getattr(url, 'split', lambda sep: [''])('/')[-1]
    return dict(
        user=user_id,
        ip=ip,
        user_type=user_type,
        url=url,
        action=action
    )
