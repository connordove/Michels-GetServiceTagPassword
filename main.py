import os
import re
import subprocess
import threading
import tkinter as tk

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

def run_powershell(st):
    result = subprocess.run(
        ["powershell",
         "-Command",
         f"Get-LapsADPassword -Identity {st} -AsPlainText"],
        capture_output=True,
        text=True
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
    root.after(0, lambda: password_display.set(pwd))

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
        print("Service Tag not found.")
        return

    print("The service tag is : " + st)

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

        recent = lines[-10:]

        history_box.delete(0, tk.END)

        for line in recent:
            history_box.insert(tk.END, line.strip())

    except FileNotFoundError:
        history_box.insert(tk.END, "No history file found.")

# creating a label for
# name using widget Label
service_tag_label = tk.Label(root, text='Service Tag', font=('calibre', 10, 'bold'))

# creating an entry for input
# name using widget Entry
service_tag_entry = tk.Entry(root, textvariable=service_tag, font=('calibre', 10, 'normal'))

# allows the user to press enter to run submit function
service_tag_entry.bind("<Return>", submit)

# creating a label for password
password_label = tk.Label(root, textvariable=password_display, font=('calibre', 10, 'bold'))
password_label.grid(row=4, column=0)

# creating a button using the widget
# Button that will call the submit function
sub_btn = tk.Button(root, text='Submit', command=submit)

# creating a listbox to display service tag and password history
history_box = tk.Listbox(root, height=10, width=50, font=('calibre', 10, 'bold'))
history_box.grid(row=5, column=0, columnspan=2)

# creating a scroll bar to view large amounts of st and password history
scrollbar = tk.Scrollbar(root, command=history_box.yview)
history_box.config(yscrollcommand=scrollbar.set)
scrollbar.grid(row=5, column=2, sticky='ns')

# placing the label and entry in
# the required position using grid
# method
service_tag_label.grid(row=0, column=0)
service_tag_entry.grid(row=0, column=1)
sub_btn.grid(row=2, column=1)

# loads the history
load_history()
# performing an infinite loop
# for the window to display
root.mainloop()