import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import time
import datetime

program_start_time = time.time()

LOG_FILE = "work_log.csv"
ONDECLARABEL_LOG_FILE = "ondeclarabel_log.csv"

# Ensure CSV files exist
for file_name in [LOG_FILE, ONDECLARABEL_LOG_FILE]:
    if not os.path.exists(file_name):
        with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Project", "Start Time", "End Time", "Duration (mins)"])  # CSV Headers

# Store active sessions
active_sessions = {}
ondeclarabel_sessions = {}

def start_stop_tracking(is_ondeclarabel=False):
    """Start or stop tracking for declarabel or ondeclarabel projects. Only one can run at a time."""
    project = project_dropdown.get().strip()
    if not project:
        messagebox.showwarning("Warning", "Please enter a project name.")
        return

    global active_sessions, ondeclarabel_sessions

    # If another session is running, stop it first
    if active_sessions and is_ondeclarabel:
        stop_tracking(False)  # Stop declarabel if switching to ondeclarabel
    elif ondeclarabel_sessions and not is_ondeclarabel:
        stop_tracking(True)  # Stop ondeclarabel if switching to declarabel

    session_dict = ondeclarabel_sessions if is_ondeclarabel else active_sessions

    if project in session_dict:
        stop_tracking(is_ondeclarabel)
    else:
        # Start tracking
        session_dict[project] = time.time()
        update_running_label(project, is_ondeclarabel)
        messagebox.showinfo("Started", f"Tracking started for: {project} (Ondeclarabel: {is_ondeclarabel})")

def stop_tracking(is_ondeclarabel):
    """Stops tracking for the active session and logs time."""
    session_dict = ondeclarabel_sessions if is_ondeclarabel else active_sessions
    log_file = ONDECLARABEL_LOG_FILE if is_ondeclarabel else LOG_FILE

    if not session_dict:
        return  # No active session to stop

    project, start_time = session_dict.popitem()
    end_time = time.time()
    duration_mins = round((end_time - start_time) / 60, 2)

    # Log the time to the appropriate file
    with open(log_file, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.date.today(), project, time.strftime("%H:%M:%S", time.localtime(start_time)),
                         time.strftime("%H:%M:%S", time.localtime(end_time)), duration_mins])

    update_project_list()
    update_running_label(None)  # No active project
    messagebox.showinfo("Stopped", f"Logged {duration_mins} mins for '{project}' (Ondeclarabel: {is_ondeclarabel}).")

    # After stopping, update the table and the aggregated data
    load_data()  # Refresh the tables with the latest data
    display_aggregated_data()  # Update the aggregated data in the overviews


def update_running_label(project=None, is_ondeclarabel=False):
    """Updates the single label to show the currently running project."""
    if project:
        running_label.config(text=f"Running project: {project} ({'Ondeclarabel' if is_ondeclarabel else 'Declarabel'})")
    else:
        running_label.config(text="No active project")

def adjust_column_width(tree):
    """Adjust column width based on max character length in each column."""
    for col in tree["columns"]:
        max_width = max(len(col), 10)  # Start with column header width
        for item in tree.get_children():
            cell_value = tree.item(item, "values")[tree["columns"].index(col)]
            max_width = max(max_width, len(str(cell_value)))
        tree.column(col, width=max_width * 8)  # Approximate character width

