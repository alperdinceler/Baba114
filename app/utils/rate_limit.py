import logging
import random
import time
from typing import Callable, TypeVar

import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class GoogleApiError(RuntimeError):
    pass


def with_backoff(call: Callable[[], requests.Response]) -> requests.Response:
    settings = get_settings()
    for attempt in range(1, settings.google.max_retries + 1):
        response = call()
        if response.status_code not in {429, 500, 502, 503, 504}:
            return response

        sleep_time = settings.google.backoff_base_s * (2 ** (attempt - 1))
        jitter = random.uniform(0, sleep_time * 0.1)
        logger.warning(
            "Google API rate limited or failed (status=%s). Retry in %.2fs.",
            response.status_code,
            sleep_time + jitter,
        )
        time.sleep(sleep_time + jitter)
    raise GoogleApiError("Google API request failed after retries")
