import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3
class HabitTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Habit Tracker")
        self.root.geometry("600x500")

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        #polaczenie z sqllite
        try:
            self.conn = sqlite3.connect("habits.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS habits (
                name TEXT PRIMARY KEY,
                dates TEXT
            )""")
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Cant connect to db: {e}")
            return
        self.create_ui()

        #wczytuje dane z bazy
        self.load_habits()

    #tworzy interfejs
    def create_ui(self):

        #pole tekstowe do wpisania nawyku
        tk.Label(self.root, text="Habit Name:").grid(row=0, column=0, padx=5, pady=5, sticky="W")
        self.habit_entry = tk.Entry(self.root)
        self.habit_entry.grid(row=0, column=1, padx=5, pady=5, sticky="EW")

        #dodawanie nowego nawyku
        tk.Button(self.root, text="Add Habit", command=self.add_habit).grid(row=0, column=2, padx=5, pady=5)

        #lista
        tk.Label(self.root, text="Habits:").grid(row=1, column=0, sticky="W", padx=5)
        self.habit_listbox = tk.Listbox(self.root)
        self.habit_listbox.grid(row=2, column=0, columnspan=2, sticky="NSEW", padx=5,
                                pady=5)
        #oznaczenie jako zrobiony
        tk.Button(self.root, text="Mark as Done", command=self.mark_done).grid(row=2, column=2, padx=5, pady=5,
                                                                               sticky="N")
        #pokarz postepy
        tk.Button(self.root, text="Visualize Progress", command=self.visualize_progress).grid(row=3, column=2, padx=5,
                                                                                              pady=5, sticky="E")
        #usun nawyk
        tk.Button(self.root, text="Delete Habit", command=self.delete_habit).grid(row=3, column=0, padx=5, pady=5,
                                                                                  sticky="W")
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    #usuwanie nawyku z bazy
    def delete_habit(self):
        selected = self.habit_listbox.curselection()
        if selected:
            habit = self.habit_listbox.get(selected)
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this '{habit}'")
            if confirm:
                try:
                    #usuwa z bazy
                    self.cursor.execute("DELETE FROM habits WHERE name = ?", (habit,))
                    self.conn.commit()
                    #usuwa z listy
                    self.habit_listbox.delete(selected)
                    messagebox.showinfo("Success", f"Habit '{habit}' has been deleted")
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Cant delete: {e}")
        else:
            messagebox.showerror("Error", "No habit selected")

    #wczytuje nawyki z bazy i wyswietla je w liscie
    def load_habits(self):
        try:
            self.habit_listbox.delete(0, tk.END)
            self.cursor.execute("SELECT name FROM habits")
            habits = self.cursor.fetchall()
            for habit in habits:
                self.habit_listbox.insert(tk.END, habit[0])
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Cant load habits: {e}")

    #dodawanie nowego nawyku
    def add_habit(self):

        habit = self.habit_entry.get().strip()
        if habit:
            try:
                self.cursor.execute("INSERT INTO habits (name, dates) VALUES (?, ?)", (habit, ""))
                self.conn.commit()
                self.habit_listbox.insert(tk.END, habit)
                self.habit_entry.delete(0, tk.END)
                messagebox.showinfo("Success", f"Habit '{habit}' added")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Habit already exists")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Cant add: {e}")
        else:
            messagebox.showerror("Error", "Habit name cant be empty")

    #oznaczenie jako gotowy
    def mark_done(self):
        selected = self.habit_listbox.curselection()
        if selected:
            habit = self.habit_listbox.get(selected)
            today = datetime.now().strftime("%Y-%m-%d")
            try:
                self.cursor.execute("SELECT dates FROM habits WHERE name = ?", (habit,))
                result = self.cursor.fetchone()
                dates = result[0].split(",") if result[0] else []

                if today not in dates:
                    dates.append(today)
                    self.cursor.execute("UPDATE habits SET dates = ? WHERE name = ?", (",".join(dates), habit))
                    self.conn.commit()
                    messagebox.showinfo("Success", f"Marked '{habit}' as done")
                else:
                    messagebox.showerror("Error", f"'{habit}' is already marked")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Cant mark: {e}")
        else:
            messagebox.showerror("Error", "Nothing is selected")

    #pokazanie postepow
    def visualize_progress(self):
        selected = self.habit_listbox.curselection()
        if selected:
            habit = self.habit_listbox.get(selected)
            try:
                self.cursor.execute("SELECT dates FROM habits WHERE name = ?", (habit,))
                result = self.cursor.fetchone()
                dates = result[0].split(",") if result[0] else []

                if dates:

                    days = sorted([datetime.strptime(date, "%Y-%m-%d") for date in dates])

                    plt.figure(figsize=(8, 4))
                    plt.scatter(days, ["DONE"] * len(days), label=habit, color="green", marker='o')


                    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%Y-%m-%d"))
                    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.DayLocator())

                    plt.xlabel("Date")
                    plt.title(f"Progress for '{habit}'")
                    plt.yticks(["DONE"])
                    plt.grid(axis="x", linestyle="--", alpha=0.6)
                    plt.legend()
                    plt.gcf().autofmt_xdate()
                    plt.show()
                else:
                    messagebox.showinfo("Info", f"No progress recorded for '{habit}'.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"visualization error: {e}")
        else:
            messagebox.showerror("Error", "No habit selected.")
