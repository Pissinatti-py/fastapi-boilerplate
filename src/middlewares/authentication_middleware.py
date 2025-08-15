from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint
)
from starlette.requests import Request
from starlette.responses import Response
from src.services.auth.authentication_service import AuthenticationService


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Base middleware that can be extended for any custom logic.
    """

    authentication_service = AuthenticationService()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Logic before the request

        response = await call_next(request)
        # Logic after the request
        return response
