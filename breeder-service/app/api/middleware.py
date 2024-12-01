from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
import time
from fastapi import Request
from app.api.auth import verify_jwt_token
from fastapi.exceptions import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("breeder-service")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log before the request is processed
        logger.info(f"Request started: {request.method} {request.url}")

        # Log query parameters (for debugging purposes)
        logger.info(f"Query parameters: {request.query_params}")

        start_time = time.time()

        # Call the next middleware or route handler
        response = await call_next(request)

        # Log after the response is generated
        process_time = time.time() - start_time
        logger.info(
            f"Request completed in {process_time:.4f} seconds with status code {response.status_code}"
        )

        return response


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_paths: list[str] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or []

    async def dispatch(self, request: Request, call_next):
        # Exclude paths from middleware
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)

        try:
            # Check for Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(
                    status_code=401, detail="Authorization header is missing"
                )

            # Check if it is a Bearer token
            if not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=401, detail="Invalid Authorization header format"
                )

            # Extract the token
            token = auth_header.split("Bearer ")[1]

            # Validate the token using the custom function
            if not verify_jwt_token(token):
                raise HTTPException(status_code=401, detail="Invalid or expired token")

            # Proceed to the next middleware or route handler
            response = await call_next(request)
            return response

        except HTTPException as http_exc:
            # Handle HTTPException explicitly and return a JSON response
            return JSONResponse(
                status_code=http_exc.status_code,
                content={"detail": http_exc.detail},
            )
        except Exception as exc:
            # Handle unexpected exceptions and return a 500 response
            return JSONResponse(
                status_code=500,
                content={"detail": "An internal server error occurred"},
            )
