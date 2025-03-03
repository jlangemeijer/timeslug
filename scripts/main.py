import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import time
import datetime

LOG_FILE = "work_log.csv"

# Ensure CSV file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Project", "Start Time", "End Time", "Duration (mins)"])  # CSV Headers

# Store active sessions
active_sessions = {}

def start_tracking():
    """Start tracking time for a selected project."""
    project = project_entry.get().strip()
    if not project:
        messagebox.showwarning("Warning", "Please enter a project name.")
        return

    if project in active_sessions:
        messagebox.showwarning("Warning", f"Already tracking '{project}'!")
        return

    active_sessions[project] = time.time()
    messagebox.showinfo("Started", f"Tracking started for: {project}")

def stop_tracking():
    """Stop tracking time and save log."""
    project = project_entry.get().strip()
    if project not in active_sessions:
        messagebox.showwarning("Warning", "No active tracking for this project.")
        return

    start_time = active_sessions.pop(project)
    end_time = time.time()
    duration_mins = round((end_time - start_time) / 60, 2)

    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.date.today(), project, time.strftime("%H:%M:%S", time.localtime(start_time)),
                         time.strftime("%H:%M:%S", time.localtime(end_time)), duration_mins])

    messagebox.showinfo("Stopped", f"Logged {duration_mins} mins for '{project}'.")

    update_project_list()

def load_data():
    """Load work log from CSV and display past week's data."""
    tree.delete(*tree.get_children())  # Clear table
    if not os.path.exists(LOG_FILE):
        return

    project_totals = {}  # Store total minutes per project
    last_week = datetime.date.today() - datetime.timedelta(days=7)

    with open(LOG_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip headers
        for row in reader:
            date_str, project, start, end, duration = row
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

            if date_obj >= last_week:  # Show only the last week's data
                tree.insert("", "end", values=(date_str, project, start, end, f"{int(float(duration))} mins"))

            if project in project_totals:
                project_totals[project] += float(duration)
            else:
                project_totals[project] = float(duration)

    # Show summary of total hours per project
    summary_text = "Project Totals (Last 7 Days):\n"
    for project, total_mins in project_totals.items():
        summary_text += f"{project}: {round(total_mins / 60, 2)} hours ({int(total_mins)} mins)\n"

    summary_label.config(text=summary_text)

def update_project_list():
    """Update the project dropdown and autocomplete suggestions."""
    projects = set()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                projects.add(row[1])  # Collect project names

    project_dropdown["values"] = list(projects)

# === GUI SETUP ===
root = tk.Tk()
root.title("Work Time Logger")
root.geometry("500x400")

# Project Entry with Dropdown
project_entry = ttk.Entry(root)
project_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
project_dropdown = ttk.Combobox(root)
project_dropdown.grid(row=0, column=1, padx=10, pady=10)
update_project_list()  # Populate with past projects

# Buttons
start_button = ttk.Button(root, text="Start", command=start_tracking)
start_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

stop_button = ttk.Button(root, text="Stop", command=stop_tracking)
stop_button.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

overview_button = ttk.Button(root, text="Show Overview", command=load_data)
overview_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

# Work Log Table (Treeview)
tree = ttk.Treeview(root, columns=("Date", "Project", "Start", "End", "Duration"), show="headings")
tree.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

for col in tree["columns"]:
    tree.heading(col, text=col)

# Summary Label
summary_label = tk.Label(root, text="Project Totals (Last 7 Days):", justify="left")
summary_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(3, weight=1)

root.mainloop()
