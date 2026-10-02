"""Money calculations independent of Discord and the database."""
from decimal import Decimal, InvalidOperation
import re
from typing import Dict, Iterable, List, Tuple

MAX_AMOUNT = 1_000_000_000_000
MAX_MEMBERS = 25


def parse_amount(value: str) -> int:
    """Accept whole dong or a k suffix (600000, 600k, 150.5k)."""
    text = value.strip().lower()
    if not re.fullmatch(r"[0-9]+(?:[.,][0-9]+)?k|[0-9]+", text):
        raise ValueError("Nhập tiền như 600000 hoặc 600k (đơn vị đồng).")
    try:
        amount = Decimal(text[:-1].replace(',', '.')) * 1000 if text.endswith('k') else Decimal(text)
    except InvalidOperation:
        raise ValueError("Số tiền không hợp lệ.")
    if amount != amount.to_integral_value() or not 0 < amount <= MAX_AMOUNT:
        raise ValueError("Số tiền phải là số nguyên từ 1 đến 1.000.000.000.000 ₫.")
    return int(amount)


def money(amount: int) -> str:
    return f"{amount:,}".replace(',', '.') + " ₫"


def validate_amount(amount: int) -> None:
    if isinstance(amount, bool) or not isinstance(amount, int) or not 0 < amount <= MAX_AMOUNT:
        raise ValueError("Số tiền không hợp lệ.")


def split_shares(amount: int, participants: Iterable[int]) -> Dict[int, int]:
    validate_amount(amount)
    members = list(participants)
    if not members or len(members) > MAX_MEMBERS or len(set(members)) != len(members):
        raise ValueError("Chọn từ 1 đến 25 thành viên khác nhau.")
    members.sort()
    quotient, remainder = divmod(amount, len(members))
    return {user_id: quotient + (index < remainder) for index, user_id in enumerate(members)}


def expense_deltas(amount: int, payer: int, participants: Iterable[int]) -> Dict[int, int]:
    deltas = {user_id: -share for user_id, share in split_shares(amount, participants).items()}
    deltas[payer] = deltas.get(payer, 0) + amount
    return deltas


def payment_deltas(amount: int, sender: int, recipient: int, balances: Dict[int, int]) -> Dict[int, int]:
    validate_amount(amount)
    if sender == recipient:
        raise ValueError("Không thể ghi trả tiền cho chính mình.")
    maximum = min(max(0, -balances.get(sender, 0)), max(0, balances.get(recipient, 0)))
    if maximum == 0:
        raise ValueError("Bạn phải đang cần trả và người nhận phải đang được nhận trong sổ nhóm.")
    if amount > maximum:
        raise ValueError(f"Khoản trả vượt số nợ hiện tại. Tối đa {money(maximum)}.")
    return {sender: amount, recipient: -amount}


def settlements(balances: Dict[int, int]) -> List[Tuple[int, int, int]]:
    if sum(balances.values()) != 0:
        raise ValueError("Sổ nợ không cân bằng.")
    debtors = sorted([(uid, -value) for uid, value in balances.items() if value < 0], key=lambda x: (-x[1], x[0]))
    creditors = sorted([(uid, value) for uid, value in balances.items() if value > 0], key=lambda x: (-x[1], x[0]))
    result = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        sender, debt = debtors[i]
        recipient, credit = creditors[j]
        amount = min(debt, credit)
        result.append((sender, recipient, amount))
        debtors[i] = (sender, debt - amount)
        creditors[j] = (recipient, credit - amount)
        i += debt == amount
        j += credit == amount
    return result
