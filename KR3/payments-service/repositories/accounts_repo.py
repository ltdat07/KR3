from sqlalchemy.ext.asyncio import AsyncSession
from models.account import Account
from sqlalchemy import select, update

class AccountsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, account: Account):
        self.session.add(account)
        await self.session.flush()
        return account

    async def get(self, user_id):
        q = select(Account).where(Account.user_id == user_id)
        res = await self.session.execute(q)
        return res.scalar_one_or_none()

    async def update_balance(self, user_id, amount):
        q = (
            update(Account)
            .where(Account.user_id == user_id)
            .values(balance=Account.balance + amount)
            .returning(Account)
        )
        res = await self.session.execute(q)
        await self.session.commit()
        return res.scalar_one()
