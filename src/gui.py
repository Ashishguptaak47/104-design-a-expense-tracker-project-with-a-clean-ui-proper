import csv
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.database import DatabaseManager
from src.models import Expense, CATEGORIES


class ExpenseTrackerApp(tk.Tk):
    def __init__(self, db_manager: DatabaseManager = None):
        super().__init__()
        self.title("Modern Expense Tracker")
        self.geometry("850x600")
        self.minsize(750, 500)

        self.db = db_manager if db_manager else DatabaseManager()

        self._configure_theme()
        self._create_widgets()
        self.refresh_data()

    def _configure_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Color palette
        bg_color = "#F4F6F9"
        accent_color = "#2C3E50"
        primary_color = "#3498DB"

        self.configure(bg=bg_color)
        style.configure(".", background=bg_color, font=("Helvetica", 10))
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground="#333333")
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground=accent_color)
        style.configure("Card.TFrame", background="#FFFFFF", relief="solid", borderwidth=1)
        style.configure("TButton", background=primary_color, foreground="#FFFFFF", borderwidth=0, padding=6)
        style.map("TButton", background=[("active", "#2980B9")])
        style.configure("Treeview", rowheight=25, font=("Helvetica", 9))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#EAECEE")

    def _create_widgets(self):
        # Header Bar
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", px=20, py=15)
        ttk.Label(header_frame, text="💸 Personal Expense Tracker", style="Header.TLabel").pack(side="left")

        # Main Tabbed Interface
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, px=20, py=(0, 20))

        # Tabs
        self.tab_dashboard = ttk.Frame(notebook)
        self.tab_transactions = ttk.Frame(notebook)
        self.tab_budgets = ttk.Frame(notebook)

        notebook.add(self.tab_dashboard, text="Dashboard & Add")
        notebook.add(self.tab_transactions, text="Transactions")
        notebook.add(self.tab_budgets, text="Budgets")

        self._build_dashboard_tab()
        self._build_transactions_tab()
        self._build_budgets_tab()

    def _build_dashboard_tab(self):
        # Top: Summary Card
        summary_card = ttk.Frame(self.tab_dashboard, style="Card.TFrame", padding=15)
        summary_card.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(summary_card, text="Total Spending", font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.lbl_total_spending = ttk.Label(summary_card, text="$0.00", font=("Helvetica", 22, "bold"), foreground="#E74C3C")
        self.lbl_total_spending.pack(anchor="w", pady=5)

        # Bottom: Add Expense Form
        form_frame = ttk.LabelFrame(self.tab_dashboard, text="Add New Expense", padding=15)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_title = ttk.Entry(form_frame, width=30)
        self.ent_title.grid(row=0, column=1, sticky="w", pady=5, padx=10)

        ttk.Label(form_frame, text="Amount ($):").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_amount = ttk.Entry(form_frame, width=30)
        self.ent_amount.grid(row=1, column=1, sticky="w", pady=5, padx=10)

        ttk.Label(form_frame, text="Category:").grid(row=2, column=0, sticky="w", pady=5)
        self.cmb_category = ttk.Combobox(form_frame, values=CATEGORIES, state="readonly", width=28)
        self.cmb_category.current(0)
        self.cmb_category.grid(row=2, column=1, sticky="w", pady=5, padx=10)

        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_date = ttk.Entry(form_frame, width=30)
        self.ent_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.ent_date.grid(row=3, column=1, sticky="w", pady=5, padx=10)

        ttk.Label(form_frame, text="Notes:").grid(row=4, column=0, sticky="nw", pady=5)
        self.ent_notes = ttk.Entry(form_frame, width=30)
        self.ent_notes.grid(row=4, column=1, sticky="w", pady=5, padx=10)

        btn_add = ttk.Button(form_frame, text="Save Expense", command=self._on_add_expense)
        btn_add.grid(row=5, column=1, sticky="e", pady=15, padx=10)

    def _build_transactions_tab(self):
        # Filter Controls
        filter_frame = ttk.Frame(self.tab_transactions, padding=10)
        filter_frame.pack(fill="x")

        ttk.Label(filter_frame, text="Filter Category:").pack(side="left", padx=(0, 5))
        self.cmb_filter = ttk.Combobox(filter_frame, values=["All"] + CATEGORIES, state="readonly", width=15)
        self.cmb_filter.current(0)
        self.cmb_filter.pack(side="left", padx=5)
        self.cmb_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_transactions())

        btn_export = ttk.Button(filter_frame, text="Export CSV", command=self._export_csv)
        btn_export.pack(side="right", padx=5)

        btn_delete = ttk.Button(filter_frame, text="Delete Selected", command=self._delete_selected_expense)
        btn_delete.pack(side="right", padx=5)

        # Treeview Table
        columns = ("id", "date", "title", "category", "amount", "notes")
        self.tree = ttk.Treeview(self.tab_transactions, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("title", text="Title")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("notes", text="Notes")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("date", width=90, anchor="center")
        self.tree.column("title", width=180)
        self.tree.column("category", width=120)
        self.tree.column("amount", width=90, anchor="e")
        self.tree.column("notes", width=200)

        scrollbar = ttk.Scrollbar(self.tab_transactions, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

    def _build_budgets_tab(self):
        form_frame = ttk.LabelFrame(self.tab_budgets, text="Set Category Budget", padding=10)
        form_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(form_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        self.cmb_budget_cat = ttk.Combobox(form_frame, values=CATEGORIES, state="readonly", width=15)
        self.cmb_budget_cat.current(0)
        self.cmb_budget_cat.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Monthly Limit ($):").grid(row=0, column=2, padx=5, pady=5)
        self.ent_budget_limit = ttk.Entry(form_frame, width=15)
        self.ent_budget_limit.grid(row=0, column=3, padx=5, pady=5)

        btn_set_budget = ttk.Button(form_frame, text="Set Budget", command=self._on_set_budget)
        btn_set_budget.grid(row=0, column=4, padx=10, pady=5)

        # Budget Overview Box
        self.budget_display_frame = ttk.LabelFrame(self.tab_budgets, text="Budget Status", padding=10)
        self.budget_display_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def _on_add_expense(self):
        try:
            title = self.ent_title.get()
            amount = float(self.ent_amount.get())
            category = self.cmb_category.get()
            date = self.ent_date.get()
            notes = self.ent_notes.get()

            expense = Expense(title=title, amount=amount, category=category, date=date, notes=notes)
            self.db.add_expense(expense)
            
            # Reset fields
            self.ent_title.delete(0, tk.END)
            self.ent_amount.delete(0, tk.END)
            self.ent_notes.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Expense added successfully!")
            self.refresh_data()
        except ValueError as ex:
            messagebox.showerror("Input Error", str(ex))

    def _delete_selected_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an expense to delete.")
            return
        
        item = self.tree.item(selected[0])
        expense_id = item["values"][0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete expense ID {expense_id}?"):
            self.db.delete_expense(expense_id)
            self.refresh_data()

    def _on_set_budget(self):
        try:
            cat = self.cmb_budget_cat.get()
            limit = float(self.ent_budget_limit.get())
            self.db.set_budget(cat, limit)
            self.ent_budget_limit.delete(0, tk.END)
            messagebox.showinfo("Success", f"Budget set for {cat}.")
            self.refresh_budgets()
        except ValueError as ex:
            messagebox.showerror("Input Error", str(ex))

    def _export_csv(self):
        expenses = self.db.get_all_expenses(self.cmb_filter.get())
        if not expenses:
            messagebox.showwarning("Export Failed", "No transactions available to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filepath:
            with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Date", "Title", "Category", "Amount", "Notes"])
                for exp in expenses:
                    writer.writerow([exp.id, exp.date, exp.title, exp.category, f"{exp.amount:.2f}", exp.notes])
            messagebox.showinfo("Export Complete", f"Successfully exported to {filepath}")

    def refresh_data(self):
        self.refresh_dashboard()
        self.refresh_transactions()
        self.refresh_budgets()

    def refresh_dashboard(self):
        stats = self.db.get_summary_stats()
        self.lbl_total_spending.config(text=f"${stats['total_spent']:.2f}")

    def refresh_transactions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        cat_filter = self.cmb_filter.get()
        expenses = self.db.get_all_expenses(cat_filter)
        for exp in expenses:
            self.tree.insert("", "end", values=(exp.id, exp.date, exp.title, exp.category, f"${exp.amount:.2f}", exp.notes))

    def refresh_budgets(self):
        for widget in self.budget_display_frame.winfo_children():
            widget.destroy()

        budgets = self.db.get_budgets()
        stats = self.db.get_summary_stats()
        by_cat = stats.get("by_category", {})

        if not budgets:
            ttk.Label(self.budget_display_frame, text="No category budgets set yet.").pack(anchor="w")
            return

        for row_idx, (cat, limit) in enumerate(budgets.items()):
            spent = by_cat.get(cat, 0.0)
            percentage = min((spent / limit) * 100, 100) if limit > 0 else 0
            
            b_frame = ttk.Frame(self.budget_display_frame)
            b_frame.pack(fill="x", pady=5)
            
            lbl_text = f"{cat}: ${spent:.2f} / ${limit:.2f} ({percentage:.1f}%)"
            color = "#E74C3C" if spent > limit else "#2ECC71"
            ttk.Label(b_frame, text=lbl_text, foreground=color, font=("Helvetica", 10, "bold")).pack(anchor="w")
            
            progress = ttk.Progressbar(b_frame, value=percentage, maximum=100)
            progress.pack(fill="x", pady=(2, 0))
