import sys
from src.database import DatabaseManager
from src.gui import ExpenseTrackerApp


def main():
    db_manager = DatabaseManager("expenses.db")
    app = ExpenseTrackerApp(db_manager=db_manager)
    app.mainloop()


if __name__ == "__main__":
    main()
