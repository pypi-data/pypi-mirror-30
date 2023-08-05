from .state import client_state
from .logger.impl import OverlockLogger
from .client.worker import send_kill_signal, start_worker

import sys
import logging

logger = logging.getLogger(__name__)

def install(process_name="unknown", metadata=None, serialiser=None, agent_host='127.0.0.1', agent_port='6837'):
    """Initialise client state

    This sets up the client library so that it can begin to interact with the
    overlock daemon

    Args:
        process_name (str): Name of process
        metadata (dict, optional): Any initial metadata
        serialiser (optional): Custom JSON serialiser for sending messages
        agent_host (optional): Host adress for sending messages to the agent.
            Defaults to 127.0.0.1. Can optionally include the port (e.g.
            127.0.0.1:8000)
        agent_port (optional): Port for sending messages to the agent. Defaults
            to 6837. If there is a conflict between agent_host and agent_port,
            the port specified in agent_host takes priority
    """
    client_state.process_name = process_name
    client_state.serialiser = serialiser
    client_state.metadata = metadata

    host = agent_host.split(':')
    client_state.agent_host = host[0]
    client_state.agent_port = host[1] if len(host) == 2 else agent_port

    ol = OverlockLogger()

    def handle_exception(*args):
        if issubclass(args[0], KeyboardInterrupt):
            sys.__excepthook__(*args)
            return

        ol.error(str(args[1]), exc_info=args)
        send_kill_signal()
        sys.__excepthook__(*args)

    sys.excepthook = handle_exception

    start_worker()
