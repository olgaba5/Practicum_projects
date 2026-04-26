   # -*- coding: utf-8 -*-
import json
import os
from datetime import datetime

# Файл для хранения данных
DATA_FILE = "cartridges.json"

def load_data():
    """Загружает данные из файла или создаёт пустую структуру"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "cartridges": [],  # список картриджей
            "departments": []  # список подразделений (для удобства)
        }

def save_data(data):
    """Сохраняет данные в файл"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_cartridge():
    data = load_data()
    print("\n--- Добавление картриджа ---")
    serial = input("Серийный номер: ").strip()
    model = input("Модель: ").strip()
    
    if not serial or not model:
        print("Ошибка: все поля обязательны!")
        return
    
    # Проверяем, есть ли уже такой серийный номер
    for cart in data["cartridges"]:
        if cart["serial"] == serial:
            print("Ошибка: картридж с таким серийным номером уже есть!")
            return
    
    
    cartridge = {
        "serial": serial,
        "model": model,
        "status": "Склад",  # статус: Склад / Выдан
        "department": None,   # подразделение, которому выдан
        "issue_date": None    # дата выдачи
    }
    data["cartridges"].append(cartridge)
    save_data(data)
    print("Картридж добавлен!\n")

def issue_cartridge():
    data = load_data()
    print("\n--- Выдача картриджа ---")
    serial = input("Серийный номер: ").strip()
    department = input("Подразделение/сотрудник: ").strip()
    
    if not serial or not department:
        print("Ошибка: все поля обязательны!")
        return
    
    for cart in data["cartridges"]:
        if cart["serial"] == serial:
            if cart["status"] != "Склад":
                print(f"Ошибка: картридж не на складе (статус: {cart['status']})")
                return
            cart["status"] = "Выдан"
            cart["department"] = department
            cart["issue_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_data(data)
            print(f"Картридж {serial} выдан {department}!\n")
            return
    print("Ошибка: картридж не найден!\n")

def return_cartridge():
    data = load_data()
    print("\n--- Возврат картриджа ---")
    serial = input("Серийный номер: ").strip()
    if not serial:
        print("Ошибка: введите серийный номер!")
        return
    
    for cart in data["cartridges"]:
        if cart["serial"] == serial:
            if cart["status"] != "Выдан":
                print("Ошибка: картридж не был выдан!")
                return
            cart["status"] = "Склад"
            cart["department"] = None
            cart["issue_date"] = None
            save_data(data)
            print(f"Картридж {serial} возвращён на склад!\n")
            return
    print("Ошибка: картридж не найден!\n")

def list_cartridges():
    data = load_data()
    print("\n--- Список картриджей ---")
    if not data["cartridges"]:
        print("Нет ни одного картриджа.")
    else:
        for i, cart in enumerate(data["cartridges"], 1):
            print(f"{i}. Серийный: {cart['serial']}")
            print(f"    Модель: {cart['model']}")
            print(f"    Статус: {cart['status']}")
            if cart["department"]:
                print(f"    Выдан: {cart['department']}")
            if cart["issue_date"]:
                print(f"    Дата выдачи: {cart['issue_date']}")
            print("-! * 30")
    print()

def main():
    print("Система учёта картриджей")
    while True:
        print("1. Добавить картридж")
        print("2. Выдать картридж")
        print("3. Вернуть картридж")
        print("4. Показать все картриджи")
        print("5. Выход")
        
        choice = input("\nВыберите действие (1–5): ").strip()
        
        if choice == "1":
            add_cartridge()
        elif choice == "2":
            issue_cartridge()
        elif choice == "3":
            return_cartridge()
        elif choice == "4":
            list_cartridges()
        elif choice == "5":
            print("До свидания!")
            break
        else:
            print("Неверный ввод. Попробуйте ещё раз.\n")

if __name__ == "__main__":
    main()