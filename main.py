import tkinter as tk
from ui.app_ui import AppUI
from logic.database import init_db

if __name__ == "__main__":
    init_db()  # Initialize SQLite database
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()