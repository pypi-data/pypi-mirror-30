import six
import time
import logging
import requests
import threading

if six.PY2:
    # pylint: disable=import-error, no-name-in-module
    from Queue import Queue
else:
    from queue import Queue # pylint: disable=import-error

logger = logging.getLogger(__name__)

def _process_queue(signal):
    # global http_queue
    session = requests.Session()
    retry = None

    while True:
        # If the kill signal has been sent we should just try and make our way
        # through the queue as quickly as possible without waiting to retry
        if signal.is_set() and retry is not None:
            retry = None
            http_queue.task_done()
            while not http_queue.empty():
                http_queue.get()
                http_queue.task_done()

        location, data = retry or http_queue.get(True)
        try:
            session.post(
                location,
                data=data,
                headers={"content-type": "application/json"},
            )
            retry = None
        except (requests.Timeout, requests.ConnectionError) as e:
            logger.warning("Error sending message to agent (%s)", repr(e))
            if not signal.is_set():
                time.sleep(1)
                retry = (location, data)
        except Exception: # pylint: disable=broad-except
            logger.exception("Unexpected error message to agent")

        if retry is None:
            http_queue.task_done()

def start_worker():
    if not http_worker.is_alive():
        http_worker.daemon = True
        http_worker.start()

def send_kill_signal():
    http_kill_signal.set()
    http_queue.join()

def unset_kill_signal():
    http_kill_signal.clear()

http_queue = Queue(maxsize=500)
http_kill_signal = threading.Event()
http_worker = threading.Thread(target=_process_queue, name="http_worker", args=(http_kill_signal,))
