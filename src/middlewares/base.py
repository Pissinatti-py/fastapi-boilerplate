from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class BaseCustomMiddleware(BaseHTTPMiddleware):
    """
    Base middleware that can be extended for any custom logic.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Logic before the request
        response = await call_next(request)
        # Logic after the request
        return response
