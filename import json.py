import json
import os
import re
import tkinter as tk
from tkinter import messagebox
import requests
FAVORITES_FILE = "favorites.json"
GITHUB_API_URL = "https://github.com"
def fetch_github_user(username):
    try:
        response = requests.get(f"{GITHUB_API_URL}{username}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "login": data.get("login"),
                "name": data.get("name") or "Не указано",
                "html_url": data.get("html_url"),
            }
        elif response.status_code == 404:
            return {"success": False, "error": "Пользователь не найден."}
        else:
            return {"success": False, "error": f"Ошибка сервера (Код {response.status_code})"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Превышено время ожидания запроса."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Отсутствует подключение к сети."}
    except Exception as e:
        return {"success": False, "error": f"Ошибка: {str(e)}"}

def search_user():
    username = entry.get().strip()
    if not username:
        messagebox.showwarning("Ошибка", "Поле поиска не должно быть пустым.")
        return
    if not re.match(r"^[a-zA-Z0-9-]+$", username):
        messagebox.showwarning("Ошибка", "Логин может содержать только латиницу, цифры и дефис.")
        return
    result = fetch_github_user(username)
    if result["success"]:
        global current_user_data
        current_user_data = result
        display_text = f"Логин: {result['login']}\nИмя: {result['name']}\nСсылка: {result['html_url']}"
        label_result.config(text=display_text, fg="black")
        btn_add.config(state="normal")
    else:
        label_result.config(text=result["error"], fg="red")
        btn_add.config(state="disabled")

def add_to_favorites():
    global current_user_data
    if not current_user_data:
        return
    login = current_user_data["login"]
    if any(user["login"].lower() == login.lower() for user in favorites):
        messagebox.showinfo("Инфо", "Пользователь уже в избранном.")
        return
    favorites.append(current_user_data)
    try:
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(favorites, f, ensure_ascii=False, indent=4)
        listbox.insert(tk.END, f"{login} ({current_user_data['name']}) — {current_user_data['html_url']}")
        messagebox.showinfo("Успех", f"Пользователь {login} добавлен.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

root = tk.Tk()
root.title("GitHub User Finder")
root.geometry("450x520")
current_user_data = None
if os.path.exists(FAVORITES_FILE):
    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            favorites = json.load(f)
    except Exception:
        favorites = []
else:
    favorites = []
tk.Label(root, text="Введите логин GitHub:", font=("Arial", 10, "bold")).pack(pady=5)
entry = tk.Entry(root, font=("Arial", 11), width=30)
entry.pack(pady=5)
tk.Button(root, text="Найти пользователя", command=search_user, bg="#e1e1e1").pack(pady=5)
label_result = tk.Label(root, text="Результаты поиска появятся здесь...", justify="left", font=("Arial", 10))
label_result.pack(pady=15)
btn_add = tk.Button(root, text="Добавить в избранное", state="disabled", command=add_to_favorites, bg="#d4edda")
btn_add.pack(pady=5)
tk.Label(root, text="Избранные пользователи (сохранено в JSON):", font=("Arial", 9, "italic")).pack(pady=(15, 2))
listbox = tk.Listbox(root, width=60, font=("Arial", 9))
listbox.pack(pady=5, fill="both", expand=True, padx=10)
for user in favorites:
    listbox.insert(tk.END, f"{user['login']} ({user['name']}) — {user['html_url']}")
root.mainloop()