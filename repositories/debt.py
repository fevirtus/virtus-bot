from typing import List, Optional
from models.cmc_debt import CMCDebt
from infra.db import postgres

class DebtRepository:
    def __init__(self):
        self.table = postgres.get_table('cmc_debts')

    async def get(self, name: str) -> Optional[CMCDebt]:
        try:
            response = self.table.select('*').eq('name', name).execute()
            if response.data:
                return CMCDebt(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting debt: {e}")
            return None

    async def upsert_debt(self, name: str, amount: int) -> Optional[CMCDebt]:
        try:
            old = await self.get(name)
            if old:
                new_amount = old.amount + amount
                response = self.table.update({"amount": new_amount}).eq('name', name).execute()
                return CMCDebt(**response.data[0])
            else:
                debt = CMCDebt(id=None, name=name, amount=amount)
                response = self.table.insert(debt.to_dict()).execute()
                return CMCDebt(**response.data[0])
        except Exception as e:
            print(f"Error upserting debt: {e}")
            return None

    async def minus_debt(self, name: str, amount: int) -> Optional[CMCDebt]:
        try:
            old = await self.get(name)
            if old:
                new_amount = max(0, old.amount - amount)
                response = self.table.update({"amount": new_amount}).eq('name', name).execute()
                return CMCDebt(**response.data[0])
            return None
        except Exception as e:
            print(f"Error minusing debt: {e}")
            return None

    async def get_all(self) -> List[CMCDebt]:
        try:
            response = self.table.select('*').execute()
            return [CMCDebt(**debt) for debt in response.data]
        except Exception as e:
            print(f"Error getting all debts: {e}")
            return [] 