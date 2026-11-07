# Expense Tracker

A modern, lightweight desktop Expense Tracker written in Python using `tkinter` for UI and `sqlite3` for local data persistence.

## Features
- 📊 **Dashboard Summary**: Real-time spending breakdown and budget health.
- 📝 **Transaction Logging**: Easily record expenses with date, category, amount, and notes.
- 🔍 **Filtering & Export**: Filter transactions by category and export data to CSV.
- 🎯 **Budget Management**: Set spending limits per category and monitor spending relative to targets.
- 📁 **Clean Architecture**: Modular code separation with data models, SQLite storage layer, and GUI components.

## Requirements
- Python 3.8+
- Standard Python packages (`tkinter`, `sqlite3`, `csv`, `dataclasses` are included in standard library)
- `pytest` (optional, for running automated tests)

## Quick Start
1. Run the application:
   ```bash
   python main.py
   ```
2. Run unit tests:
   ```bash
   pytest tests/
   ```

## Structure
- `main.py`: Entry point for launching the GUI application.
- `src/models.py`: Expense and Budget dataclass definitions and input validations.
- `src/database.py`: Database management layer for SQLite operations.
- `src/gui.py`: Main application UI layout and user event handlers.
- `tests/test_main.py`: Test suite verifying data integrity and storage logic.
