import tkinter as tk
import subprocess
import re
import os
from os.path import join

root = tk.Tk()

# setting the windows size
root.geometry("600x400")

# gets the userprofile name, ex: cdove
os.environ["USERPROFILE"]
# sets the file_path to the users desktop
desktop = os.path.join(os.environ["USERPROFILE"], "OneDrive - Michels Corporation", "Desktop")
file_path = os.path.join(desktop, "LAPSHistory.txt")

# declaring string variable
# for storing service tag and password
service_tag = tk.StringVar()
st_password = tk.StringVar()
password_display = tk.StringVar()
password_display.set("Password will appear here")


# defining a function that will
# get the name and password and
# print them on the screen
def submit():
    st = service_tag.get()

    print("The service tag is : " + st)

    result = subprocess.run(
		["powershell",
		"-Command",
		f"Get-LapsADPassword -Identity {st} -AsPlainText"],
		capture_output=True,
		text=True
    )
    output = result.stdout
    match = re.search(r"Password\s*:\s*(\S+)", output)
    st_password = "ERROR"

    if match:
        st_password = match.group(1)
        print("The password is : " + st_password)
        password_display.set(st_password)
    else:
        print("Password not found.")
        password_display.set("Password not found.")
    try:
        print(file_path)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{st}, {st_password}\n")
    except:
        print('File not found.')

    load_history()

    service_tag.set("")

def load_history():
    try:
        print(file_path)
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

password_label = tk.Label(root, textvariable=password_display, font=('calibre', 10, 'bold'))
password_label.grid(row=3, column=1)

# creating a button using the widget
# Button that will call the submit function
sub_btn = tk.Button(root, text='Submit', command=submit)

history_box = tk.Listbox(root, height=10, width=50)
history_box.grid(row=4, column=0, columnspan=2)

scrollbar = tk.Scrollbar(root, command=history_box.yview)
history_box.config(yscrollcommand=scrollbar.set)

scrollbar.grid(row=4, column=2, sticky='ns')

# placing the label and entry in
# the required position using grid
# method
service_tag_label.grid(row=0, column=0)
service_tag_entry.grid(row=0, column=1)
sub_btn.grid(row=2, column=1)

load_history()
# performing an infinite loop
# for the window to display
root.mainloop()