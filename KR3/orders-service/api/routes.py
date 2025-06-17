import os
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from pydantic import BaseModel
from uuid import UUID, uuid4
from typing import List
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.order import Order, OrderStatus
from models.schema import get_sessionmaker
from config import settings

router = APIRouter()

TESTING = os.getenv("TESTING", "").lower() in ("1", "true", "yes")


class OrderCreateRequest(BaseModel):
    amount: float

class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    amount: float
    status: OrderStatus


async def get_session() -> AsyncSession:
    Session, _ = get_sessionmaker(settings.database_url)
    async with Session() as session:
        yield session

async def get_user_id(x_user_id: UUID = Header(..., alias="X-User-Id")) -> UUID:
    return x_user_id


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    req: OrderCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_user_id)
):
    # 1) Сохранение в БД
    new_order = Order(id=uuid4(), user_id=user_id, amount=req.amount)
    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)

    if not TESTING:
        try:
            payload = {
                "aggregate_id": str(new_order.id),
                "payload": {"user_id": str(user_id), "amount": float(req.amount)}
            }
            await request.app.state.kafka_producer.send(
                settings.orders_topic,
                payload,
                key=str(new_order.id).encode("utf-8"),
            )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to publish order_created: {e}")

    return new_order


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    session: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_user_id)
):
    result = await session.execute(select(Order).where(Order.user_id == user_id))
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