def load_data():
    """Load work log from CSV and display past week's data, adjusting column widths dynamically."""
    def populate_table(tree, file_name):
        tree.delete(*tree.get_children())  # Clear table
        if not os.path.exists(file_name):
            return

        last_week = datetime.date.today() - datetime.timedelta(days=7)

        with open(file_name, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip headers
            for row in reader:
                date_str, project, start, end, duration = row
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                if date_obj >= last_week:
                    tree.insert("", "end", values=(date_str, project, start, end, f"{int(float(duration))} mins"))

        adjust_column_width(tree)  # Adjust column widths dynamically

    populate_table(tree, LOG_FILE)  # Load main work log
    populate_table(ondeclarabel_tree, ONDECLARABEL_LOG_FILE)  # Load ondeclarabel log
    display_aggregated_data()  # Display aggregated data below each tree

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

def display_aggregated_data():
    """Display the aggregated total time for each project, grouped by day and project, under the respective log tables."""
    def get_aggregated_data(file_name):
        """Return aggregated data grouped by day and project for the last 7 days."""
        aggregated_data = {}

        with open(file_name, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            last_week = datetime.date.today() - datetime.timedelta(days=7)

            for row in reader:
                date_str, project, start, end, duration = row
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

                if date_obj >= last_week:
                    if date_obj not in aggregated_data:
                        aggregated_data[date_obj] = {}

                    if project not in aggregated_data[date_obj]:
                        aggregated_data[date_obj][project] = 0

                    aggregated_data[date_obj][project] += float(duration)

        return aggregated_data

    # Clear previous aggregated data labels
    for widget in aggregated_data_frame_declarabel.winfo_children():
        widget.destroy()
    for widget in aggregated_data_frame_ondeclarabel.winfo_children():
        widget.destroy()

    # Get aggregated data for both logs
    declarabel_aggregated = get_aggregated_data(LOG_FILE)
    ondeclarabel_aggregated = get_aggregated_data(ONDECLARABEL_LOG_FILE)

    # Display aggregated data for Declarabel projects
    for date_obj in sorted(declarabel_aggregated.keys()):
        date_label = tk.Label(aggregated_data_frame_declarabel, text=f"{date_obj}:")
        date_label.pack(anchor="w")
        for project, total_time in declarabel_aggregated[date_obj].items():
            project_label = tk.Label(aggregated_data_frame_declarabel, text=f"  {project}: {round(total_time, 2)} mins")
            project_label.pack(anchor="w")

    # Display aggregated data for Ondeclarabel projects
    for date_obj in sorted(ondeclarabel_aggregated.keys()):
        date_label = tk.Label(aggregated_data_frame_ondeclarabel, text=f"{date_obj}:")
        date_label.pack(anchor="w")
        for project, total_time in ondeclarabel_aggregated[date_obj].items():
            project_label = tk.Label(aggregated_data_frame_ondeclarabel, text=f"  {project}: {round(total_time, 2)} mins")
            project_label.pack(anchor="w")

def stop_werkdag():
    """Stops the workday and calculates total work time, declarabel time, and ondeclarabel time."""
    end_time = time.time()
    workday_duration = round((end_time - program_start_time) / 3600, 2)  # Convert to hours

    # Get total declarabel and ondeclarabel hours
    declarabel_time = sum_total_time(LOG_FILE)
    ondeclarabel_time = sum_total_time(ONDECLARABEL_LOG_FILE)

    # Display summary
    summary_text = f"Workday: {workday_duration} hrs | Declarabel: {declarabel_time} hrs | Ondeclarabel: {ondeclarabel_time} hrs"

    # Update UI
    workday_summary_label.config(text=summary_text)

    messagebox.showinfo("Workday Summary", summary_text)

def sum_total_time(file_name):
    """Summarizes total time in hours from the given log file for today."""
    if not os.path.exists(file_name):
        return 0

    total_time = 0
    today_str = str(datetime.date.today())

    with open(file_name, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip headers
        for row in reader:
            date_str, _, _, _, duration = row
            if date_str == today_str:
                total_time += float(duration)

    return round(total_time / 60, 2)  # Convert minutes to hours


# === GUI SETUP ===
root = tk.Tk()
root.title("Time Slug")
root.geometry("1000x600")

# Project Entry with Dropdown
project_dropdown = ttk.Combobox(root)
# project_dropdown.grid(row=0, column=0, columnspan=1, padx=10, pady=5, sticky="ew")
update_project_list()

# Row 0: Projectnaam selectie
projectnaam_label = tk.Label(root, text=f"1. Selecteer bestaand project of geef nieuwe projectnaam op.")
projectnaam_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

# Row 1:

start_stop_button = ttk.Button(root, text="Start/Stop Timer", command=lambda: start_stop_tracking(False))
start_stop_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

ondeclarabel_button = ttk.Button(root, text="Start/Stop Ondeclarabel", command=lambda: start_stop_tracking(True))
ondeclarabel_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")


# Work Log Table (Treeview)
tree = ttk.Treeview(root, columns=("Date", "Project", "Start", "End", "Duration"), show="headings")
tree.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

ondeclarabel_tree = ttk.Treeview(root, columns=("Date", "Project", "Start", "End", "Duration"), show="headings")
ondeclarabel_tree.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")

for col in tree["columns"]:
    tree.heading(col, text=col)

for col in ondeclarabel_tree["columns"]:
    ondeclarabel_tree.heading(col, text=col)

# Running project label (Single label for both types)
running_label = tk.Label(root, text="No active project", justify="left")
running_label.grid(row=0, column=1, columnspan=1, padx=10, pady=10)

# Big Labels for Aggregated Data
declarabel_label = tk.Label(root, text="Declarabel", font=("Arial", 16, "bold"))
declarabel_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")

ondeclarabel_label = tk.Label(root, text="Ondeclarabel", font=("Arial", 16, "bold"))
ondeclarabel_label.grid(row=5, column=1, padx=10, pady=10, sticky="w")

# Aggregated data frames for Declarabel and Ondeclarabel
aggregated_data_frame_declarabel = tk.Frame(root)
aggregated_data_frame_declarabel.grid(row=6, column=0, padx=10, pady=5, sticky="nw")

aggregated_data_frame_ondeclarabel = tk.Frame(root)
aggregated_data_frame_ondeclarabel.grid(row=6, column=1, padx=10, pady=5, sticky="nw")

# Label to display program start time
program_start_label = tk.Label(root, text=f"Program started at: {time.strftime('%H:%M:%S', time.localtime(program_start_time))}")
program_start_label.grid(row=7, column=0, padx=10, pady=10, sticky="w")

# # Button to stop workday
# stop_werkdag_button = ttk.Button(root, text="Stop Werkdag", command=stop_werkdag)
# stop_werkdag_button.grid(row=7, column=1, padx=10, pady=10, sticky="w")

# # Workday Summary Label
# workday_summary_label = tk.Label(root, text="Workday: -- hrs | Declarabel: -- hrs | Ondeclarabel: -- hrs", font=("Arial", 12, "bold"))
# workday_summary_label.grid(row=7, column=3, padx=10, pady=10, sticky="w")

# === Werkdag ===
# werkdag_frame = ttk.LabelFrame(root, text="Je werkdag", padding=10)
# werkdag_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

# projectnaam_label = tk.Label(werkdag_frame, text="1. Selecteer bestaand project of geef nieuwe projectnaam op.")
# projectnaam_label.pack(anchor="w", padx=5, pady=5)

# project_dropdown = ttk.Combobox(werkdag_frame)
# project_dropdown.pack(fill="x", padx=5, pady=5)

# === Timer Controls Box ===
timer_frame = ttk.LabelFrame(root, text="Timer Controls", padding=10)
timer_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

start_stop_button = ttk.Button(timer_frame, text="Start/Stop Timer")
start_stop_button.pack(side="left", padx=5, pady=5)

ondeclarabel_button = ttk.Button(timer_frame, text="Start/Stop Ondeclarabel")
ondeclarabel_button.pack(side="left", padx=5, pady=5)

# === Running Project Box ===
running_frame = ttk.LabelFrame(root, text="Current Status", padding=10)
running_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

running_label = tk.Label(running_frame, text="No active project")
running_label.pack(anchor="w")

# === Work Log Tables ===
tables_frame = ttk.LabelFrame(root, text="Work Logs", padding=10)
tables_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

tree = ttk.Treeview(tables_frame, columns=("Date", "Project", "Start", "End", "Duration"), show="headings")
tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

ondeclarabel_tree = ttk.Treeview(tables_frame, columns=("Date", "Project", "Start", "End", "Duration"), show="headings")
ondeclarabel_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

# === Aggregated Data Box ===
aggregated_frame = ttk.LabelFrame(root, text="Aggregated Work Data", padding=10)
aggregated_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

declarabel_label = tk.Label(aggregated_frame, text="Declarabel", font=("Arial", 16, "bold"))
declarabel_label.pack(anchor="w", padx=5, pady=5)

aggregated_data_frame_declarabel = tk.Frame(aggregated_frame)
aggregated_data_frame_declarabel.pack(anchor="w", padx=5, pady=5)

ondeclarabel_label = tk.Label(aggregated_frame, text="Ondeclarabel", font=("Arial", 16, "bold"))
ondeclarabel_label.pack(anchor="w", padx=5, pady=5)

aggregated_data_frame_ondeclarabel = tk.Frame(aggregated_frame)
aggregated_data_frame_ondeclarabel.pack(anchor="w", padx=5, pady=5)

# === Workday Summary Box ===
summary_frame = ttk.LabelFrame(root, text="Workday Summary", padding=10)
summary_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

program_start_label = tk.Label(summary_frame, text=f"Programma gestart om: {time.strftime('%H:%M:%S', time.localtime(program_start_time))}")
program_start_label.pack(anchor="w", padx=5, pady=5)

# Configure grid weights to allow expansion
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(3, weight=1)

root.mainloop()

# Grid configurations
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(3, weight=1)




root.mainloop()
