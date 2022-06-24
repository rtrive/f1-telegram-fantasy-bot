from enum import Enum
from typing import TypeVar, Callable, Optional, Union

import requests

from core.error import Error

T = TypeVar('T')


class HTTPMethod(Enum):
    GET = 'GET'
    POST = 'POST'


class HTTPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def make_request(self, method: HTTPMethod, path: str, headers: Optional[dict], decoder: Callable[[dict], T]) -> Union[Error, T]:
        http_response = requests.request(method=method.value, url=f"{self.base_url}{path}", headers=headers if headers else None)
        if http_response.status_code == 200:
            return decoder(http_response.json())
        else:
            return Error(http_response.json())
