import logging

from overlock import errors
from overlock.client import OverlockRequestsClient
from overlock.state import client_state
from overlock.client.base import BaseClient
from .base import LogMixin

logger = logging.getLogger(__name__)


class OverlockLogger(LogMixin, BaseClient):
    def __init__(self, client_type=OverlockRequestsClient):
        super(OverlockLogger, self).__init__()

        cmds = [
            "update_state",
            "update_metadata",
            "lifecycle_event",
            "post_log"
        ]

        self._client = client_type()

        for c in cmds:
            setattr(self, c, getattr(self, "_" + c))

    def _check_node_id(self, kwargs):
        if "node_id" not in kwargs:
            # pylint: disable=protected-access
            kwargs.update(node_id=client_state._node_id)

        if kwargs.get("node_id"):
            if not isinstance(kwargs["node_id"], str):
                raise errors.InvalidNodeIdError

    def _update_state(self, new_state, **kwargs):
        self._check_node_id(kwargs)
        self._client.update_state(new_state, **kwargs)

    def _update_metadata(self, new_metadata, **kwargs):
        self._check_node_id(kwargs)
        self._client.update_metadata(new_metadata, **kwargs)

    def _lifecycle_event(self, key_type, comment, **kwargs):
        self._check_node_id(kwargs)
        self._client.lifecycle_event(key_type, comment, **kwargs)

    def _post_log(self, log_data, **kwargs):
        self._check_node_id(kwargs)
        self._client.post_log(log_data, **kwargs)
