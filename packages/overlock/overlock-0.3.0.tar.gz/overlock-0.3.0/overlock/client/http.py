import json
import logging
import time

from .worker import http_queue, http_kill_signal

# pylint: disable=wrong-import-position
import six

if six.PY2:
    # pylint: disable=import-error, no-name-in-module
    from urlparse import urlunparse
    from Queue import Full
else:
    from urllib.parse import urlunparse # pylint: disable=import-error, no-name-in-module
    from queue import Full # pylint: disable=import-error

from .base import BaseClient
from overlock.state import client_state
from overlock import __version__ as lib_version

logger = logging.getLogger(__name__)

# Info added to all requests
STD_INFO = {
    "library": "python",
    "version": lib_version,
}

class OverlockRequestsClient(BaseClient):
    """Connects to the agent over an http socket
    """

    def __init__(self):
        self._msg_queue = http_queue

    def _construct(self, vals):
        vals.update(STD_INFO)
        return json.dumps(vals, cls=client_state.serialiser)

    def _queue_message(self, location, data):
        if http_kill_signal.is_set():
            return
        try:
            http_queue.put_nowait((location, data))
        except Full:
            http_queue.get()
            self._queue_message(location, data)

    def _send_message(self, path, vals, node_id):
        location = self._loc(path, node_id)
        data = self._construct(vals)
        self._queue_message(location, data)

    def _loc(self, path, node_id):
        netloc = "{}:{}".format(client_state.agent_host, client_state.agent_port)
        path = "/api/v1/{}/{}".format(path.lstrip("/"), client_state.process_name)
        query = "node_id={:s}".format(node_id) if node_id else None

        return urlunparse(("http", netloc, path, None, query, None))

    def update_state(self, new_state, node_id=None):
        self._send_message(
            "/state",
            {
                "state": new_state
            },
            node_id,
        )

    def update_metadata(self, new_metadata, node_id=None):
        self._send_message(
            "/metadata",
            {
                "metadata": new_metadata
            },
            node_id,
        )

    def lifecycle_event(self, key_type, comment, node_id=None):
        self._send_message(
            "/lifecycle",
            {
                "type": key_type,
                "comment": comment,
            },
            node_id,
        )

    def post_log(self, log_data, node_id=None):
        self._send_message(
            "/log",
            {
                "logs": [
                    log_data,
                ]
            },
            node_id,
        )
