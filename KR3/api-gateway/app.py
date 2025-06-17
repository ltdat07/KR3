import os
from fastapi import FastAPI, HTTPException, Response, Request
import httpx

app = FastAPI(title="API Gateway")

ORDERS_URL = os.getenv("ORDERS_URL", "http://orders-service:8001")
PAYMENTS_URL = os.getenv("PAYMENTS_URL", "http://payments-service:8002")

@app.get("/health")
async def health():
    return {"status": "ok"}

# — Orders —
@app.post("/orders")
async def create_order(request: Request, payload: dict):
    user_id = request.headers.get("X-User-Id")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ORDERS_URL}/orders", json=payload,
            headers={"X-User-Id": user_id}
        )
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type")
    )

@app.get("/orders")
async def list_orders(request: Request):
    user_id = request.headers.get("X-User-Id")
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{ORDERS_URL}/orders",
            headers={"X-User-Id": user_id}
        )
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

@app.get("/orders/{order_id}")
async def get_order(order_id: str, request: Request):
    user_id = request.headers.get("X-User-Id")
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{ORDERS_URL}/orders/{order_id}",
            headers={"X-User-Id": user_id}
        )
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

# — Payments —
@app.post("/accounts")
async def create_account(request: Request, payload: dict):
    user_id = request.headers.get("X-User-Id")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PAYMENTS_URL}/accounts", json=payload,
            headers={"X-User-Id": user_id}
        )
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

@app.post("/accounts/topup")
async def top_up(request: Request, payload: dict):
    user_id = request.headers.get("X-User-Id")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PAYMENTS_URL}/accounts/topup", json=payload,
            headers={"X-User-Id": user_id}
        )
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

@app.get("/accounts/balance")
async def get_balance(request: Request):
    user_id = request.headers.get("X-User-Id")
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{PAYMENTS_URL}/accounts/balance",
            headers={"X-User-Id": user_id}
        )
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

@app.post("/accounts/charge")
async def charge_account(request: Request, payload: dict):
    user_id = request.headers.get("X-User-Id")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PAYMENTS_URL}/accounts/charge", json=payload,
            headers={"X-User-Id": user_id}
        )
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))
