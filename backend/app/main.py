from fastapi import FastAPI, Request
import httpx
import logging

app = FastAPI(title="LLM-Guard Proxy")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm-guard")

UPSTREAM_URL = "https://httpbin.org"


@app.get("/")
async def health_check():
    return {
        "service": "LLM-Guard",
        "status": "running"
    }


@app.api_route(
    "/proxy/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"]
)
async def proxy(request: Request, path: str):

    target_url = f"{UPSTREAM_URL}/{path}"

    body = await request.body()

    logger.info(
        "Request: %s %s",
        request.method,
        target_url
    )

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            content=body,
            headers={
                key: value
                for key, value in request.headers.items()
                if key.lower() != "host"
            }
        )

    logger.info(
        "Response: %s",
        response.status_code
    )

    return {
        "status_code": response.status_code,
        "upstream_response": response.text
    }
