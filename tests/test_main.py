import os
import pytest
from src.models import Expense
from src.database import DatabaseManager


@pytest.fixture
def db():
    db_mgr = DatabaseManager(":memory:")
    yield db_mgr


def test_expense_validation():
    # Valid expense
    e = Expense(title="Groceries", amount=45.5, category="Food", date="2023-10-01", notes="Weekly food")
    e.validate()  # Should not raise exception

    # Invalid amount
    with pytest.raises(ValueError, match="Amount must be greater than zero"):
        Expense(title="Groceries", amount=-10, category="Food", date="2023-10-01").validate()

    # Invalid date
    with pytest.raises(ValueError, match="Date must be in YYYY-MM-DD format"):
        Expense(title="Groceries", amount=10, category="Food", date="10/01/2023").validate()

    # Invalid category
    with pytest.raises(ValueError, match="Invalid category"):
        Expense(title="Groceries", amount=10, category="Space Travel", date="2023-10-01").validate()


def test_database_crud(db):
    exp = Expense(title="Coffee", amount=4.50, category="Food", date="2023-10-15")
    exp_id = db.add_expense(exp)
    assert exp_id == 1

    expenses = db.get_all_expenses()
    assert len(expenses) == 1
    assert expenses[0].title == "Coffee"
    assert expenses[0].amount == 4.50

    # Test summary
    stats = db.get_summary_stats()
    assert stats["total_spent"] == 4.50
    assert stats["by_category"]["Food"] == 4.50

    # Test deletion
    deleted = db.delete_expense(exp_id)
    assert deleted is True
    assert len(db.get_all_expenses()) == 0


def test_budget_management(db):
    db.set_budget("Food", 200.0)
    budgets = db.get_budgets()
    assert budgets.get("Food") == 200.0

    with pytest.raises(ValueError):
        db.set_budget("Food", -50.0)
