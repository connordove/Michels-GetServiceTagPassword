import os
import re
import subprocess
import threading
import ctypes
import tkinter as tk
from ctypes import wintypes
from tkinter import messagebox

root = tk.Tk()

# setting the windows size
root.geometry("600x400")

# gets the userprofile name, ex: cdove
# sets the file_path to the users desktop, prints path in terminal
desktop = os.path.join(os.environ["USERPROFILE"], "OneDrive - Michels Corporation", "Desktop")
file_path = os.path.join(desktop, "LAPSHistory.txt")
print("History File Path is : " + file_path)

# declaring string variable
# for storing service tag and password
service_tag = tk.StringVar()
st_password = tk.StringVar()
password_display = tk.StringVar()
# sets password_display label to display following text
password_display.set("Password will appear here")

# defining a function that will
# run powershell command
# sort for password from output
# updates GUI and trys writing to a file
def run_powershell(st):
    result = subprocess.run(
        ["powershell",
         "-Command",
         f"Get-LapsADPassword -Identity {st} -AsPlainText"],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    output = result.stdout

    match = re.search(r"Password\s*:\s*(\S+)", output)

    if match:
        pwd = match.group(1)
    else:
        pwd = "ERROR"
        st_local = "INVALID"
        st = st_local

    # Update GUI safely
    root.after(0, lambda: password_display.set("SN, Password"))

    # Write to file
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{st}, {pwd}\n")
    except Exception as e:
        print("File write error:", e)

    # Refresh history safely
    root.after(0, load_history)


# defining a function that will
# get the name and password and
# print them on the screen
# save the name and password to file
def submit(event=None):
    st = service_tag.get()

    if st == "":
        print("Service Number not found.")
        return

    print("The service number is : " + st)

    password_display.set("Running...")

    threading.Thread(target=run_powershell, args=(st,), daemon=True).start()

    service_tag.set("")


# defining a function that will
# load name and passwords from
# the given file path and display in
# history_box Listbox
def load_history():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        recent = lines[-100:]

        history_box.delete(0, tk.END)

        for line in recent:
            history_box.insert(tk.END, line.strip())

        history_box.see(tk.END)

    except FileNotFoundError:
        history_box.insert(tk.END, "No history file found.")

def delete_history():
    confirm_delete_box = tk.messagebox.askyesno("Delete History",
                                                "Are you sure you want to delete password History?")

    if confirm_delete_box:
        print("Deleting history file.")
        history_box.delete(0, tk.END)
        if os.path.exists(file_path):
            os.remove(file_path)
            # Force Windows Explorer refresh
            HWND_BROADCAST = 0xFFFF
            WM_COMMAND = 0x0111
            REFRESH = 41504

            ctypes.windll.user32.PostMessageW(
                HWND_BROADCAST, WM_COMMAND, REFRESH, 0
            )

            print("File deleted and desktop refreshed successfully.")
        else:
            print("No history file found.")
    else:
        print("Chose not to delete history.")
        return


# creating a label for
# name using widget Label
service_tag_label = tk.Label(root, text='Service Number', font=('calibre', 10, 'bold'))

# creating an entry for input
# name using widget Entry
service_tag_entry = tk.Entry(root, textvariable=service_tag, font=('calibre', 10, 'normal'))

# allows the user to press enter to run submit function
service_tag_entry.bind("<Return>", submit)

# creating a label for password
password_label = tk.Label(root, textvariable=password_display, font=('calibre', 10, 'bold'))

# creating a button using the widget
# Button that will call the submit function
sub_btn = tk.Button(root, text='Submit', command=submit)

delete_btn = tk.Button(root, text='Delete History', command=delete_history)

# creating a listbox to display service tag and password history
history_box = tk.Listbox(root, height=10, width=50, font=('calibre', 10, 'bold'))

# creating a scroll bar to view large amounts of st and password history
scrollbar = tk.Scrollbar(root, command=history_box.yview)
history_box.config(yscrollcommand=scrollbar.set)

# placing the label and entry in
# the required position using grid
# method
service_tag_label.grid(row=0, column=0)
service_tag_entry.grid(row=0, column=1)
sub_btn.grid(row=2, column=1)
delete_btn.grid(row=2, column=2)
password_label.grid(row=4, column=0)
history_box.grid(row=5, column=0, columnspan=2)
scrollbar.grid(row=5, column=2, sticky='ns')


# loads the history
load_history()
# performing an infinite loop
# for the window to display
root.mainloop()