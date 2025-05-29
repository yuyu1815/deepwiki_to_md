"""
Error Handling Utilities for DeepWiki to Markdown Converter

This module provides error handling utility functions for the DeepWiki to Markdown converter.
"""

import logging
import sys
import traceback
import requests
from typing import Optional, Callable, Any

from deepwiki_to_md.utils.localization import get_localized_message

logger = logging.getLogger(__name__)


def setup_error_handling() -> None:
    """
    Set up global error handling.
    
    This function sets up global exception handlers and other error handling mechanisms.
    """

    # Set up sys.excepthook to log uncaught exceptions
    def exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Let KeyboardInterrupt pass through
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Log the exception
        logger.critical(
            get_localized_message("uncaught_exception"),
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = exception_handler
    logger.debug("Global error handling set up")


def handle_request_error(error: requests.RequestException, url: str) -> None:
    """
    Handle a request error.
    
    Args:
        error (requests.RequestException): The request exception
        url (str): The URL that caused the error
    """
    if isinstance(error, requests.ConnectionError):
        logger.error(get_localized_message("connection_error", url=url))
    elif isinstance(error, requests.Timeout):
        logger.error(get_localized_message("timeout_error", url=url))
    elif isinstance(error, requests.HTTPError):
        status_code = error.response.status_code if error.response else "unknown"
        logger.error(get_localized_message("http_error", url=url, status_code=status_code))
    else:
        logger.error(get_localized_message("request_error", url=url, error=str(error)))


def retry_on_exception(
        func: Callable,
        max_retries: int = 3,
        retry_delay: int = 2,
        exceptions: tuple = (requests.RequestException,),
        on_retry: Optional[Callable[[Exception, int], None]] = None
) -> Callable:
    """
    Decorator to retry a function on exception.
    
    Args:
        func (Callable): Function to retry
        max_retries (int): Maximum number of retries
        retry_delay (int): Delay between retries in seconds
        exceptions (tuple): Exceptions to catch and retry on
        on_retry (Optional[Callable[[Exception, int], None]]): Function to call on retry
        
    Returns:
        Callable: Wrapped function
    """
    import time

    def wrapper(*args, **kwargs):
        last_exception = None

        for retry in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e

                if retry < max_retries:
                    if on_retry:
                        on_retry(e, retry + 1)
                    else:
                        logger.warning(
                            get_localized_message(
                                "retry_attempt",
                                function=func.__name__,
                                retry=retry + 1,
                                max_retries=max_retries,
                                error=str(e)
                            )
                        )

                    # Wait before retrying
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        get_localized_message(
                            "max_retries_exceeded",
                            function=func.__name__,
                            max_retries=max_retries,
                            error=str(e)
                        )
                    )

        # If we get here, all retries failed
        raise last_exception

    return wrapper


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log the execution time of a function.
    
    Args:
        func (Callable): Function to log execution time for
        
    Returns:
        Callable: Wrapped function
    """
    import time

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        logger.debug(
            get_localized_message(
                "execution_time",
                function=func.__name__,
                time=end_time - start_time
            )
        )

        return result

    return wrapper
