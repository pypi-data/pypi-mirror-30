import json
import time
import inspect

from datetime import datetime

from Products.ZCatalog.ZCatalog import ZCatalog
from zope.globalrequest import getRequest

from edw.logger.util import get_request_data
from edw.logger.decorators import log_errors

from edw.logger.config import logger
from edw.logger.config import LOG_CATALOG
from edw.logger.config import LOG_CATALOG_STACK


old_catalog_object = ZCatalog.catalog_object


@log_errors("Cannot log catalog indexing")
def _log(catalog, obj, uid, idxs, metadata, dt):
    request = getRequest()

    request_data = get_request_data(request)

    log_dict = {
        "IP": request_data['ip'],
        "User": request_data['user'],
        "Date": datetime.now().isoformat(),
        "URL": request_data['url'],
        "Action": request_data['action'],
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
