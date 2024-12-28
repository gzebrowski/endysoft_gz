import logging

from .settings import *  # noqa

logger = logging.getLogger(__name__)

TESTING = True

try:
    from .local_test_settings import *  # noqa
except ImportError as err2:
    logger.debug(str(err2))
else:
    try:
        apply_test_globals(globals())  # noqa
    except NameError:
        pass
