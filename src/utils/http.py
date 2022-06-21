from typing import Callable, TypeVar, Union

from core.error import Error
from requests import Response  # type: ignore

T = TypeVar("T")


def decode_http_response(
    req: Union[Response, Response], decode_fn: Callable[[dict], T]
) -> Union[Error, T]:
    status_code = req.status_code
    if status_code == 200:
        return decode_fn(req.json())
    else:
        return Error(req.json())
