import logging
import time
import uuid
from fastapi import Request

logger = logging.getLogger("app")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    # Don't log sensitive bodies
    logger.info(
        f"request_id={request_id} method={request.method} path={request.url.path} status={response.status_code} duration_ms={duration_ms}"
    )
    response.headers["X-Request-ID"] = request_id
    return response
