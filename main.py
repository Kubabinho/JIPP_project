import tkinter as tk
from habit_tracker import HabitTracker

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTracker(root)
    root.mainloop()