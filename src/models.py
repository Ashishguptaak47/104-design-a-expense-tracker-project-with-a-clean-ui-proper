from dataclasses import dataclass
from typing import Optional
from datetime import datetime

CATEGORIES = ["Food", "Transport", "Utilities", "Entertainment", "Health", "Shopping", "Other"]


@dataclass
class Expense:
    title: str
    amount: float
    category: str
    date: str  # YYYY-MM-DD
    notes: str = ""
    id: Optional[int] = None

    def validate(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty.")
        if self.amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if self.category not in CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(CATEGORIES)}")
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")
