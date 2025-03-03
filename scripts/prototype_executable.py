"""Script to test if I can make an executable that can be run from another PC."""

import tkinter as tk

def on_button_click():
    label.config(text="Hello, Tkinter!")

# Create the main window
root = tk.Tk()
root.title("Simple Tkinter App")
root.geometry("300x200")  # Set window size

# Create a label
label = tk.Label(root, text="Click the button!", font=("Arial", 14))
label.pack(pady=20)

# Create a button
button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack()

# Run the Tkinter event loop
root.mainloop()
