import logging
from fastapi import Request

logger = logging.getLogger("uvicorn")

async def log_request(request: Request):
    logger.info(f"Request: {request.method} {request.url}")

# GDPR: Audit logs should be retained for 1 year, access restricted to admin/auditor roles.
