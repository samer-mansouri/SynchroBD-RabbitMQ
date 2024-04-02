import tkinter as tk
from tkinter import ttk
import threading
import pika
import json
import mysql.connector

class HeadOfficeApp:
    def __init__(self, master):
        self.master = master
        self.master.title('Head Office Sales Records')
        self.master.geometry('1920x1080')

        self.tree = None
        self.setup_ui()
        threading.Thread(target=self.setup_rabbitmq_consumer, daemon=True).start()

    def setup_ui(self):
        self.tree = ttk.Treeview(self.master, columns=('Remote ID', 'Branch Office', 'Date', 'Region', 'Product', 'Qty', 'Cost', 'Amt', 'Tax', 'Total'), show='headings')
        for col in self.tree['columns']:
            self.tree.column(col, anchor=tk.W, width=120)
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.refresh_view()

    def refresh_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        records = self.db_execute("SELECT remote_id, branch_office_id, date, region, product, qty, cost, amt, tax, total FROM sales", fetch=True)
        for record in records:
            self.tree.insert('', tk.END, values=record)

    def db_execute(self, query, params=None, commit=False, fetch=False):
        with mysql.connector.connect(user='user', password='password', host='localhost', database='head_office') as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if commit:
                conn.commit()
            if fetch:
                return cursor.fetchall()

    def setup_rabbitmq_consumer(self):
        credentials = pika.PlainCredentials('user', 'password')
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
        channel = connection.channel()

        channel.exchange_declare(exchange='sales_actions', exchange_type='topic')
        result = channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='sales_actions', queue=queue_name, routing_key='sales.#')
        channel.basic_consume(queue=queue_name, on_message_callback=self.on_message, auto_ack=True)
        channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        print(f" [x] Received '{method.routing_key}':'{body.decode()}")
        message = json.loads(body)
        action = method.routing_key.split('.')[1]
        self.process_action(action, message)

    def process_action(self, action, message):
        data = message.get('data')
        branch_office_id = message.get('branch_office_id')  # Corrected variable name
        if action == 'insert':
            self.db_execute(
                "INSERT INTO sales (remote_id, branch_office_id, date, region, product, qty, cost, amt, tax, total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (data['remote_id'], branch_office_id, data['date'], data['region'], data['product'], data['qty'], data['cost'], data['amt'], data['tax'], data['total']),
                commit=True
            )
        elif action == 'update':
            self.db_execute(
                "UPDATE sales SET date=%s, region=%s, product=%s, qty=%s, cost=%s, amt=%s, tax=%s, total=%s WHERE remote_id=%s AND branch_office_id=%s",
                (data['date'], data['region'], data['product'], data['qty'], data['cost'], data['amt'], data['tax'], data['total'], data['remote_id'], branch_office_id),
                commit=True
            )
        elif action == 'delete':
            self.db_execute(
                "DELETE FROM sales WHERE remote_id=%s AND branch_office_id=%s",
                (data['remote_id'], branch_office_id),
                commit=True
            )
        # Refresh the UI to reflect changes
        self.master.after(0, self.refresh_view)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam')
    app = HeadOfficeApp(root)
    root.mainloop()
