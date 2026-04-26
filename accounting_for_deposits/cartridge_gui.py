# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
from datetime import datetime
from collections import Counter

DATA_FILE = "cartridges.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"cartridges": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class CartridgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт картриджей")       
        self.root.geometry("900x500")

        self.data = load_data()

        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)

        ttk.Button(
            btn_frame, text="Добавить", command=self.add_cartridge).pack(
                side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text="Выдать", command=self.issue_cartridge).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text="Вернуть", command=self.return_cartridge).pack(
                side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text="Обновить", command=self.refresh_table).pack(
                side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text="Отчет", command=self.generate_report).pack(
                side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(
            root,
            columns=(
                "Num", "Serial", "Model", "Status", "IssuedTo", "IssueDate"),
            show="headings",
            height=15
        )
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.tree.heading("Num", text="№")       
        self.tree.heading("Serial", text="Серийный номер")
        self.tree.heading("Model", text="Модель")
        self.tree.heading("Status", text="Статус")
        self.tree.heading("IssuedTo", text="Выдан кому")
        self.tree.heading("IssueDate", text="Дата выдачи")

        self.tree.column("Num", width=50)
        self.tree.column("Serial", width=150)
        self.tree.column("Model", width=120)
        self.tree.column("Status", width=100)
        self.tree.column("IssuedTo", width=200)
        self.tree.column("IssueDate", width=120)

        self.refresh_table()

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for idx, cart in enumerate(self.data["cartridges"], 1):
            issued_to = cart.get("issued_to", "")
            issue_date = cart.get("issue_date", "")
            self.tree.insert("", "end", values=(
                idx,
                cart["serial"],
                cart["model"],
                cart["status"],
                issued_to,
                issue_date
            ))

    def add_cartridge(self):
        def save():
            serial = serial_entry.get().strip()
            model = model_entry.get().strip()
            if not serial or not model:
                messagebox.showerror("Ошибка", "Все поля обязательны!")
                return
            for cart in self.data["cartridges"]:
                if cart["serial"] == serial:
                    messagebox.showerror(
                        "Ошибка", "Картридж с таким номером уже есть!")
                    return
            self.data["cartridges"].append({
                "serial": serial,
                "model": model,
                "status": "Склад",
                "issued_to": "",
                "issue_date": ""
            })
            save_data(self.data)
            self.refresh_table()
            add_window.destroy()
            messagebox.showinfo("Успех", "Картридж добавлен!")

        add_window = tk.Toplevel(self.root)
        add_window.title("Добавить картридж")
        add_window.geometry("400x180")
        add_window.resizable(False, False)

        tk.Label(add_window, text="Серийный номер:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w")
        serial_entry = tk.Entry(add_window, width=30)
        serial_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(add_window, text="Модель:").grid(
            row=1, column=0, padx=10, pady=10, sticky="w")
        model_entry = tk.Entry(add_window, width=30)
        model_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(
            add_window,
            text="Сохранить",
            command=save,
            bg="#4CAF50",
            fg="white"
        ).grid(row=2, column=0, columnspan=2, pady=10)

    def issue_cartridge(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите картридж в таблице!")
            return

        values = self.tree.item(selected, "values")
        serial = values[1]

        cart = next((
            c for c in self.data["cartridges"] if c["serial"] == serial), None)
        if not cart:
            messagebox.showerror("Ошибка", "Картридж не найден!")
            return

        if cart["status"] != "Склад":
            messagebox.showerror(
                "Ошибка", f"Картридж не на складе (статус: {cart['status']})")
            return

        def do_issue():
            department = dep_combo.get().strip()
            if not department or department == "Выберите отдел":
                messagebox.showerror("Ошибка", "Выберите подразделение!")
                return
            cart["status"] = "Выдан"
            cart["issued_to"] = department
            cart["issue_date"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            save_data(self.data)
            self.refresh_table()
            issue_window.destroy()
            messagebox.showinfo("Успех", f"Картридж выдан в {department}!")

        issue_window = tk.Toplevel(self.root)
        issue_window.title("Выдать картридж")
        issue_window.geometry("500x250")
        issue_window.resizable(False, False)

        tk.Label(
            issue_window, text=f"Серийный: {serial}").grid(
                row=0, column=0, padx=10, pady=10, sticky="w")
        tk.Label(
            issue_window, text=f"Модель: {cart['model']}").grid(
                row=1, column=0, padx=10, pady=5, sticky="w")

        tk.Label(
            issue_window, text="Подразделение:").grid(
                row=2, column=0, padx=10, pady=10, sticky="w")

        departments = [
            "Выберите отдел",
            "Бух", "Склад сырья", "ООПП", "КомОт", "ПЭО", 
            "ОтВалидации", "Технологи", "АУП", "Испыт центр", 
            "ООК", "ОКК", "КАЛаб", "Окадр", "ОхТр", "Водоподг", 
            "ОИР", "Цех2", "Цех1", "Цех3", "Цех4", "Цех5", "Цех6",
            "Другое"
        ]
        dep_combo = ttk.Combobox(issue_window, values=departments, width=25)
        dep_combo.set("Выберите отдел")
        dep_combo.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(
            issue_window,
            text="Выдать",
            command=do_issue,
            bg="#4CAF50",
            fg="white"
        ).grid(row=3, column=0, columnspan=2, pady=10)

    def return_cartridge(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите картридж в таблице!")
            return

        values = self.tree.item(selected, "values")
        serial = values[1]

        cart = next((
            c for c in self.data["cartridges"] if c["serial"] == serial), None)
        if not cart:
            messagebox.showerror("Ошибка", "Картридж не найден!")
            return

        if cart["status"] != "Выдан":
            messagebox.showerror(
                "Ошибка", f"Картридж не выдан (статус: {cart['status']})")
            return

        cart["status"] = "Склад"
        cart["issued_to"] = ""
        cart["issue_date"] = ""
        save_data(self.data)
        self.refresh_table()
        messagebox.showinfo("Успех", "Картридж возвращён на склад!")

    def get_all_departments(self):
        """Получить список всех отделов (стандартные + используемые)"""
        standard_departments = [
            "Бух", "Склад сырья", "ООПП", "КомОт", "ПЭО", 
            "ОтВалидации", "Технологи", "АУП", "Испыт центр", 
            "ООК", "ОКК", "КАЛаб", "Окадр", "ОхТр", "Водоподг", 
            "ОИР", "Цех2", "Цех1", "Цех3", "Цех4", "Цех5", "Цех6"
        ]

        used_departments = set()
        for cart in self.data["cartridges"]:
            if cart["status"] == "Выдан" and cart["issued_to"]:
                used_departments.add(cart["issued_to"])

        all_departments = sorted(list(set(standard_departments + list(
            used_departments))))
        return all_departments

    def get_department_statistics(
            self, month_filter=None, department_filter=None):
        """Статистика по отделам с фильтрацией по месяцам и отделам"""
        department_stats = Counter()
        monthly_issues = 0
        filtered_issues = 0

        for cart in self.data["cartridges"]:
            if cart["status"] == "Выдан" and cart["issued_to"]:
                if department_filter and department_filter != "Все отделы":
                    if cart["issued_to"] != department_filter:
                        continue

                month_match = True
                if month_filter and cart["issue_date"]:
                    try:
                        issue_date = datetime.strptime(
                            cart["issue_date"], "%d.%m.%Y %H:%M")
                        if issue_date.month != month_filter:
                            month_match = False
                    except ValueError:
                        pass

                if month_match:
                    department_stats[cart["issued_to"]] += 1
                    monthly_issues += 1
                    filtered_issues += 1
                elif not month_filter:
                    department_stats[cart["issued_to"]] += 1

        return department_stats, monthly_issues, filtered_issues

    def generate_report(self):
        """Генерация отчета с расширенной статистикой"""
        report_window = tk.Toplevel(self.root)
        report_window.title("Расширенный отчет по картриджам")
        report_window.geometry("800x600")

        filter_frame = ttk.Frame(report_window)
        filter_frame.pack(pady=10)

        tk.Label(
            filter_frame, text="Месяц:").grid(
                row=0, column=0, padx=5, sticky="w")
        month_var = tk.StringVar(value="Все месяцы")
        month_combo = ttk.Combobox(
            filter_frame, textvariable=month_var,
            values=["Все месяцы", "Январь", "Февраль", "Март", "Апрель",
                    "Май", "Июнь", "Июль", "Август", "Сентябрь",
                    "Октябрь", "Ноябрь", "Декабрь"], width=12)
        month_combo.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Отдел:").grid(
            row=0, column=2, padx=5, sticky="w")
        department_var = tk.StringVar(value="Все отделы")
        departments = ["Все отделы"] + self.get_all_departments()
        department_combo = ttk.Combobox(
            filter_frame, textvariable=department_var,
            values=departments, width=15)
        department_combo.grid(row=0, column=3, padx=5)

        def update_report():
            month_name = month_var.get()
            month_filter = None
            if month_name != "Все месяцы":
                months = [
                    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь",
                    "Декабрь"]
                month_filter = months.index(month_name) + 1

            department_filter = department_var.get()

            total = len(self.data["cartridges"])
            in_stock = len(
                [c for c in self.data["cartridges"] if c["status"] == "Склад"])
            issued = len(
                [c for c in self.data["cartridges"] if c["status"] == "Выдан"])

            department_stats, monthly_issues, filtered_issues = (
                self.get_department_statistics(month_filter, department_filter)
            )
            month_text = f" за {month_name.lower()}" if month_filter else ""
            dept_text = (
                f" - {department_filter}" if department_filter != "Все отделы" else ""
            )

            report_text = f"""ОТЧЕТ ПО КАРТРИДЖАМ{month_text}{dept_text}
Дата формирования: {datetime.now().strftime("%d.%m.%Y %H:%M")}

ОБЩАЯ СТАТИСТИКА:
Всего картриджей: {total}
На складе: {in_stock}
Выдано: {issued}
"""
            if month_filter and department_filter == "Все отделы":
                report_text += f"Выдано в выбранном месяце: {monthly_issues}\n"
            elif department_filter != "Все отделы":
                report_text += f"Выдано по фильтру: {filtered_issues}\n"
            if department_filter == "Все отделы" and department_stats:
                report_text += f"\nСТАТИСТИКА ПО ОТДЕЛАМ{month_text}:\n"
                for dept, count in department_stats.most_common():
                    report_text += f"  {dept}: {count} картриджей\n"
            elif department_filter != "Все отделы" and filtered_issues > 0:
                report_text += f"\nСТАТИСТИКА ПО ОТДЕЛУ:\n"
                report_text += f"  {department_filter}: {filtered_issues} картриджей\n"

            report_text += "\nДЕТАЛЬНАЯ ИНФОРМАЦИЯ:\n"
            displayed_count = 0
            for idx, cart in enumerate(self.data["cartridges"], 1):
                if department_filter != "Все отделы":
                    if cart["issued_to"] != department_filter:
                        continue

                if month_filter and cart["status"] == "Выдан" and cart["issue_date"]:
                    try:
                        issue_date = datetime.strptime(cart["issue_date"], "%d.%m.%Y %H:%M")
                        if issue_date.month != month_filter:
                            continue
                    except ValueError:
                        pass
                elif month_filter and cart["status"] != "Выдан":
                    continue

                report_text += f"\n{idx}. Серийный: {cart['serial']}"
                report_text += f" | Модель: {cart['model']}"
                report_text += f" | Статус: {cart['status']}"
                if cart["status"] == "Выдан":
                    report_text += f" | Выдан: {cart['issued_to']}"
                    report_text += f" | Дата: {cart['issue_date']}"
                displayed_count += 1

            if displayed_count == 0:
                report_text += "\nНет данных, соответствующих выбранным фильтрам"

            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, report_text)
            text_widget.config(state=tk.DISABLED)

        ttk.Button(
            filter_frame, text="Обновить отчет",
            command=update_report).grid(row=0, column=4, padx=10)

        text_frame = ttk.Frame(report_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Courier New", 9))
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(report_window)
        btn_frame.pack(pady=10)

        ttk.Button(
            btn_frame, text="Сохранить в файл",
            command=lambda: self.save_report(
                      text_widget.get(1.0, tk.END))).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text="Копировать в буфер",
            command=lambda: self.copy_to_clipboard(
                      text_widget.get(1.0, tk.END))).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text="Закрыть",
            command=report_window.destroy).pack(side=tk.LEFT, padx=5)

        update_report()

    def save_report(self, report_text):
        """Сохранение отчета в файл"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            title="Сохранить отчет как"
        )

        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(report_text)
                messagebox.showinfo(
                    "Успех", f"Отчет сохранен в файл:\n{filename}")
            except Exception as e:
                messagebox.showerror(
                    "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def copy_to_clipboard(self, report_text):
        """Копирование в буфер обмена"""
        self.root.clipboard_clear()
        self.root.clipboard_append(report_text)
        messagebox.showinfo("Успех", "Отчет скопирован в буфер обмена")


if __name__ == "__main__":
    root = tk.Tk()
    app = CartridgeApp(root)
    root.mainloop()
