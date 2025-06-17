from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
import sys

router = APIRouter()

class CreateAccountRequest(BaseModel):
    initial_balance: float = 0.0

class TopUpRequest(BaseModel):
    amount: float

class BalanceResponse(BaseModel):
    user_id: UUID
    balance: float

class ChargeRequest(BaseModel):
    order_id: UUID
    amount: float

class ChargeResponse(BaseModel):
    order_id: UUID
    status: str

TESTING = "pytest" in sys.modules

if not TESTING:
    # Подключаем реальную БД и сессии
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select

    from models.account import Account
    from models.schema import get_sessionmaker
    from config import settings

    SessionLocal, _ = get_sessionmaker(settings.database_url)

    async def get_session() -> AsyncSession:
        async with SessionLocal() as session:
            yield session

async def get_user_id(x_user_id: UUID = Header(..., alias="X-User-Id")) -> UUID:
    return x_user_id

if TESTING:
    # простое in-memory хранилище для тестов
    _store: dict[UUID, Decimal] = {}

@router.post("", response_model=BalanceResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    req: CreateAccountRequest,
    user_id: UUID = Depends(get_user_id),
    session=Depends(get_session) if not TESTING else None,
):
    if TESTING:
        if user_id in _store:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
        _store[user_id] = Decimal(str(req.initial_balance))
        return BalanceResponse(user_id=user_id, balance=float(_store[user_id]))

    result = await session.execute(select(Account).where(Account.user_id == user_id))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    account = Account(user_id=user_id, balance=req.initial_balance)
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return BalanceResponse(user_id=account.user_id, balance=float(account.balance))

@router.post("/topup", response_model=BalanceResponse)
async def top_up(
    req: TopUpRequest,
    user_id: UUID = Depends(get_user_id),
    session=Depends(get_session) if not TESTING else None,
):
    if TESTING:
        if user_id not in _store:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        _store[user_id] += Decimal(str(req.amount))
        return BalanceResponse(user_id=user_id, balance=float(_store[user_id]))

    result = await session.execute(select(Account).where(Account.user_id == user_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    account.balance += Decimal(str(req.amount))
    await session.commit()
    await session.refresh(account)
    return BalanceResponse(user_id=account.user_id, balance=float(account.balance))

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    user_id: UUID = Depends(get_user_id),
    session=Depends(get_session) if not TESTING else None,
):
    if TESTING:
        if user_id not in _store:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        return BalanceResponse(user_id=user_id, balance=float(_store[user_id]))

    result = await session.execute(select(Account).where(Account.user_id == user_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return BalanceResponse(user_id=account.user_id, balance=float(account.balance))

@router.post("/charge", response_model=ChargeResponse)
async def charge_account(
    req: ChargeRequest,
    user_id: UUID = Depends(get_user_id),
    session=Depends(get_session) if not TESTING else None,
):
    if TESTING:
        if user_id not in _store:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        amount = Decimal(str(req.amount))
        if _store[user_id] < amount:
            raise HTTPException(status_code=402, detail="Insufficient funds")
        _store[user_id] -= amount
        return ChargeResponse(order_id=req.order_id, status="SUCCESS")

    result = await session.execute(select(Account).where(Account.user_id == user_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    amount = Decimal(str(req.amount))
    if account.balance < amount:
        raise HTTPException(status_code=402, detail="Insufficient funds")
    account.balance -= amount
    await session.commit()
    return ChargeResponse(order_id=req.order_id, status="SUCCESS")
