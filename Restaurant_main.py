
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

MENU = {
    "Veg Burger": 120,
    "Cheese Pizza": 250,
    "Masala Dosa": 90,
    "Paneer Sandwich": 100,
    "French Fries": 80,
    "Veg Biryani": 180,
    "Cold Coffee": 100,
    "Lemon Soda": 40
}

TAX_RATE = 0.05
DATA_FILE = "bills.json"

class RestaurantBilling:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Billing System")
        self.root.geometry("750x650")
        self.root.resizable(False, False)

        self.order = []

        tk.Label(
            root,
            text="RESTAURANT BILLING SYSTEM",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#17365D",
            pady=15
        ).pack(fill="x")

        form = tk.Frame(root, padx=15, pady=15)
        form.pack(fill="x")

        tk.Label(form, text="Menu Item").grid(row=0, column=0, padx=5, pady=5)
        self.item_var = tk.StringVar()
        self.item_box = ttk.Combobox(
            form,
            textvariable=self.item_var,
            values=list(MENU.keys()),
            state="readonly",
            width=22
        )
        self.item_box.grid(row=0, column=1, padx=5, pady=5)
        self.item_box.current(0)
        self.item_box.bind("<<ComboboxSelected>>", self.show_price)

        tk.Label(form, text="Quantity").grid(row=0, column=2, padx=5, pady=5)
        self.qty_entry = tk.Entry(form, width=10)
        self.qty_entry.grid(row=0, column=3, padx=5, pady=5)
        self.qty_entry.insert(0, "1")

        self.price_label = tk.Label(form, text="Price: ₹120")
        self.price_label.grid(row=1, column=1, pady=5)

        tk.Button(
            form,
            text="Add Item",
            command=self.add_item,
            bg="#198754",
            fg="white",
            width=15
        ).grid(row=1, column=2, padx=5, pady=10)

        columns = ("Item", "Quantity", "Price", "Amount")
        self.table = ttk.Treeview(
            root,
            columns=columns,
            show="headings",
            height=13
        )

        for column in columns:
            self.table.heading(column, text=column)
            self.table.column(column, width=170, anchor="center")

        self.table.pack(padx=15, pady=10, fill="x")

        self.subtotal_label = tk.Label(root, text="Subtotal: ₹0.00", font=("Arial", 12))
        self.subtotal_label.pack(anchor="e", padx=35)

        self.tax_label = tk.Label(root, text="Tax (5%): ₹0.00", font=("Arial", 12))
        self.tax_label.pack(anchor="e", padx=35)

        self.total_label = tk.Label(
            root,
            text="Grand Total: ₹0.00",
            font=("Arial", 15, "bold"),
            fg="#17365D"
        )
        self.total_label.pack(anchor="e", padx=35, pady=5)

        buttons = tk.Frame(root, pady=12)
        buttons.pack()

        tk.Button(
            buttons,
            text="Generate Bill",
            command=self.generate_bill,
            width=15,
            bg="#17365D",
            fg="white"
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            buttons,
            text="Remove Selected",
            command=self.remove_item,
            width=15
        ).grid(row=0, column=1, padx=8)

        tk.Button(
            buttons,
            text="Clear Order",
            command=self.clear_order,
            width=15
        ).grid(row=0, column=2, padx=8)

        self.update_totals()

    def show_price(self, event=None):
        item = self.item_var.get()
        self.price_label.config(text=f"Price: ₹{MENU[item]}")

    def add_item(self):
        item = self.item_var.get()

        try:
            quantity = int(self.qty_entry.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Quantity",
                "Enter a positive whole number."
            )
            return

        price = MENU[item]
        amount = price * quantity

        self.order.append({
            "item": item,
            "quantity": quantity,
            "price": price,
            "amount": amount
        })

        self.refresh_table()
        self.update_totals()

    def refresh_table(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for item in self.order:
            self.table.insert(
                "",
                "end",
                values=(
                    item["item"],
                    item["quantity"],
                    f'₹{item["price"]:.2f}',
                    f'₹{item["amount"]:.2f}'
                )
            )

    def update_totals(self):
        subtotal = sum(item["amount"] for item in self.order)
        tax = subtotal * TAX_RATE
        total = subtotal + tax

        self.subtotal_label.config(text=f"Subtotal: ₹{subtotal:.2f}")
        self.tax_label.config(text=f"Tax (5%): ₹{tax:.2f}")
        self.total_label.config(text=f"Grand Total: ₹{total:.2f}")

    def remove_item(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select an item to remove.")
            return

        index = self.table.index(selected[0])
        self.order.pop(index)
        self.refresh_table()
        self.update_totals()

    def clear_order(self):
        self.order.clear()
        self.refresh_table()
        self.update_totals()

    def generate_bill(self):
        if not self.order:
            messagebox.showwarning("Warning", "Please add items first.")
            return

        subtotal = sum(item["amount"] for item in self.order)
        tax = subtotal * TAX_RATE
        total = subtotal + tax

        bill = {
            "bill_no": datetime.now().strftime("%Y%m%d%H%M%S"),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": self.order.copy(),
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "grand_total": round(total, 2)
        }

        bills = []

        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as file:
                    bills = json.load(file)
                if not isinstance(bills, list):
                    bills = []
            except (json.JSONDecodeError, OSError):
                bills = []

        bills.append(bill)

        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(bills, file, indent=4)
        except OSError as error:
            messagebox.showerror("File Error", str(error))
            return

        receipt = f"Bill No: {bill['bill_no']}\n"
        receipt += f"Date: {bill['date']}\n"
        receipt += "-" * 32 + "\n"

        for item in self.order:
            receipt += (
                f"{item['item']} x {item['quantity']} = "
                f"₹{item['amount']:.2f}\n"
            )

        receipt += "-" * 32 + "\n"
        receipt += f"Subtotal: ₹{subtotal:.2f}\n"
        receipt += f"Tax (5%): ₹{tax:.2f}\n"
        receipt += f"Grand Total: ₹{total:.2f}\n"

        messagebox.showinfo("Customer Bill", receipt)

        self.clear_order()


if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantBilling(root)
    root.mainloop()
