from typing import List, Optional
from datetime import datetime
from models.debt_group import HomeMember, Expense, ExpenseShare
from infra.db import postgres

class HomeDebtRepository:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HomeDebtRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not HomeDebtRepository._initialized:
            self.db = postgres.get_table('home_members')
            HomeDebtRepository._initialized = True

    async def add_member(self, discord_user_id: int, name: str) -> HomeMember:
        """Thêm thành viên mới vào nhà"""
        data = await self.db.table("home_members").insert({
            "discord_user_id": discord_user_id,
            "name": name
        }).execute()
        return HomeMember(**data.data[0])

    async def get_member(self, discord_user_id: int) -> Optional[HomeMember]:
        """Lấy thông tin thành viên theo discord_user_id"""
        data = await self.db.table("home_members").select("*").eq("discord_user_id", discord_user_id).execute()
        if not data.data:
            return None
        return HomeMember(**data.data[0])

    async def get_all_members(self) -> List[HomeMember]:
        """Lấy danh sách tất cả thành viên"""
        data = await self.db.table("home_members").select("*").execute()
        return [HomeMember(**member) for member in data.data]

    async def add_expense(self, amount: float, description: str, paid_by: int) -> Expense:
        """Thêm khoản chi tiêu mới"""
        # Tạo expense
        expense_data = await self.db.table("expenses").insert({
            "amount": amount,
            "description": description,
            "paid_by": paid_by
        }).execute()
        expense = Expense(**expense_data.data[0])

        # Lấy danh sách thành viên
        members = await self.get_all_members()
        share_amount = amount / len(members)

        # Tạo expense shares cho từng thành viên
        for member in members:
            await self.db.table("expense_shares").insert({
                "expense_id": expense.id,
                "member_id": member.discord_user_id,
                "share_amount": share_amount,
                "is_paid": member.discord_user_id == paid_by  # Người trả tiền được đánh dấu là đã trả
            }).execute()

        return expense

    async def get_expense(self, expense_id: int) -> Optional[Expense]:
        """Lấy thông tin khoản chi tiêu"""
        data = await self.db.table("expenses").select("*").eq("id", expense_id).execute()
        if not data.data:
            return None
        return Expense(**data.data[0])

    async def get_all_expenses(self) -> List[Expense]:
        """Lấy danh sách tất cả khoản chi tiêu"""
        data = await self.db.table("expenses").select("*").order("created_at", desc=True).execute()
        return [Expense(**expense) for expense in data.data]

    async def get_expense_shares(self, expense_id: int) -> List[ExpenseShare]:
        """Lấy danh sách chia tiền của một khoản chi tiêu"""
        data = await self.db.table("expense_shares").select("*").eq("expense_id", expense_id).execute()
        return [ExpenseShare(**share) for share in data.data]

    async def mark_share_as_paid(self, share_id: int) -> Optional[ExpenseShare]:
        """Đánh dấu một phần chia tiền đã được trả"""
        data = await self.db.table("expense_shares").update({
            "is_paid": True
        }).eq("id", share_id).execute()
        if not data.data:
            return None
        return ExpenseShare(**data.data[0])

    async def get_member_balance(self, discord_user_id: int) -> float:
        """Tính số dư của một thành viên (số tiền phải trả - số tiền đã trả)"""
        # Lấy tất cả expense shares của thành viên
        data = await self.db.table("expense_shares").select("*").eq("member_id", discord_user_id).execute()
        shares = [ExpenseShare(**share) for share in data.data]

        # Tính tổng số tiền phải trả
        total_owed = sum(share.share_amount for share in shares)
        
        # Tính tổng số tiền đã trả
        total_paid = sum(share.share_amount for share in shares if share.is_paid)

        return total_owed - total_paid 