import tkinter as tk
from tkinter import ttk
from .database import DatabaseManager
from .consumer import RabbitMQConsumer
import os

class HeadOfficeApp:
    def __init__(self, master):
        self.master = master
        self.master.title('Head Office Sales Records')
        self.master.geometry('1920x1080')

        self.db_manager = DatabaseManager({
            'user': os.getenv('HEAD_OFFICE_DB_USER'),
            'password': os.getenv('HEAD_OFFICE_DB_PASSWORD'),
            'host': os.getenv('HEAD_OFFICE_DB_HOST'),
            'database': os.getenv('HEAD_OFFICE_DB_NAME')
        })

        RabbitMQConsumer(self.process_action)

        self.setup_ui()

    def setup_ui(self):
        self.tree = ttk.Treeview(self.master, columns=('Remote ID', 'Branch Office', 'Date', 'Region', 'Product', 'Qty', 'Cost', 'Amt', 'Tax', 'Total'), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.refresh_view()

    def refresh_view(self):
        records = self.db_manager.execute("SELECT remote_id, branch_office_id, date, region, product, qty, cost, amt, tax, total FROM sales", fetch=True)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for record in records:
            self.tree.insert('', tk.END, values=record)

    def process_action(self, action, message):
        data = message.get('data', {})
        branch_office_id = message.get('branch_office_id')
        try:
            if action == 'insert':
                self.db_manager.execute(
                    "INSERT INTO sales (remote_id, branch_office_id, date, region, product, qty, cost, amt, tax, total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (data['remote_id'], branch_office_id, data['date'], data['region'], data['product'], data['qty'], data['cost'], data['amt'], data['tax'], data['total']),
                    commit=True
                )
            elif action == 'update':
                self.db_manager.execute(
                    "UPDATE sales SET date=%s, region=%s, product=%s, qty=%s, cost=%s, amt=%s, tax=%s, total=%s WHERE remote_id=%s AND branch_office_id=%s",
                    (data['date'], data['region'], data['product'], data['qty'], data['cost'], data['amt'], data['tax'], data['total'], data['remote_id'], branch_office_id),
                    commit=True
                )
            elif action == 'delete':
                self.db_manager.execute(
                    "DELETE FROM sales WHERE remote_id=%s AND branch_office_id=%s",
                    (data['remote_id'], branch_office_id),
                    commit=True
                )
            self.master.after(0, self.refresh_view)
        except Exception as e:
            print(f"Error processing action {action}: {e}")