import ttk

root = tk.Tk()
root.title("Тест GUI")
root.geometry("400x300")

label = tk.Label(root, text="GUI работает!", font=("Arial", 16))
label.pack(pady=20)
import tkinter as tk
from tkinter 
button = ttk.Button(root, text="Закрыть", command=root.destroy)
button.pack(pady=10)

root.mainloop()
