import re
import subprocess
import tkinter
from datetime import date
import customtkinter
import customtkinter as customTk





class App(customTk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x800")
        self.title("My GUI")

        # --- Frame ---
        self.password_frame = PasswordList(master=self)
        self.password_frame.grid(row=3, column=0, padx=20, pady=20)

        self.password_frame.add_item("Password 1")
        self.password_frame.add_item("Password 2")

        # --- Button ---
        self.button = customTk.CTkButton(self, command=self.button_clicked, text="Submit")
        self.button.grid(row=0, column=6, padx=20, pady=20)

        # --- Label ---
        self.sn_label = customTk.CTkLabel(self, text="Service Number", font=('default', 22, "bold"))
        self.sn_label.grid(row=0, column=0, padx=20, pady=20)

        self.password_label = customTk.CTkLabel(self, text="Password will appear below", font=('default', 16, "bold"))
        self.password_label.grid(row=2, column=0, padx=20, pady=20)

        # --- Entry ---
        self.sn_entry = customTk.CTkEntry(self, placeholder_text="Enter SN Here", font=('default', 18, "bold"))
        self.sn_entry.grid(row=0, column=1, padx=20, pady=20)
        self.sn_entry.bind("<Return>", self.submit_service_tag)


    def button_clicked(self):
        print("Button clicked")
        self.submit_service_tag()

    def submit_service_tag(self, event=None):
        service_number = self.sn_entry.get().upper()
        self.focus()    # changes the focus to main window, removes blinking cursor
        # runs if service number is not blank
        if service_number != "":
            print("SERVICE NUMBER: " + service_number)
            self.password_label.configure(text="Running...")
            self.password_frame.add_item(service_number)

        # runs if service number is blank
        elif service_number == "":
            self.sn_entry.delete(0, "end")
            self.password_label.configure(text="Service Number cannot be blank")

        self.sn_entry.delete(0, "end")


    def run_powershell(self, service_number):
        result = subprocess.run(
            ["PowerShell",
             "-Command",
             f"Get-LapsADPassword -Identity {service_number} -asplaintext"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        output = result.stdout
        #print(output)

        password_match = re.search(r"Password\s*:\s*(\S+)", output)
        expiration_match = re.search(r"ExpirationTimestamp\s*:\s*(\S+)", output)

        if expiration_match:
            expired_string = expiration_match.group(1).split('/')
            expired_date = date(int(expired_string[2]), int(expired_string[0]), int(expired_string[1]))
            expired = (expired_date < date.today())
            print("Today: " + str(date.today()) + " Expiration: " + str(expired_date) + " Expired?: " + str(expired))
        else:
            print("No expiration timestamp")

        if password_match:
            password = password_match.group(1)
            if expired:
                password = password_match.group(1) + f"   |{expired_string}|"
        else:
            password = "NO PASSWORD FOUND"

        print("POWERSHELL DONE")

        # TO:DO create QR Code




class PasswordList(customTk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.items = []
        self.selected = None

    def add_item(self, text):
        btn = customTk.CTkButton(
            self,
            text=text,
            anchor="w",
            command=lambda b=text: self.select_item(b)
        )
        btn.pack(fill="x", padx=5, pady=2)

        self.items.append((text, btn))

    def select_item(self, text):
        self.selected = text

        for t, btn in self.items:
            if t == text:
                btn.configure(fg_color="red")  # selected
            else:
                btn.configure(fg_color=("gray75", "gray25"))

    def delete_selected(self):
        for text, btn in self.items:
            if text == self.selected:
                btn.destroy()
        self.items = [(t, b) for t, b in self.items if t != self.selected]
        self.selected = None




if __name__ == '__main__':
    app = App()
    print(date.today())
    app.run_powershell("5qft9y3")
    app.mainloop()
