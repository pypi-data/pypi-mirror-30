import json
import logging
import transaction

from datetime import datetime

from ZODB.Connection import Connection

from edw.logger.util import get_request_data
from edw.logger.decorators import log_errors

from edw.logger.config import logger
from edw.logger.config import LOG_DB


def __after_conn_close(request_data):

    @log_errors("Cannot log transaction commit.")
    def on_close():
        url = request_data['url']
        logger.info(json.dumps({
            "IP": request_data['ip'],
            "User": request_data['user'],
            "Date": datetime.now().isoformat(),
            "URL": url,
            "Action": request_data['action'],
            "Type": 'Commit',
            "LoggerName": logger.name,
        }))

    return on_close


@log_errors("Cannot log transaction commit.")
def handler_commit(event):
    """ Handle ZPublisher.pubevents.PubBeforeCommit.
        This is the only event where we can intercept a
        transaction before it gets committed. Also the only
        event where hooks can be placed and ensure they are
        only executed after a true DB commit.
    """
    if not LOG_DB:
        return

    # get the active transaction
    txn = transaction.get()

    # get needed values now as the request contents will
    # change after commit.
    request = event.request
    request_data = get_request_data(request)

    # transactions that will do a commit have a ZODB.Connection
    # object in ``_resources``. Since the transaction has an
    # open connection we know it will be committed.
    for conn in (c for c in txn._resources if isinstance(c, Connection)):
        # ZODB.Connection objects support callbacks on close.
        # In this case we wrap the callback in another function
        # so we can also pass in the event.
        conn.onCloseCallback(__after_conn_close(request_data))
