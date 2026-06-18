import json
import os
import re
import tkinter as tk
from tkinter import messagebox, ttk
import requests

HISTORY_FILE = "history.json"
API_URL = "https://er-api.com"

if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception:
        history = []
else:
    history = []

try:
    response = requests.get(API_URL, timeout=5)
    if response.status_code == 200:
        rates = response.json().get("rates", {})
    else:
        rates = {"USD": 1.0, "EUR": 0.92, "RUB": 92.5, "CNY": 7.23, "GBP": 0.79}
except Exception:
    rates = {"USD": 1.0, "EUR": 0.92, "RUB": 92.5, "CNY": 7.23, "GBP": 0.79}


def convert_currency():
    amount_str = amount_entry.get().strip()
    c_from = from_currency.get()
    c_to = to_currency.get()
    if not amount_str or not re.match(r"^\d+(\.\d+)?$", amount_str):
        messagebox.showwarning(
            "Ошибка ввода", "Сумма должна быть положительным числом."
        )
        return
    amount = float(amount_str)
    if amount <= 0:
        messagebox.showwarning("Ошибка ввода", "Сумма должна быть больше нуля.")
        return
    amount_in_usd = amount / rates[c_from]
    converted_amount = round(amount_in_usd * rates[c_to], 2)
    result_label.config(
        text=f"Результат: {amount} {c_from} = {converted_amount} {c_to}"
    )
    log_entry = {
        "amount_from": amount,
        "curr_from": c_from,
        "amount_to": converted_amount,
        "curr_to": c_to,
    }
    history.append(log_entry)
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
    refresh_history_table()


def refresh_history_table():
    for item in tree.get_children():
        tree.delete(item)
    for log in reversed(history):
        tree.insert(
            "",
            tk.END,
            values=(
                log["amount_from"],
                log["curr_from"],
                log["amount_to"],
                log["curr_to"],
            ),
        )


root = tk.Tk()
root.title("Currency Converter — Конвертер валют")
root.geometry("600x530")
root.resizable(False, False)
conv_frame = ttk.LabelFrame(root, text=" Конвертация ", padding=15)
conv_frame.pack(fill="x", padx=15, pady=10)
ttk.Label(conv_frame, text="Сумма:", font=("Arial", 10)).grid(
    row=0, column=0, sticky="w", pady=5
)
amount_entry = ttk.Entry(conv_frame, font=("Arial", 10))
amount_entry.grid(row=0, column=1, columnspan=3, fill="x", pady=5, padx=5)
currency_list = list(rates.keys())
ttk.Label(conv_frame, text="Из:", font=("Arial", 10)).grid(
    row=1, column=0, sticky="w", pady=5
)
from_currency = ttk.Combobox(
    conv_frame, values=currency_list, state="readonly", width=10
)
from_currency.grid(row=1, column=1, pady=5, padx=5)
from_currency.set("USD")
ttk.Label(conv_frame, text="В:", font=("Arial", 10)).grid(
    row=1, column=2, sticky="w", pady=5
)
to_currency = ttk.Combobox(
    conv_frame, values=currency_list, state="readonly", width=10
)
to_currency.grid(row=1, column=3, pady=5, padx=5)
to_currency.set("RUB")
convert_btn = ttk.Button(conv_frame, text="Конвертировать", command=convert_currency)
convert_btn.grid(row=2, column=0, columnspan=4, pady=10)
result_label = ttk.Label(
    conv_frame, text="Результат: ---", font=("Arial", 11, "bold"), foreground="blue"
)
result_label.grid(row=3, column=0, columnspan=4, pady=5)
hist_frame = ttk.LabelFrame(root, text=" История конвертаций ", padding=10)
hist_frame.pack(fill="both", expand=True, padx=15, pady=10)
columns = ("amount_from", "curr_from", "amount_to", "curr_to")
tree = ttk.Treeview(hist_frame, columns=columns, show="headings")
tree.heading("amount_from", text="Исходная сумма")
tree.heading("curr_from", text="Из валюты")
tree.heading("amount_to", text="Результат")
tree.heading("curr_to", text="В валюту")
tree.column("amount_from", anchor="center", width=120)
tree.column("curr_from", anchor="center", width=100)
tree.column("amount_to", anchor="center", width=120)
tree.column("curr_to", anchor="center", width=100)
tree.pack(side="left", fill="both", expand=True)
scrollbar = ttk.Scrollbar(hist_frame, orient="vertical", command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar.set)
refresh_history_table()
root.mainloop()

