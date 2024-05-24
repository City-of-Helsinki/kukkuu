import logging
from functools import wraps
from threading import Thread
from typing import Optional

logger = logging.getLogger(__name__)


def execute_in_background(
    thread_name: Optional[str] = None, daemonic: Optional[bool] = None
):
    """A decorator to execute a function in a new thread in background.

    Args:
        daemonic (Optional[bool], optional): Set a new thread as daemonic.
            If not None, daemon explicitly sets whether the thread is daemonic.
            If None, the daemonic property is inherited from the current thread.
            Defaults to None.
    """

    def decorator(target_function):
        @wraps(target_function)
        def start_thread(*args, **kwargs):
            logger.debug("Creating a new thread to execute a function in background...")
            thread = Thread(
                name=thread_name,
                target=target_function,
                args=args,
                kwargs=kwargs,
                daemon=daemonic,
            )
            logger.info(f"Starting a thread [{thread}].")
            thread.start()

        return start_thread

    return decorator
