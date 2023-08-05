import json
import logging
import time
import inspect

from datetime import datetime

from Products.ZCatalog.ZCatalog import ZCatalog
from zope.globalrequest import getRequest

from edw.logger.util import get_user_data
from edw.logger.decorators import log_errors

from edw.logger.config import logger
from edw.logger.config import LOG_CATALOG
from edw.logger.config import LOG_CATALOG_STACK


old_catalog_object = ZCatalog.catalog_object


@log_errors("Cannot log catalog indexing")
def _log(catalog, obj, uid, idxs, metadata, dt):
    request = getRequest()

    url = request.get("URL", None)
    action = getattr(url, 'split', lambda sep: [''])('/')[-1]
    user_data = get_user_data(request)

    log_dict = {
        "IP": user_data['ip'],
        "User": user_data['user'],
        "Date": datetime.now().isoformat(),
        "URL": url,
        "Action": action,
        "Type": 'Catalog',
        "Catalog": catalog.absolute_url(1),
        "Object": uid,
        "Duration": dt,
        "Indexes": idxs,
        "Metadata": metadata,
        "LoggerName": logger.name,
    }

    if LOG_CATALOG_STACK:
        log_dict['Stack'] = [
            '{}({}){}'.format(path, line, func)
            for _, path, line, func, _, _
            in inspect.stack()
        ]

    logger.info(json.dumps(log_dict))


def catalog_object(self, obj, uid=None, idxs=None, update_metadata=1,
                   pghandler=None):
    t_start = time.time()
    old_catalog_object(self, obj, uid, idxs, update_metadata, pghandler)
    dt = time.time() - t_start
    _log(self, obj, uid, idxs, update_metadata, float('{0:.4f}'.format(dt)))


if LOG_CATALOG:
    # avoid re-patching
    if ZCatalog.catalog_object.__code__ != catalog_object.__code__:
        ZCatalog.catalog_object = catalog_object
