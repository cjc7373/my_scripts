import logging
import os
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


def set_github_token(token: Optional[str] = None) -> None:
    """
    get token from parameter or env variable GITHUB_TOKEN
    If token not set, fetching Github API may have usage limits
    """
    if not token:
        token = os.environ.get("GITHUB_TOKEN")
    print(f"Github token is: {token}")
    if token:
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
        logger.error(f"Request url: {res.request.url}\nbody: {res.request.body!r}")
        logger.error(f"Response body: {res.content.decode()}")
    res.raise_for_status()
    return res.json()
