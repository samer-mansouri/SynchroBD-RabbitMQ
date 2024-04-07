import tkinter as tk
from tkinter import messagebox, ttk
from main.utils.database import DatabaseManager
from main.utils.producer import RabbitMQProducer
import json

class SalesApp:
    def __init__(self, master, title, database_config, branch_office, db_region):
        self.master = master
        self.branch_office = branch_office
        self.master.title(title)
        self.master.geometry("1920x1080")
        
        
        # Initialize the database manager
        self.db_manager = DatabaseManager(database_config)
        
        
        # Initializing Producer
        self.producer = RabbitMQProducer()

        self.region = db_region
        # Styling
        style = ttk.Style(self.master)
        style.theme_use('clam')

        # Initialize the Treeview
        self.setup_treeview()

        # Initialize the form
        self.setup_form()

        # Initialize the buttons
        self.setup_buttons()

        # Load initial data into the Treeview
        self.load_data()

    def setup_treeview(self):
        tree_frame = ttk.Frame(self.master, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree_scroll = ttk.Scrollbar(tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=self.tree_scroll.set, selectmode="extended", columns=("Date", "Region", "Product", "Qty", "Cost", "Amt", "Tax", "Total"))
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree_scroll.config(command=self.tree.yview)
        
        self.tree.column("#0", width=0, stretch=tk.NO)
        for col in ("Date", "Region", "Product", "Qty", "Cost", "Amt", "Tax", "Total"):
            self.tree.column(col, anchor=tk.W, width=120)
            self.tree.heading(col, text=col, anchor=tk.W)
        
        self.tree.bind("<<TreeviewSelect>>", self.get_selected_row)
        self.tree.bind("<Button-1>", self.on_treeview_click)
        self.tree.bind('<ButtonRelease-1>', self.on_treeview_click)

    def setup_form(self):
        entry_frame = ttk.Frame(self.master, padding="10")
        entry_frame.pack(fill=tk.X, padx=10, pady=5)
        
        labels = ["Date", "Product", "Qty", "Cost", "Amt", "Tax", "Total"]
        self.entries = {}
        print("labels:", labels)
        for i, label in enumerate(labels):
            ttk.Label(entry_frame, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="W")
            entry = ttk.Entry(entry_frame)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="EW")
            entry_frame.columnconfigure(1, weight=1)
            self.entries[label.lower()] = entry

    def setup_buttons(self):
        button_frame = ttk.Frame(self.master, padding="10")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Insert Record", command=self.insert_data).pack(side=tk.LEFT, padx=5, pady=5)
        self.update_button = ttk.Button(button_frame, text="Update Selected Record", command=self.update_data, state="disabled")
        self.update_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.delete_button = ttk.Button(button_frame, text="Delete Selected Record", command=self.delete_data, state="disabled")
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = "SELECT * FROM sales"
        rows = self.db_manager.execute(query, fetch=True)
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def insert_data(self):
        data = {entry: self.entries[entry].get() for entry in self.entries}
        if all(data.values()):
            query = """
                INSERT INTO sales (date, product, qty, cost, amt, tax, total, region)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = tuple(data[entry] for entry in self.entries) + (self.region,)
            try:
                data['remote_id'] = self.db_manager.insert(query, params=params)
                data['region'] = self.region
                print("remote_id:", data['remote_id'])
                messagebox.showinfo("Success", "Record inserted successfully.")
                self.producer.publish_message('insert', json.dumps({"branch_office_id": self.branch_office, "data": data}))
                self.clear_entries()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", "Please fill in all fields.")

    def update_data(self):
        selected_item = self.tree.focus()  # Get the selected item
        print("selected_item id", self.tree.item(selected_item, 'values')[-1])
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to update.")
            return
        data = {entry: self.entries[entry].get() for entry in self.entries}
        data["remote_id"] = self.tree.item(selected_item, 'values')[-1]
        query = """
            UPDATE sales 
            SET date=%s, product=%s, qty=%s, cost=%s, amt=%s, tax=%s, total=%s 
            WHERE id=%s
        """
        params = tuple(data[entry] for entry in self.entries) + (self.tree.item(selected_item, 'values')[-1],)
        try:
            self.db_manager.execute(query, params=params, commit=True)
            print("data:", data)
            self.producer.publish_message('update', json.dumps({"branch_office_id": self.branch_office, "data": data}))
            messagebox.showinfo("Success", "Record updated successfully.")
            self.clear_entries()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_data(self):
        selected_item = self.tree.focus()  # Get the selected item
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return
        print("Full selected item:", self.tree.item(selected_item, 'values'))
        query = "DELETE FROM sales WHERE id=%s"
        ##the id is the last value in the selected item
        selected_id = self.tree.item(selected_item, 'values')[-1]
        print("selected_id:", selected_id)
        try:
            self.db_manager.execute(query, params=(selected_id,), commit=True)
            self.producer.publish_message('delete', json.dumps({"branch_office_id": self.branch_office, "data": {"remote_id": selected_id}}))
            messagebox.showinfo("Success", "Record deleted successfully.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # def clear_entries(self):
    #     for entry in self.entries.values():
    #         entry.delete(0, tk.END)
    #     self.master.update_idletasks()  # Force the Tkinter window to update

    def get_selected_row(self, event):
        self.clear_entries()  # Clear any existing data in the entry fields
        self.update_button['state'] = 'normal'  # Enable the update button
        self.delete_button['state'] = 'normal'  # Enable the delete button

        selected_item = self.tree.focus()  # Get the selected item
        if selected_item:  # If something is selected
            row = self.tree.item(selected_item, 'values')  # Get the item's values
            ## remove from the tuple the element with index 1
            row = row[:1] + row[2:]
            print("Selected row:", row)
            self.selected_row = row  # Save the selected row data
            for key, entry in zip(self.entries.keys(), row):
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, entry)

    # def on_treeview_click(self, event):
    #     print("Clicked inside Treeview")  # Debug print
    #     if self.tree.identify_row(event.y) == '':
    #         print("Clicked outside of items")  # Debug print
    #         self.clear_entries()
    #         self.toggle_button_state()

    def on_treeview_click(self, event):
        if self.tree.identify_row(event.y) == '':
            self.tree.selection_remove(self.tree.selection())
            self.tree.focus('')  # Remove focus from the Treeview
            self.clear_entries()
            self.toggle_button_state()

    def clear_entries(self):
        print("Clearing entries")  # Debug print
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def toggle_button_state(self):
        print("Toggling button state")  # Debug print
        selected = self.tree.selection()
        state = 'normal' if selected else 'disabled'
        self.update_button['state'] = state
        self.delete_button['state'] = state


if __name__ == "__main__":
    root = tk.Tk()
    app = SalesApp(root, "Sales CRUD Operations")
    root.mainloop()
