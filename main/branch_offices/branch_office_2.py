import sys
from main.utils.branch_offices import SalesApp
import tkinter as tk
import os



root = tk.Tk()
database = {
    'user': os.getenv('BRANCH_OFFICE_2_DB_USER'),
    'password': os.getenv('BRANCH_OFFICE_2_DB_PASSWORD'),
    'host': os.getenv('BRANCH_OFFICE_2_DB_HOST'),
    'port': os.getenv('BRANCH_OFFICE_2_DB_PORT'),
    'database': os.getenv('BRANCH_OFFICE_2_DB_NAME')
}
branche_office = 2
app = SalesApp(root, "Sales CRUD Operations - Branch Office 2", database, branche_office)
root.mainloop()