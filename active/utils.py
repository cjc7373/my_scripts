import logging
from typing import Any, Optional, Union

import requests

logger = logging.getLogger(__name__)


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r


__session = requests.Session()


def set_github_token(token: str) -> None:
    """
    If token not set, fetching Github API may have usage limits
    """
    __session.auth = BearerAuth(token=token)


def fetch_github_api(
    method: str, path: str, data: Optional[Union[list, dict]] = None
) -> Any:
    """
    We are using requests.Session (which utilizes utllib3's connection pool) to improve performance
    """
    res = __session.request(method, f"https://api.github.com/{path}", json=data)
    if not res.ok:
        logger.error(f"Previous request not succeeded.")
        logger.error(f"Request url: {res.request.url}\nbody: {res.request.body}")
        logger.error(f"Response body: {res.content.decode()}")
    res.raise_for_status()
    return res.json()
