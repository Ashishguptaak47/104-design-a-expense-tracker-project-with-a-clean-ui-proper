import sqlite3
from typing import List, Dict, Optional
from src.models import Expense


class DatabaseManager:
    def __init__(self, db_path: str = "expenses.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    notes TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    category TEXT PRIMARY KEY,
                    monthly_limit REAL NOT NULL
                )
            """)
            conn.commit()

    def add_expense(self, expense: Expense) -> int:
        expense.validate()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (title, amount, category, date, notes) VALUES (?, ?, ?, ?, ?)",
                (expense.title.strip(), expense.amount, expense.category, expense.date, expense.notes.strip())
            )
            conn.commit()
            return cursor.lastrowid

    def delete_expense(self, expense_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_all_expenses(self, category_filter: Optional[str] = None) -> List[Expense]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if category_filter and category_filter != "All":
                cursor.execute("SELECT * FROM expenses WHERE category = ? ORDER BY date DESC, id DESC", (category_filter,))
            else:
                cursor.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC")
            
            rows = cursor.fetchall()
            return [
                Expense(
                    id=row["id"],
                    title=row["title"],
                    amount=row["amount"],
                    category=row["category"],
                    date=row["date"],
                    notes=row["notes"]
                ) for row in rows
            ]

    def get_summary_stats(self) -> Dict[str, float]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(amount) as total FROM expenses")
            total_row = cursor.fetchone()
            total = total_row["total"] if total_row and total_row["total"] else 0.0

            cursor.execute("SELECT category, SUM(amount) as cat_total FROM expenses GROUP BY category")
            cat_rows = cursor.fetchall()
            by_category = {row["category"]: row["cat_total"] for row in cat_rows}

            return {
                "total_spent": total,
                "by_category": by_category
            }

    def set_budget(self, category: str, limit_amount: float) -> None:
        if limit_amount <= 0:
            raise ValueError("Budget limit must be greater than zero.")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO budgets (category, monthly_limit) VALUES (?, ?)", (category, limit_amount))
            conn.commit()

    def get_budgets(self) -> Dict[str, float]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM budgets")
            return {row["category"]: row["monthly_limit"] for row in cursor.fetchall()}
